"""
Views for User app - Auth and Profile endpoints.
"""
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken

from apps.users.models import User
from apps.users.serializers import (
    DeactivationStatusSerializer,
    LoginSerializer,
    LogoutSerializer,
    UserDeactivationSerializer,
    UserSerializer,
    UserProfileSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
)
from apps.users.services import DeactivationService
from apps.users.tasks import send_password_reset_email, send_password_changed_notification


class LoginView(APIView):
    """
    POST /api/v1/auth/login/

    Authenticate user and return JWT tokens.
    """
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})

        if not serializer.is_valid():
            return Response(
                {'detail': 'Invalid credentials or missing fields.'},
                status=status.HTTP_400_BAD_REQUEST
                if 'email' not in request.data or 'password' not in request.data
                else status.HTTP_401_UNAUTHORIZED
            )

        user = serializer.validated_data['user']

        # Update last login
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])

        # Generate tokens
        refresh = RefreshToken.for_user(user)

        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data,
        })


class LogoutView(APIView):
    """
    POST /api/v1/auth/logout/

    Blacklist refresh token to logout user.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = LogoutSerializer

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {'detail': 'Refresh token is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer.save()
        return Response({'detail': 'Successfully logged out.'})


class CustomTokenRefreshView(TokenRefreshView):
    """
    POST /api/v1/auth/refresh/

    Refresh access token using refresh token.
    Rotation enabled - returns new refresh token.
    """

    def post(self, request, *args, **kwargs):
        if 'refresh' not in request.data:
            return Response(
                {'detail': 'Refresh token is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            return super().post(request, *args, **kwargs)
        except (TokenError, InvalidToken):
            return Response(
                {'detail': 'Invalid or expired token.'},
                status=status.HTTP_401_UNAUTHORIZED
            )


class UserProfileView(RetrieveUpdateAPIView):
    """
    GET /api/v1/users/me/ - Get current user profile
    PUT /api/v1/users/me/ - Update current user profile
    PATCH /api/v1/users/me/ - Partial update current user profile
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user


class PasswordResetRequestView(APIView):
    """
    POST /api/v1/auth/password/reset/

    Request password reset email.
    Always returns 200 to prevent email enumeration.
    """
    permission_classes = [AllowAny]
    serializer_class = PasswordResetRequestSerializer

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {'detail': 'Email is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email=email, is_active=True)
            send_password_reset_email.delay(user.id)
        except User.DoesNotExist:
            pass  # Don't reveal if email exists

        return Response({
            'detail': 'If an account exists with this email, a reset link has been sent.'
        })


class PasswordResetConfirmView(APIView):
    """
    POST /api/v1/auth/password/reset/confirm/

    Confirm password reset with token and new password.
    """
    permission_classes = [AllowAny]
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()

        # Send notification if enabled
        if user.security_notifications_enabled:
            send_password_changed_notification.delay(user.id)

        return Response({'detail': 'Password has been reset successfully.'})


class UserDeactivationView(APIView):
    """
    POST /api/v1/users/:id/deactivate/

    Deactivate a user account with data export.
    Admin only.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        if not request.user.is_admin:
            return Response(
                {'detail': 'Only admins can deactivate users.'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            target_user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response(
                {'detail': 'User not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if target_user.id == request.user.id:
            return Response(
                {'detail': 'Cannot deactivate your own account.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = UserDeactivationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        reason = serializer.validated_data['reason']
        force = serializer.validated_data.get('force', False)

        try:
            audit = DeactivationService.execute_deactivation(
                user=target_user,
                admin=request.user,
                reason=reason,
                force=force,
            )
        except ValueError as e:
            return Response(
                {
                    'detail': str(e),
                    'pending_timesheets_count': DeactivationService.get_pending_timesheets_count(target_user),
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        export_data = audit.export_data
        export_summary = {
            'time_entries_count': len(export_data.get('time_entries', [])),
            'timesheets_count': len(export_data.get('timesheets', [])),
            'has_csv_blob': bool(export_data.get('csv_blob')),
        }

        return Response({
            'success': True,
            'message': f'User {target_user.email} has been deactivated.',
            'export_summary': export_summary,
        })


class UserDeactivationStatusView(APIView):
    """
    GET /api/v1/users/:id/deactivation-status/

    Check if a user can be deactivated.
    Admin only.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        if not request.user.is_admin:
            return Response(
                {'detail': 'Only admins can check deactivation status.'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            target_user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response(
                {'detail': 'User not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        pending_count = DeactivationService.get_pending_timesheets_count(target_user)

        return Response({
            'can_deactivate': pending_count == 0,
            'pending_timesheets_count': pending_count,
            'user_id': target_user.id,
        })
