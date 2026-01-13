"""
Serializers for User app.
"""
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from apps.users.models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model - basic info."""

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'role',
            'timezone',
            'workflow_notifications_enabled',
            'security_notifications_enabled',
        ]
        read_only_fields = ['id', 'email', 'role']


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile updates."""

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'role',
            'timezone',
            'workflow_notifications_enabled',
            'security_notifications_enabled',
            'company',
            'manager',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'email', 'role', 'company', 'manager', 'created_at', 'updated_at']


class LoginSerializer(serializers.Serializer):
    """Serializer for login endpoint."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password,
        )

        if not user:
            raise serializers.ValidationError(
                'Unable to log in with provided credentials.',
                code='authorization'
            )

        if not user.is_active:
            raise serializers.ValidationError(
                'User account is disabled.',
                code='authorization'
            )

        attrs['user'] = user
        return attrs


class LoginResponseSerializer(serializers.Serializer):
    """Serializer for login response."""

    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserSerializer()


class LogoutSerializer(serializers.Serializer):
    """Serializer for logout endpoint."""

    refresh = serializers.CharField()

    def validate_refresh(self, value):
        try:
            self.token = RefreshToken(value)
        except TokenError:
            raise serializers.ValidationError('Invalid or expired token.')
        return value

    def save(self):
        self.token.blacklist()


class TokenRefreshSerializer(serializers.Serializer):
    """Serializer for token refresh - delegates to simplejwt."""

    refresh = serializers.CharField()

    def validate(self, attrs):
        try:
            refresh = RefreshToken(attrs['refresh'])
            data = {'access': str(refresh.access_token)}

            # Rotate refresh token
            refresh.set_jti()
            refresh.set_exp()
            refresh.set_iat()

            data['refresh'] = str(refresh)

            # Blacklist old token
            RefreshToken(attrs['refresh']).blacklist()

            return data
        except TokenError as e:
            raise serializers.ValidationError(str(e))


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for password reset request."""

    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for password reset confirmation."""

    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({
                'confirm_password': 'Passwords do not match.'
            })

        try:
            uid = force_str(urlsafe_base64_decode(attrs['uid']))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError({
                'uid': 'Invalid user identifier.'
            })

        if not default_token_generator.check_token(user, attrs['token']):
            raise serializers.ValidationError({
                'token': 'Invalid or expired token.'
            })

        attrs['user'] = user
        return attrs

    def save(self):
        user = self.validated_data['user']
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class UserDeactivationSerializer(serializers.Serializer):
    """Serializer for user deactivation request."""

    reason = serializers.CharField()
    force = serializers.BooleanField(default=False)

    def validate_reason(self, value):
        if not value.strip():
            raise serializers.ValidationError('Deactivation reason is required.')
        return value


class DeactivationStatusSerializer(serializers.Serializer):
    """Serializer for deactivation status response."""

    can_deactivate = serializers.BooleanField()
    pending_timesheets_count = serializers.IntegerField()
    user_id = serializers.IntegerField()


class DeactivationResponseSerializer(serializers.Serializer):
    """Serializer for deactivation response."""

    success = serializers.BooleanField()
    message = serializers.CharField()
    export_summary = serializers.DictField()
