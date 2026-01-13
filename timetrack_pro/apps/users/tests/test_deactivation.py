"""
Tests for User Deactivation workflow - TDD approach.

Business Rules:
- Deactivation requires all pending timesheets to be approved/rejected first
- Admin can override with force deactivation
- Deactivation exports user data (JSON + base64 CSV blob)
- Export stored in audit table
"""
import base64
import json
from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.utils import timezone
from rest_framework import status

from apps.timesheets.models import Timesheet
from apps.users.models import User


@pytest.mark.django_db
class TestUserDeactivationService:
    """Tests for user deactivation service logic."""

    def test_can_deactivate_user_with_no_pending_timesheets(self, user):
        """
        Given: User with no pending timesheets
        When: Checking if can deactivate
        Then: Returns True
        """
        from apps.users.services import DeactivationService

        assert DeactivationService.can_deactivate(user) is True

    def test_cannot_deactivate_user_with_submitted_timesheet(self, user):
        """
        Given: User with SUBMITTED timesheet
        When: Checking if can deactivate
        Then: Returns False
        """
        from apps.users.services import DeactivationService

        Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
            status=Timesheet.Status.SUBMITTED,
        )

        assert DeactivationService.can_deactivate(user) is False

    def test_cannot_deactivate_user_with_draft_timesheet(self, user):
        """
        Given: User with DRAFT timesheet
        When: Checking if can deactivate
        Then: Returns False (drafts need resolution)
        """
        from apps.users.services import DeactivationService

        Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
            status=Timesheet.Status.DRAFT,
        )

        assert DeactivationService.can_deactivate(user) is False

    def test_can_deactivate_user_with_only_approved_timesheets(self, user):
        """
        Given: User with only APPROVED timesheets
        When: Checking if can deactivate
        Then: Returns True
        """
        from apps.users.services import DeactivationService

        Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
            status=Timesheet.Status.APPROVED,
        )

        assert DeactivationService.can_deactivate(user) is True

    def test_can_deactivate_user_with_only_rejected_timesheets(self, user):
        """
        Given: User with only REJECTED timesheets
        When: Checking if can deactivate
        Then: Returns True (rejected = resolved)
        """
        from apps.users.services import DeactivationService

        Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
            status=Timesheet.Status.REJECTED,
        )

        assert DeactivationService.can_deactivate(user) is True

    def test_get_pending_timesheets_count(self, user):
        """
        Given: User with mix of timesheet statuses
        When: Getting pending count
        Then: Returns count of DRAFT + SUBMITTED
        """
        from apps.users.services import DeactivationService

        Timesheet.objects.create(
            user=user, week_start=date(2024, 6, 3), status=Timesheet.Status.DRAFT
        )
        Timesheet.objects.create(
            user=user, week_start=date(2024, 6, 10), status=Timesheet.Status.SUBMITTED
        )
        Timesheet.objects.create(
            user=user, week_start=date(2024, 6, 17), status=Timesheet.Status.APPROVED
        )

        assert DeactivationService.get_pending_timesheets_count(user) == 2


@pytest.mark.django_db
class TestUserDataExport:
    """Tests for user data export functionality."""

    def test_export_user_data_returns_json(self, user, project, time_entry_factory):
        """
        Given: User with time entries
        When: Exporting user data
        Then: Returns JSON with user profile and entries
        """
        from apps.users.services import DeactivationService

        time_entry_factory(user=user, project=project, hours=Decimal('8.00'))

        export_data = DeactivationService.export_user_data(user)

        assert 'profile' in export_data
        assert 'time_entries' in export_data
        assert export_data['profile']['email'] == user.email

    def test_export_includes_timesheets(self, user):
        """
        Given: User with timesheets
        When: Exporting user data
        Then: Export includes timesheet data
        """
        from apps.users.services import DeactivationService

        Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
            status=Timesheet.Status.APPROVED,
        )

        export_data = DeactivationService.export_user_data(user)

        assert 'timesheets' in export_data
        assert len(export_data['timesheets']) == 1

    def test_export_creates_csv_blob(self, user, project, time_entry_factory):
        """
        Given: User with time entries
        When: Exporting user data
        Then: Returns base64-encoded CSV blob
        """
        from apps.users.services import DeactivationService

        time_entry_factory(user=user, project=project, hours=Decimal('8.00'))

        export_data = DeactivationService.export_user_data(user)

        assert 'csv_blob' in export_data
        decoded = base64.b64decode(export_data['csv_blob'])
        assert b'date' in decoded.lower() or b'hours' in decoded.lower()

    def test_export_stored_in_audit_table(self, user, admin):
        """
        Given: User being deactivated
        When: Deactivation is executed
        Then: Export is stored in UserDeactivationAudit
        """
        from apps.users.models import UserDeactivationAudit
        from apps.users.services import DeactivationService

        DeactivationService.execute_deactivation(
            user=user,
            admin=admin,
            reason='Employee departure',
        )

        audit = UserDeactivationAudit.objects.get(user=user)
        assert audit.admin == admin
        assert audit.reason == 'Employee departure'
        assert audit.export_data is not None


@pytest.mark.django_db
class TestDeactivationExecution:
    """Tests for executing user deactivation."""

    def test_deactivation_sets_user_inactive(self, user, admin):
        """
        Given: Active user with no pending timesheets
        When: Executing deactivation
        Then: User is_active becomes False
        """
        from apps.users.services import DeactivationService

        DeactivationService.execute_deactivation(
            user=user,
            admin=admin,
            reason='Employee departure',
        )

        user.refresh_from_db()
        assert user.is_active is False

    def test_deactivation_fails_with_pending_timesheets(self, user, admin):
        """
        Given: User with pending timesheets
        When: Executing deactivation without force
        Then: Raises ValueError
        """
        from apps.users.services import DeactivationService

        Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
            status=Timesheet.Status.SUBMITTED,
        )

        with pytest.raises(ValueError, match='pending'):
            DeactivationService.execute_deactivation(
                user=user,
                admin=admin,
                reason='Employee departure',
            )

    def test_force_deactivation_works_with_pending_timesheets(self, user, admin):
        """
        Given: User with pending timesheets
        When: Force deactivating
        Then: User is deactivated anyway
        """
        from apps.users.services import DeactivationService

        Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
            status=Timesheet.Status.SUBMITTED,
        )

        DeactivationService.execute_deactivation(
            user=user,
            admin=admin,
            reason='Termination',
            force=True,
        )

        user.refresh_from_db()
        assert user.is_active is False

    def test_force_deactivation_records_force_flag(self, user, admin):
        """
        Given: Force deactivation
        When: Checking audit record
        Then: Force flag is True
        """
        from apps.users.models import UserDeactivationAudit
        from apps.users.services import DeactivationService

        Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
            status=Timesheet.Status.SUBMITTED,
        )

        DeactivationService.execute_deactivation(
            user=user,
            admin=admin,
            reason='Termination',
            force=True,
        )

        audit = UserDeactivationAudit.objects.get(user=user)
        assert audit.was_forced is True


@pytest.mark.django_db
class TestDeactivationAPI:
    """Tests for user deactivation API endpoint."""

    def test_admin_can_deactivate_user(self, authenticated_admin_client, user):
        """
        Given: Admin user
        When: POST /users/:id/deactivate/
        Then: Returns 200 and user is deactivated
        """
        response = authenticated_admin_client.post(
            f'/api/v1/users/{user.id}/deactivate/',
            {'reason': 'Employee departure'},
        )

        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.is_active is False

    def test_admin_can_force_deactivate(self, authenticated_admin_client, user):
        """
        Given: User with pending timesheets
        When: Admin force deactivates
        Then: Returns 200
        """
        Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
            status=Timesheet.Status.SUBMITTED,
        )

        response = authenticated_admin_client.post(
            f'/api/v1/users/{user.id}/deactivate/',
            {'reason': 'Termination', 'force': True},
        )

        assert response.status_code == status.HTTP_200_OK

    def test_deactivation_fails_without_force_if_pending(
        self, authenticated_admin_client, user
    ):
        """
        Given: User with pending timesheets
        When: Admin deactivates without force
        Then: Returns 400 with pending count
        """
        Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
            status=Timesheet.Status.SUBMITTED,
        )

        response = authenticated_admin_client.post(
            f'/api/v1/users/{user.id}/deactivate/',
            {'reason': 'Employee departure'},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'pending' in str(response.data).lower()

    def test_non_admin_cannot_deactivate(self, authenticated_manager_client, user):
        """
        Given: Manager user (not admin)
        When: POST /users/:id/deactivate/
        Then: Returns 403
        """
        response = authenticated_manager_client.post(
            f'/api/v1/users/{user.id}/deactivate/',
            {'reason': 'Employee departure'},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_deactivation_requires_reason(self, authenticated_admin_client, user):
        """
        Given: Admin user
        When: POST without reason
        Then: Returns 400
        """
        response = authenticated_admin_client.post(
            f'/api/v1/users/{user.id}/deactivate/',
            {},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_cannot_deactivate_self(self, authenticated_admin_client, admin):
        """
        Given: Admin user
        When: Trying to deactivate themselves
        Then: Returns 400
        """
        response = authenticated_admin_client.post(
            f'/api/v1/users/{admin.id}/deactivate/',
            {'reason': 'Self deactivation'},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_deactivation_returns_export_summary(
        self, authenticated_admin_client, user
    ):
        """
        Given: User with data
        When: Deactivating
        Then: Response includes export summary
        """
        Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
            status=Timesheet.Status.APPROVED,
        )

        response = authenticated_admin_client.post(
            f'/api/v1/users/{user.id}/deactivate/',
            {'reason': 'Employee departure'},
        )

        assert response.status_code == status.HTTP_200_OK
        assert 'export_summary' in response.data


@pytest.mark.django_db
class TestCheckDeactivationStatusAPI:
    """Tests for checking if user can be deactivated."""

    def test_admin_can_check_deactivation_status(
        self, authenticated_admin_client, user
    ):
        """
        Given: Admin user
        When: GET /users/:id/deactivation-status/
        Then: Returns 200 with can_deactivate and pending_count
        """
        response = authenticated_admin_client.get(
            f'/api/v1/users/{user.id}/deactivation-status/'
        )

        assert response.status_code == status.HTTP_200_OK
        assert 'can_deactivate' in response.data
        assert 'pending_timesheets_count' in response.data

    def test_status_shows_pending_timesheets(self, authenticated_admin_client, user):
        """
        Given: User with pending timesheets
        When: Checking status
        Then: Shows correct pending count
        """
        Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
            status=Timesheet.Status.SUBMITTED,
        )
        Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 17),
            status=Timesheet.Status.DRAFT,
        )

        response = authenticated_admin_client.get(
            f'/api/v1/users/{user.id}/deactivation-status/'
        )

        assert response.data['can_deactivate'] is False
        assert response.data['pending_timesheets_count'] == 2
