"""
Tests for Admin Audit Log API - TDD approach.

Endpoint:
- GET /api/v1/timesheets/audit-log/ - List AdminOverride records
"""
from datetime import date, timedelta

import pytest
from rest_framework import status

from apps.timesheets.models import AdminOverride, Timesheet


def get_week_start(d: date = None) -> date:
    """Get the Monday of the week containing the given date."""
    if d is None:
        d = date.today()
    return d - timedelta(days=d.weekday())


@pytest.mark.django_db
class TestAdminAuditLogEndpoint:
    """Tests for GET /api/v1/timesheets/audit-log/"""

    def test_admin_can_list_audit_log(
        self, authenticated_admin_client, admin, user, timesheet_factory
    ):
        """
        Given: AdminOverride records exist
        When: GET /timesheets/audit-log/
        Then: Returns list of audit records
        """
        timesheet = timesheet_factory(user=user, status=Timesheet.Status.APPROVED)
        AdminOverride.objects.create(
            timesheet=timesheet,
            admin=admin,
            action=AdminOverride.Action.UNLOCK,
            reason='Correction needed',
            previous_status=Timesheet.Status.APPROVED,
        )

        response = authenticated_admin_client.get('/api/v1/timesheets/audit-log/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['data']) == 1
        assert response.data['data'][0]['action'] == AdminOverride.Action.UNLOCK
        assert response.data['data'][0]['reason'] == 'Correction needed'

    def test_audit_log_includes_admin_details(
        self, authenticated_admin_client, admin, user, timesheet_factory
    ):
        """
        Given: AdminOverride record
        When: GET /timesheets/audit-log/
        Then: Includes admin user details
        """
        timesheet = timesheet_factory(user=user, status=Timesheet.Status.APPROVED)
        AdminOverride.objects.create(
            timesheet=timesheet,
            admin=admin,
            action=AdminOverride.Action.UNLOCK,
            reason='Test reason',
            previous_status=Timesheet.Status.APPROVED,
        )

        response = authenticated_admin_client.get('/api/v1/timesheets/audit-log/')

        assert response.status_code == status.HTTP_200_OK
        record = response.data['data'][0]
        assert 'admin_id' in record
        assert 'admin_email' in record
        assert record['admin_id'] == admin.id

    def test_audit_log_includes_timesheet_details(
        self, authenticated_admin_client, admin, user, timesheet_factory
    ):
        """
        Given: AdminOverride record
        When: GET /timesheets/audit-log/
        Then: Includes timesheet and user details
        """
        timesheet = timesheet_factory(user=user, status=Timesheet.Status.APPROVED)
        AdminOverride.objects.create(
            timesheet=timesheet,
            admin=admin,
            action=AdminOverride.Action.UNLOCK,
            reason='Test reason',
            previous_status=Timesheet.Status.APPROVED,
        )

        response = authenticated_admin_client.get('/api/v1/timesheets/audit-log/')

        assert response.status_code == status.HTTP_200_OK
        record = response.data['data'][0]
        assert 'timesheet_id' in record
        assert 'timesheet_user_id' in record
        assert 'timesheet_week_start' in record

    def test_audit_log_filters_by_action(
        self, authenticated_admin_client, admin, user, timesheet_factory
    ):
        """
        Given: Multiple AdminOverride actions
        When: GET /timesheets/audit-log/?action=UNLOCK
        Then: Only UNLOCK actions returned
        """
        timesheet1 = timesheet_factory(user=user, status=Timesheet.Status.APPROVED)
        timesheet2 = timesheet_factory(
            user=user, status=Timesheet.Status.APPROVED,
            week_start=get_week_start(date.today() - timedelta(weeks=1))
        )
        AdminOverride.objects.create(
            timesheet=timesheet1,
            admin=admin,
            action=AdminOverride.Action.UNLOCK,
            reason='Unlock reason',
            previous_status=Timesheet.Status.APPROVED,
        )
        AdminOverride.objects.create(
            timesheet=timesheet2,
            admin=admin,
            action=AdminOverride.Action.FORCE_APPROVE,
            reason='Force approve reason',
            previous_status=Timesheet.Status.SUBMITTED,
        )

        response = authenticated_admin_client.get('/api/v1/timesheets/audit-log/?action=UNLOCK')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['data']) == 1
        assert response.data['data'][0]['action'] == AdminOverride.Action.UNLOCK

    def test_audit_log_filters_by_admin(
        self, authenticated_admin_client, admin, user, user_factory, timesheet_factory
    ):
        """
        Given: Actions by different admins
        When: GET /timesheets/audit-log/?admin_id=X
        Then: Only that admin's actions returned
        """
        from apps.users.models import User

        admin2 = user_factory(role=User.Role.ADMIN)
        timesheet = timesheet_factory(user=user, status=Timesheet.Status.APPROVED)
        AdminOverride.objects.create(
            timesheet=timesheet,
            admin=admin,
            action=AdminOverride.Action.UNLOCK,
            reason='Admin 1 action',
            previous_status=Timesheet.Status.APPROVED,
        )
        timesheet2 = timesheet_factory(
            user=user, status=Timesheet.Status.APPROVED,
            week_start=get_week_start(date.today() - timedelta(weeks=1))
        )
        AdminOverride.objects.create(
            timesheet=timesheet2,
            admin=admin2,
            action=AdminOverride.Action.UNLOCK,
            reason='Admin 2 action',
            previous_status=Timesheet.Status.APPROVED,
        )

        response = authenticated_admin_client.get(f'/api/v1/timesheets/audit-log/?admin_id={admin.id}')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['data']) == 1
        assert response.data['data'][0]['admin_id'] == admin.id

    def test_audit_log_filters_by_date_range(
        self, authenticated_admin_client, admin, user, timesheet_factory
    ):
        """
        Given: Actions at different times
        When: GET /timesheets/audit-log/?start_date=X&end_date=Y
        Then: Only actions in range returned
        """
        today = date.today()
        timesheet = timesheet_factory(user=user, status=Timesheet.Status.APPROVED)
        AdminOverride.objects.create(
            timesheet=timesheet,
            admin=admin,
            action=AdminOverride.Action.UNLOCK,
            reason='Recent action',
            previous_status=Timesheet.Status.APPROVED,
        )

        response = authenticated_admin_client.get(
            f'/api/v1/timesheets/audit-log/?start_date={today - timedelta(days=1)}'
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['data']) == 1

    def test_audit_log_ordered_by_created_at_desc(
        self, authenticated_admin_client, admin, user, timesheet_factory
    ):
        """
        Given: Multiple audit records
        When: GET /timesheets/audit-log/
        Then: Records ordered by created_at descending (newest first)
        """
        timesheet1 = timesheet_factory(user=user, status=Timesheet.Status.APPROVED)
        timesheet2 = timesheet_factory(
            user=user, status=Timesheet.Status.APPROVED,
            week_start=get_week_start(date.today() - timedelta(weeks=1))
        )
        record1 = AdminOverride.objects.create(
            timesheet=timesheet1,
            admin=admin,
            action=AdminOverride.Action.UNLOCK,
            reason='First action',
            previous_status=Timesheet.Status.APPROVED,
        )
        record2 = AdminOverride.objects.create(
            timesheet=timesheet2,
            admin=admin,
            action=AdminOverride.Action.FORCE_APPROVE,
            reason='Second action',
            previous_status=Timesheet.Status.SUBMITTED,
        )

        response = authenticated_admin_client.get('/api/v1/timesheets/audit-log/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['data']) == 2
        assert response.data['data'][0]['id'] == record2.id

    def test_manager_cannot_view_audit_log(self, authenticated_manager_client):
        """
        Given: Manager user (not admin)
        When: GET /timesheets/audit-log/
        Then: Returns 403 Forbidden
        """
        response = authenticated_manager_client.get('/api/v1/timesheets/audit-log/')

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_employee_cannot_view_audit_log(self, authenticated_client):
        """
        Given: Regular employee
        When: GET /timesheets/audit-log/
        Then: Returns 403 Forbidden
        """
        response = authenticated_client.get('/api/v1/timesheets/audit-log/')

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_returns_401(self, api_client):
        """
        Given: No authentication
        When: GET /timesheets/audit-log/
        Then: Returns 401
        """
        response = api_client.get('/api/v1/timesheets/audit-log/')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
