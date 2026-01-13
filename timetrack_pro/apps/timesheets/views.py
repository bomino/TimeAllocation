"""
Views for Timesheet API.
"""
from datetime import date

from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.timesheets.models import AdminOverride, ApprovalDelegation, OOOPeriod, Timesheet, TimesheetComment
from apps.timesheets.serializers import (
    AdminOverrideSerializer,
    ApprovalDelegationCreateSerializer,
    ApprovalDelegationSerializer,
    OOOPeriodSerializer,
    TimesheetApproveSerializer,
    TimesheetCommentCreateSerializer,
    TimesheetCommentSerializer,
    TimesheetDetailSerializer,
    TimesheetListSerializer,
    TimesheetRejectSerializer,
    TimesheetSubmitSerializer,
    TimesheetUnlockSerializer,
)
from apps.timesheets.services import DelegationService, OOOService
from core.pagination import StandardPagination


class IsManagerPermission:
    """Check if user is a manager."""

    def has_permission(self, request, view):
        return request.user.is_manager


class IsAdminPermission:
    """Check if user is an admin."""

    def has_permission(self, request, view):
        return request.user.is_admin


class TimesheetViewSet(viewsets.ModelViewSet):
    """ViewSet for Timesheet CRUD and workflow operations."""

    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination

    def get_serializer_class(self):
        if self.action == 'list':
            return TimesheetListSerializer
        return TimesheetDetailSerializer

    def get_queryset(self):
        user = self.request.user
        view_param = self.request.query_params.get('view')
        status_filter = self.request.query_params.get('status')

        if view_param == 'team' and user.is_manager:
            queryset = Timesheet.objects.filter(
                Q(user=user) | Q(user__manager=user)
            )
        else:
            queryset = Timesheet.objects.filter(user=user)

        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset.select_related('user', 'approved_by')

    def _can_access_timesheet(self, user, timesheet):
        """Check if user can access this timesheet."""
        if timesheet.user == user:
            return True
        if user.is_manager and timesheet.user.manager == user:
            return True
        if user.is_admin:
            return True
        return False

    def _can_manage_timesheet(self, user, timesheet):
        """Check if user can approve/reject this timesheet."""
        if user.is_admin:
            return True
        if user.is_manager and timesheet.user.manager == user:
            return True
        if user.is_manager and DelegationService.can_approve_via_delegation(user, timesheet):
            return True
        return False

    def retrieve(self, request, *args, **kwargs):
        try:
            timesheet = Timesheet.objects.select_related('user', 'approved_by').get(
                pk=kwargs['pk']
            )
        except Timesheet.DoesNotExist:
            return Response(
                {'detail': 'Not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if not self._can_access_timesheet(request.user, timesheet):
            return Response(
                {'detail': 'Not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(timesheet)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """Submit a timesheet for approval."""
        try:
            timesheet = Timesheet.objects.get(pk=pk, user=request.user)
        except Timesheet.DoesNotExist:
            return Response(
                {'detail': 'Not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = TimesheetSubmitSerializer(
            data={},
            context={'request': request, 'timesheet': timesheet}
        )

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        timesheet = serializer.save()

        from apps.timesheets.tasks import send_timesheet_submitted_notification
        send_timesheet_submitted_notification.delay(timesheet.id)

        return Response(TimesheetDetailSerializer(timesheet).data)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a submitted timesheet."""
        if not request.user.is_manager:
            return Response(
                {'detail': 'Only managers can approve timesheets.'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            timesheet = Timesheet.objects.select_related('user').get(pk=pk)
        except Timesheet.DoesNotExist:
            return Response(
                {'detail': 'Not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if not self._can_manage_timesheet(request.user, timesheet):
            return Response(
                {'detail': 'You cannot approve this timesheet.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = TimesheetApproveSerializer(
            data={},
            context={'request': request, 'timesheet': timesheet}
        )

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        timesheet = serializer.save()

        from apps.timesheets.tasks import send_timesheet_approved_notification
        send_timesheet_approved_notification.delay(timesheet.id)

        return Response(TimesheetDetailSerializer(timesheet).data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a submitted timesheet."""
        if not request.user.is_manager:
            return Response(
                {'detail': 'Only managers can reject timesheets.'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            timesheet = Timesheet.objects.select_related('user').get(pk=pk)
        except Timesheet.DoesNotExist:
            return Response(
                {'detail': 'Not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if not self._can_manage_timesheet(request.user, timesheet):
            return Response(
                {'detail': 'You cannot reject this timesheet.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = TimesheetRejectSerializer(
            data=request.data,
            context={'request': request, 'timesheet': timesheet}
        )

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        timesheet = serializer.save()

        from apps.timesheets.tasks import send_timesheet_rejected_notification
        send_timesheet_rejected_notification.delay(timesheet.id)

        return Response(TimesheetDetailSerializer(timesheet).data)

    @action(detail=True, methods=['post'])
    def unlock(self, request, pk=None):
        """Admin unlock of a timesheet."""
        if not request.user.is_admin:
            return Response(
                {'detail': 'Only admins can unlock timesheets.'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            timesheet = Timesheet.objects.select_related('user', 'user__company__settings').get(pk=pk)
        except Timesheet.DoesNotExist:
            return Response(
                {'detail': 'Not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = TimesheetUnlockSerializer(
            data=request.data,
            context={'request': request, 'timesheet': timesheet}
        )

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        timesheet = serializer.save()
        return Response(TimesheetDetailSerializer(timesheet).data)

    @action(detail=True, methods=['get', 'post'])
    def comments(self, request, pk=None):
        """List or add comments on a timesheet."""
        try:
            timesheet = Timesheet.objects.select_related('user').get(pk=pk)
        except Timesheet.DoesNotExist:
            return Response(
                {'detail': 'Not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if not self._can_access_timesheet(request.user, timesheet):
            return Response(
                {'detail': 'Not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if request.method == 'GET':
            comments = timesheet.comments.select_related('author', 'entry').all()
            serializer = TimesheetCommentSerializer(comments, many=True)
            return Response(serializer.data)

        serializer = TimesheetCommentCreateSerializer(
            data=request.data,
            context={'request': request, 'timesheet': timesheet}
        )

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        comment = serializer.save()
        return Response(
            TimesheetCommentSerializer(comment).data,
            status=status.HTTP_201_CREATED
        )


class OOOPeriodViewSet(viewsets.ModelViewSet):
    """ViewSet for OOO Period CRUD operations."""

    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination
    serializer_class = OOOPeriodSerializer
    http_method_names = ['get', 'post', 'delete']

    def get_queryset(self):
        return OOOPeriod.objects.filter(user=self.request.user).order_by('-start_date')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        start_date = serializer.validated_data['start_date']
        end_date = serializer.validated_data['end_date']

        try:
            ooo_period = OOOService.create_ooo_period(
                user=request.user,
                start_date=start_date,
                end_date=end_date,
            )
        except ValueError as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            OOOPeriodSerializer(ooo_period).data,
            status=status.HTTP_201_CREATED
        )

    def destroy(self, request, *args, **kwargs):
        try:
            ooo_period = OOOPeriod.objects.get(
                pk=kwargs['pk'],
                user=request.user
            )
        except OOOPeriod.DoesNotExist:
            return Response(
                {'detail': 'Not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if not OOOService.cancel_ooo_period(ooo_period):
            return Response(
                {'detail': 'Cannot cancel past OOO periods.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminAuditLogView(APIView):
    """GET /api/v1/timesheets/audit-log/ - List AdminOverride records."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_admin:
            return Response(
                {'detail': 'Only admins can view audit logs.'},
                status=status.HTTP_403_FORBIDDEN
            )

        queryset = AdminOverride.objects.filter(
            timesheet__user__company=request.user.company
        ).select_related('timesheet', 'timesheet__user', 'admin')

        action_filter = request.query_params.get('action')
        admin_id = request.query_params.get('admin_id')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if action_filter:
            queryset = queryset.filter(action=action_filter)
        if admin_id:
            queryset = queryset.filter(admin_id=admin_id)
        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)

        queryset = queryset.order_by('-created_at')

        paginator = StandardPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = AdminOverrideSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class ApprovalDelegationViewSet(viewsets.ModelViewSet):
    """ViewSet for ApprovalDelegation CRUD operations."""

    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination
    serializer_class = ApprovalDelegationSerializer
    http_method_names = ['get', 'post', 'delete']

    def get_queryset(self):
        user = self.request.user
        received = self.request.query_params.get('received')

        if received == 'true':
            return ApprovalDelegation.objects.filter(delegate=user)
        return ApprovalDelegation.objects.filter(delegator=user)

    def list(self, request, *args, **kwargs):
        if not request.user.is_manager:
            return Response(
                {'detail': 'Only managers can view delegations.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        if not request.user.is_manager:
            return Response(
                {'detail': 'Only managers can create delegations.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ApprovalDelegationCreateSerializer(
            data=request.data,
            context={'request': request}
        )

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        delegation = serializer.save()
        return Response(
            ApprovalDelegationSerializer(delegation).data,
            status=status.HTTP_201_CREATED
        )

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_manager:
            return Response(
                {'detail': 'Only managers can revoke delegations.'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            delegation = ApprovalDelegation.objects.get(
                pk=kwargs['pk'],
                delegator=request.user
            )
        except ApprovalDelegation.DoesNotExist:
            return Response(
                {'detail': 'Not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        delegation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
