"""
Views for Reporting/Analytics API.
"""
from datetime import date, datetime
from decimal import Decimal

from django.db.models import Sum, Count, Q
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.timeentries.models import TimeEntry
from apps.timesheets.models import Timesheet
from apps.users.models import User


class HoursSummaryView(APIView):
    """GET /api/v1/reports/hours/summary/"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_manager:
            return Response(
                {'detail': 'Only managers and admins can view reports.'},
                status=status.HTTP_403_FORBIDDEN
            )

        queryset = TimeEntry.objects.filter(
            user__company=request.user.company,
            timesheet__status=Timesheet.Status.APPROVED,
        )

        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        group_by = request.query_params.get('group_by')

        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)

        if not request.user.is_admin:
            managed_users = User.objects.filter(manager=request.user)
            queryset = queryset.filter(
                Q(user__in=managed_users) | Q(user=request.user)
            )

        total_hours = queryset.aggregate(total=Sum('hours'))['total'] or Decimal('0.00')

        response_data = {
            'total_hours': str(total_hours),
            'entry_count': queryset.count(),
        }

        if group_by == 'user':
            by_user = queryset.values('user__id', 'user__email', 'user__first_name', 'user__last_name').annotate(
                total_hours=Sum('hours')
            ).order_by('-total_hours')
            response_data['by_user'] = [
                {
                    'user_id': item['user__id'],
                    'email': item['user__email'],
                    'name': f"{item['user__first_name']} {item['user__last_name']}".strip(),
                    'total_hours': str(item['total_hours']),
                }
                for item in by_user
            ]

        if group_by == 'project':
            by_project = queryset.values('project__id', 'project__name').annotate(
                total_hours=Sum('hours')
            ).order_by('-total_hours')
            response_data['by_project'] = [
                {
                    'project_id': item['project__id'],
                    'project_name': item['project__name'],
                    'total_hours': str(item['total_hours']),
                }
                for item in by_project
            ]

        return Response(response_data)


class ApprovalMetricsView(APIView):
    """GET /api/v1/reports/approval/metrics/"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_manager:
            return Response(
                {'detail': 'Only managers and admins can view reports.'},
                status=status.HTTP_403_FORBIDDEN
            )

        queryset = Timesheet.objects.filter(user__company=request.user.company)

        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if start_date:
            queryset = queryset.filter(week_start__gte=start_date)
        if end_date:
            queryset = queryset.filter(week_start__lte=end_date)

        if not request.user.is_admin:
            managed_users = User.objects.filter(manager=request.user)
            queryset = queryset.filter(
                Q(user__in=managed_users) | Q(user=request.user)
            )

        total = queryset.count()
        draft_count = queryset.filter(status=Timesheet.Status.DRAFT).count()
        submitted_count = queryset.filter(status=Timesheet.Status.SUBMITTED).count()
        approved_count = queryset.filter(status=Timesheet.Status.APPROVED).count()
        rejected_count = queryset.filter(status=Timesheet.Status.REJECTED).count()

        decided_count = approved_count + rejected_count
        approval_rate = (approved_count / decided_count * 100) if decided_count > 0 else 0

        return Response({
            'total_timesheets': total,
            'draft_count': draft_count,
            'submitted_count': submitted_count,
            'approved_count': approved_count,
            'rejected_count': rejected_count,
            'approval_rate': round(approval_rate, 2),
        })


class UtilizationReportView(APIView):
    """GET /api/v1/reports/utilization/"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_manager:
            return Response(
                {'detail': 'Only managers and admins can view reports.'},
                status=status.HTTP_403_FORBIDDEN
            )

        queryset = User.objects.filter(
            company=request.user.company,
            is_active=True,
        )

        user_id = request.query_params.get('user_id')
        expected_weekly_hours = Decimal(request.query_params.get('expected_weekly_hours', '40'))
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if user_id:
            queryset = queryset.filter(id=user_id)

        if not request.user.is_admin:
            managed_users = User.objects.filter(manager=request.user)
            queryset = queryset.filter(
                Q(id__in=managed_users.values_list('id', flat=True)) | Q(id=request.user.id)
            )

        entry_filters = Q(
            timeentries__timesheet__status=Timesheet.Status.APPROVED
        )
        if start_date:
            entry_filters &= Q(timeentries__date__gte=start_date)
        if end_date:
            entry_filters &= Q(timeentries__date__lte=end_date)

        utilization_data = []
        for user in queryset:
            total_hours = TimeEntry.objects.filter(
                user=user,
                timesheet__status=Timesheet.Status.APPROVED,
            )
            if start_date:
                total_hours = total_hours.filter(date__gte=start_date)
            if end_date:
                total_hours = total_hours.filter(date__lte=end_date)

            hours_sum = total_hours.aggregate(total=Sum('hours'))['total'] or Decimal('0.00')
            utilization_percent = float(hours_sum / expected_weekly_hours * 100) if expected_weekly_hours > 0 else 0

            utilization_data.append({
                'user_id': user.id,
                'email': user.email,
                'name': f"{user.first_name} {user.last_name}".strip(),
                'total_hours': str(hours_sum),
                'expected_hours': str(expected_weekly_hours),
                'utilization_percent': round(utilization_percent, 2),
            })

        return Response({
            'utilization_data': utilization_data,
            'expected_weekly_hours': str(expected_weekly_hours),
        })
