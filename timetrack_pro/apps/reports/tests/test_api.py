"""
Tests for Reporting/Analytics API - TDD approach.

Endpoints:
- GET /api/v1/reports/hours/summary/ - Hours summary by user/project/period
- GET /api/v1/reports/approval/metrics/ - Approval workflow metrics
- GET /api/v1/reports/utilization/ - Utilization report
"""
from datetime import date, timedelta
from decimal import Decimal

import pytest
from rest_framework import status

from apps.timesheets.models import Timesheet


def get_week_start(d: date = None) -> date:
    """Get the Monday of the week containing the given date."""
    if d is None:
        d = date.today()
    return d - timedelta(days=d.weekday())


@pytest.mark.django_db
class TestHoursSummaryEndpoint:
    """Tests for GET /api/v1/reports/hours/summary/"""

    def test_admin_can_get_hours_summary(
        self, authenticated_admin_client, user, project, timesheet_factory,
        time_entry_factory, company
    ):
        """
        Given: Approved timesheets with time entries
        When: GET /reports/hours/summary/
        Then: Returns aggregated hours data
        """
        timesheet = timesheet_factory(user=user, status=Timesheet.Status.APPROVED)
        time_entry_factory(user=user, project=project, timesheet=timesheet, hours=Decimal('8.00'))
        time_entry_factory(user=user, project=project, timesheet=timesheet, hours=Decimal('6.00'))

        response = authenticated_admin_client.get('/api/v1/reports/hours/summary/')

        assert response.status_code == status.HTTP_200_OK
        assert 'total_hours' in response.data
        assert Decimal(response.data['total_hours']) == Decimal('14.00')

    def test_hours_summary_filters_by_date_range(
        self, authenticated_admin_client, user, project, timesheet_factory,
        time_entry_factory
    ):
        """
        Given: Time entries across different dates
        When: GET /reports/hours/summary/?start_date=X&end_date=Y
        Then: Only entries in range included
        """
        timesheet = timesheet_factory(user=user, status=Timesheet.Status.APPROVED)
        today = date.today()
        time_entry_factory(
            user=user, project=project, timesheet=timesheet,
            date=today, hours=Decimal('8.00')
        )
        time_entry_factory(
            user=user, project=project, timesheet=timesheet,
            date=today - timedelta(days=30), hours=Decimal('4.00')
        )

        response = authenticated_admin_client.get(
            f'/api/v1/reports/hours/summary/?start_date={today - timedelta(days=7)}&end_date={today}'
        )

        assert response.status_code == status.HTTP_200_OK
        assert Decimal(response.data['total_hours']) == Decimal('8.00')

    def test_hours_summary_groups_by_user(
        self, authenticated_admin_client, user, user_factory, project,
        timesheet_factory, time_entry_factory
    ):
        """
        Given: Time entries from multiple users
        When: GET /reports/hours/summary/?group_by=user
        Then: Returns hours grouped by user
        """
        user2 = user_factory()
        timesheet1 = timesheet_factory(user=user, status=Timesheet.Status.APPROVED)
        timesheet2 = timesheet_factory(user=user2, status=Timesheet.Status.APPROVED)
        time_entry_factory(user=user, project=project, timesheet=timesheet1, hours=Decimal('8.00'))
        time_entry_factory(user=user2, project=project, timesheet=timesheet2, hours=Decimal('6.00'))

        response = authenticated_admin_client.get('/api/v1/reports/hours/summary/?group_by=user')

        assert response.status_code == status.HTTP_200_OK
        assert 'by_user' in response.data
        assert len(response.data['by_user']) == 2

    def test_hours_summary_groups_by_project(
        self, authenticated_admin_client, user, project, project_factory,
        timesheet_factory, time_entry_factory
    ):
        """
        Given: Time entries on multiple projects
        When: GET /reports/hours/summary/?group_by=project
        Then: Returns hours grouped by project
        """
        project2 = project_factory()
        timesheet = timesheet_factory(user=user, status=Timesheet.Status.APPROVED)
        time_entry_factory(user=user, project=project, timesheet=timesheet, hours=Decimal('8.00'))
        time_entry_factory(user=user, project=project2, timesheet=timesheet, hours=Decimal('4.00'))

        response = authenticated_admin_client.get('/api/v1/reports/hours/summary/?group_by=project')

        assert response.status_code == status.HTTP_200_OK
        assert 'by_project' in response.data
        assert len(response.data['by_project']) == 2

    def test_manager_can_view_team_hours(
        self, authenticated_manager_client, user, project, timesheet_factory,
        time_entry_factory, manager
    ):
        """
        Given: Manager with reports
        When: GET /reports/hours/summary/
        Then: Returns hours for managed users
        """
        timesheet = timesheet_factory(user=user, status=Timesheet.Status.APPROVED)
        time_entry_factory(user=user, project=project, timesheet=timesheet, hours=Decimal('8.00'))

        response = authenticated_manager_client.get('/api/v1/reports/hours/summary/')

        assert response.status_code == status.HTTP_200_OK

    def test_employee_cannot_view_reports(self, authenticated_client):
        """
        Given: Regular employee
        When: GET /reports/hours/summary/
        Then: Returns 403 Forbidden
        """
        response = authenticated_client.get('/api/v1/reports/hours/summary/')

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_returns_401(self, api_client):
        """
        Given: No authentication
        When: GET /reports/hours/summary/
        Then: Returns 401
        """
        response = api_client.get('/api/v1/reports/hours/summary/')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestApprovalMetricsEndpoint:
    """Tests for GET /api/v1/reports/approval/metrics/"""

    def test_admin_can_get_approval_metrics(
        self, authenticated_admin_client, user, timesheet_factory
    ):
        """
        Given: Timesheets in various states
        When: GET /reports/approval/metrics/
        Then: Returns approval workflow metrics
        """
        today = date.today()
        timesheet_factory(user=user, status=Timesheet.Status.DRAFT, week_start=get_week_start(today))
        timesheet_factory(user=user, status=Timesheet.Status.SUBMITTED, week_start=get_week_start(today - timedelta(weeks=1)))
        timesheet_factory(user=user, status=Timesheet.Status.APPROVED, week_start=get_week_start(today - timedelta(weeks=2)))
        timesheet_factory(user=user, status=Timesheet.Status.REJECTED, week_start=get_week_start(today - timedelta(weeks=3)))

        response = authenticated_admin_client.get('/api/v1/reports/approval/metrics/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['total_timesheets'] == 4
        assert response.data['draft_count'] == 1
        assert response.data['submitted_count'] == 1
        assert response.data['approved_count'] == 1
        assert response.data['rejected_count'] == 1

    def test_approval_metrics_includes_rates(
        self, authenticated_admin_client, user, timesheet_factory
    ):
        """
        Given: Multiple timesheets
        When: GET /reports/approval/metrics/
        Then: Includes approval/rejection rates
        """
        today = date.today()
        timesheet_factory(user=user, status=Timesheet.Status.APPROVED, week_start=get_week_start(today))
        timesheet_factory(user=user, status=Timesheet.Status.APPROVED, week_start=get_week_start(today - timedelta(weeks=1)))
        timesheet_factory(user=user, status=Timesheet.Status.REJECTED, week_start=get_week_start(today - timedelta(weeks=2)))

        response = authenticated_admin_client.get('/api/v1/reports/approval/metrics/')

        assert response.status_code == status.HTTP_200_OK
        assert 'approval_rate' in response.data

    def test_approval_metrics_filters_by_date(
        self, authenticated_admin_client, user, timesheet_factory
    ):
        """
        Given: Timesheets from different periods
        When: GET /reports/approval/metrics/?start_date=X&end_date=Y
        Then: Only includes timesheets in range
        """
        today = date.today()
        timesheet_factory(user=user, status=Timesheet.Status.APPROVED, week_start=get_week_start(today - timedelta(weeks=4)))
        timesheet_factory(user=user, status=Timesheet.Status.APPROVED, week_start=get_week_start(today))

        response = authenticated_admin_client.get(
            f'/api/v1/reports/approval/metrics/?start_date={today - timedelta(days=7)}'
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data['total_timesheets'] == 1

    def test_manager_can_view_team_metrics(
        self, authenticated_manager_client, user, timesheet_factory
    ):
        """
        Given: Manager with team
        When: GET /reports/approval/metrics/
        Then: Returns metrics for managed users
        """
        timesheet_factory(user=user, status=Timesheet.Status.SUBMITTED)

        response = authenticated_manager_client.get('/api/v1/reports/approval/metrics/')

        assert response.status_code == status.HTTP_200_OK

    def test_employee_cannot_view_metrics(self, authenticated_client):
        """
        Given: Regular employee
        When: GET /reports/approval/metrics/
        Then: Returns 403 Forbidden
        """
        response = authenticated_client.get('/api/v1/reports/approval/metrics/')

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestUtilizationReportEndpoint:
    """Tests for GET /api/v1/reports/utilization/"""

    def test_admin_can_get_utilization_report(
        self, authenticated_admin_client, user, project, timesheet_factory,
        time_entry_factory
    ):
        """
        Given: Time entries for users
        When: GET /reports/utilization/
        Then: Returns utilization percentage per user
        """
        timesheet = timesheet_factory(user=user, status=Timesheet.Status.APPROVED)
        time_entry_factory(user=user, project=project, timesheet=timesheet, hours=Decimal('40.00'))

        response = authenticated_admin_client.get('/api/v1/reports/utilization/')

        assert response.status_code == status.HTTP_200_OK
        assert 'utilization_data' in response.data

    def test_utilization_filters_by_user(
        self, authenticated_admin_client, user, project, timesheet_factory,
        time_entry_factory
    ):
        """
        Given: Multiple users
        When: GET /reports/utilization/?user_id=X
        Then: Returns utilization for specific user
        """
        timesheet = timesheet_factory(user=user, status=Timesheet.Status.APPROVED)
        time_entry_factory(user=user, project=project, timesheet=timesheet, hours=Decimal('40.00'))

        response = authenticated_admin_client.get(
            f'/api/v1/reports/utilization/?user_id={user.id}'
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['utilization_data']) == 1

    def test_utilization_sets_expected_hours(
        self, authenticated_admin_client, user, project, timesheet_factory,
        time_entry_factory
    ):
        """
        Given: User with logged hours
        When: GET /reports/utilization/?expected_weekly_hours=40&user_id=X
        Then: Calculates utilization based on expected
        """
        timesheet = timesheet_factory(user=user, status=Timesheet.Status.APPROVED)
        time_entry_factory(user=user, project=project, timesheet=timesheet, hours=Decimal('32.00'))

        response = authenticated_admin_client.get(
            f'/api/v1/reports/utilization/?expected_weekly_hours=40&user_id={user.id}'
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['utilization_data']) == 1
        utilization = response.data['utilization_data'][0]
        assert utilization['utilization_percent'] == 80.0

    def test_employee_cannot_view_utilization(self, authenticated_client):
        """
        Given: Regular employee
        When: GET /reports/utilization/
        Then: Returns 403 Forbidden
        """
        response = authenticated_client.get('/api/v1/reports/utilization/')

        assert response.status_code == status.HTTP_403_FORBIDDEN
