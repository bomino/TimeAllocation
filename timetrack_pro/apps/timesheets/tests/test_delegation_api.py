"""
Tests for Delegation/Proxy Approval API - TDD approach.

Endpoints:
- GET    /api/v1/delegations/ - List active delegations
- POST   /api/v1/delegations/ - Create delegation
- DELETE /api/v1/delegations/:id/ - Revoke delegation
"""
from datetime import date, timedelta

import pytest
from rest_framework import status

from apps.timesheets.models import ApprovalDelegation, Timesheet


def get_week_start(d: date = None) -> date:
    """Get the Monday of the week containing the given date."""
    if d is None:
        d = date.today()
    return d - timedelta(days=d.weekday())


@pytest.mark.django_db
class TestListDelegationsEndpoint:
    """Tests for GET /api/v1/delegations/"""

    def test_manager_can_list_own_delegations(
        self, authenticated_manager_client, manager, user_factory
    ):
        """
        Given: Manager with active delegation
        When: GET /delegations/
        Then: Returns manager's delegations
        """
        from apps.users.models import User

        delegate = user_factory(role=User.Role.MANAGER)
        ApprovalDelegation.objects.create(
            delegator=manager,
            delegate=delegate,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=7),
        )

        response = authenticated_manager_client.get('/api/v1/delegations/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['data']) == 1
        assert response.data['data'][0]['delegate'] == delegate.id

    def test_manager_sees_delegations_they_received(
        self, authenticated_manager_client, manager, user_factory
    ):
        """
        Given: Manager who received a delegation
        When: GET /delegations/?received=true
        Then: Returns delegations where user is delegate
        """
        from apps.users.models import User

        other_manager = user_factory(role=User.Role.MANAGER)
        ApprovalDelegation.objects.create(
            delegator=other_manager,
            delegate=manager,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=7),
        )

        response = authenticated_manager_client.get('/api/v1/delegations/?received=true')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['data']) == 1
        assert response.data['data'][0]['delegator'] == other_manager.id

    def test_employee_cannot_list_delegations(self, authenticated_client):
        """
        Given: Regular employee
        When: GET /delegations/
        Then: Returns 403 Forbidden
        """
        response = authenticated_client.get('/api/v1/delegations/')

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_returns_401(self, api_client):
        """
        Given: No authentication
        When: GET /delegations/
        Then: Returns 401
        """
        response = api_client.get('/api/v1/delegations/')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestCreateDelegationEndpoint:
    """Tests for POST /api/v1/delegations/"""

    def test_manager_can_create_delegation(
        self, authenticated_manager_client, manager, user_factory
    ):
        """
        Given: Manager user
        When: POST /delegations/ with valid delegate
        Then: Returns 201 with created delegation
        """
        from apps.users.models import User

        delegate = user_factory(role=User.Role.MANAGER)
        payload = {
            'delegate_id': delegate.id,
            'start_date': str(date.today()),
            'end_date': str(date.today() + timedelta(days=7)),
        }

        response = authenticated_manager_client.post('/api/v1/delegations/', payload)

        assert response.status_code == status.HTTP_201_CREATED
        assert ApprovalDelegation.objects.filter(
            delegator=manager, delegate=delegate
        ).exists()

    def test_cannot_delegate_to_non_manager(
        self, authenticated_manager_client, user
    ):
        """
        Given: Manager trying to delegate to employee
        When: POST /delegations/
        Then: Returns 400 Bad Request
        """
        payload = {
            'delegate_id': user.id,
            'start_date': str(date.today()),
            'end_date': str(date.today() + timedelta(days=7)),
        }

        response = authenticated_manager_client.post('/api/v1/delegations/', payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_cannot_delegate_to_self(
        self, authenticated_manager_client, manager
    ):
        """
        Given: Manager trying to delegate to themselves
        When: POST /delegations/
        Then: Returns 400 Bad Request
        """
        payload = {
            'delegate_id': manager.id,
            'start_date': str(date.today()),
            'end_date': str(date.today() + timedelta(days=7)),
        }

        response = authenticated_manager_client.post('/api/v1/delegations/', payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_end_date_must_be_after_start_date(
        self, authenticated_manager_client, user_factory
    ):
        """
        Given: Invalid date range
        When: POST /delegations/
        Then: Returns 400 Bad Request
        """
        from apps.users.models import User

        delegate = user_factory(role=User.Role.MANAGER)
        payload = {
            'delegate_id': delegate.id,
            'start_date': str(date.today()),
            'end_date': str(date.today() - timedelta(days=1)),
        }

        response = authenticated_manager_client.post('/api/v1/delegations/', payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_employee_cannot_create_delegation(
        self, authenticated_client, user_factory
    ):
        """
        Given: Regular employee
        When: POST /delegations/
        Then: Returns 403 Forbidden
        """
        from apps.users.models import User

        delegate = user_factory(role=User.Role.MANAGER)
        payload = {
            'delegate_id': delegate.id,
            'start_date': str(date.today()),
            'end_date': str(date.today() + timedelta(days=7)),
        }

        response = authenticated_client.post('/api/v1/delegations/', payload)

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestRevokeDelegationEndpoint:
    """Tests for DELETE /api/v1/delegations/:id/"""

    def test_manager_can_revoke_own_delegation(
        self, authenticated_manager_client, manager, user_factory
    ):
        """
        Given: Manager with active delegation
        When: DELETE /delegations/:id/
        Then: Returns 204 and delegation is removed
        """
        from apps.users.models import User

        delegate = user_factory(role=User.Role.MANAGER)
        delegation = ApprovalDelegation.objects.create(
            delegator=manager,
            delegate=delegate,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=7),
        )

        response = authenticated_manager_client.delete(f'/api/v1/delegations/{delegation.id}/')

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not ApprovalDelegation.objects.filter(id=delegation.id).exists()

    def test_cannot_revoke_others_delegation(
        self, authenticated_manager_client, user_factory
    ):
        """
        Given: Delegation owned by another manager
        When: DELETE /delegations/:id/
        Then: Returns 404 Not Found
        """
        from apps.users.models import User

        other_manager = user_factory(role=User.Role.MANAGER)
        delegate = user_factory(role=User.Role.MANAGER)
        delegation = ApprovalDelegation.objects.create(
            delegator=other_manager,
            delegate=delegate,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=7),
        )

        response = authenticated_manager_client.delete(f'/api/v1/delegations/{delegation.id}/')

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert ApprovalDelegation.objects.filter(id=delegation.id).exists()


@pytest.mark.django_db
class TestDelegatedApprovalWorkflow:
    """Tests for delegated approval behavior."""

    def test_delegate_can_approve_delegators_timesheets(
        self, api_client, manager, user, user_factory, timesheet_factory
    ):
        """
        Given: Active delegation from manager to delegate
        When: Delegate approves timesheet of manager's report
        Then: Approval succeeds
        """
        from rest_framework_simplejwt.tokens import RefreshToken
        from apps.users.models import User

        delegate = user_factory(role=User.Role.MANAGER)
        ApprovalDelegation.objects.create(
            delegator=manager,
            delegate=delegate,
            start_date=date.today() - timedelta(days=1),
            end_date=date.today() + timedelta(days=7),
        )

        timesheet = timesheet_factory(user=user, status=Timesheet.Status.SUBMITTED)

        refresh = RefreshToken.for_user(delegate)
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        response = api_client.post(f'/api/v1/timesheets/{timesheet.id}/approve/')

        assert response.status_code == status.HTTP_200_OK
        timesheet.refresh_from_db()
        assert timesheet.status == Timesheet.Status.APPROVED
        assert timesheet.approved_by == delegate

    def test_expired_delegation_does_not_grant_access(
        self, api_client, manager, user, user_factory, timesheet_factory
    ):
        """
        Given: Expired delegation
        When: Former delegate tries to approve timesheet
        Then: Returns 403 Forbidden
        """
        from rest_framework_simplejwt.tokens import RefreshToken
        from apps.users.models import User

        delegate = user_factory(role=User.Role.MANAGER)
        ApprovalDelegation.objects.create(
            delegator=manager,
            delegate=delegate,
            start_date=date.today() - timedelta(days=14),
            end_date=date.today() - timedelta(days=7),
        )

        timesheet = timesheet_factory(user=user, status=Timesheet.Status.SUBMITTED)

        refresh = RefreshToken.for_user(delegate)
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        response = api_client.post(f'/api/v1/timesheets/{timesheet.id}/approve/')

        assert response.status_code == status.HTTP_403_FORBIDDEN
