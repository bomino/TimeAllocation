"""
Tests for User Profile API endpoints - TDD approach.

Endpoints:
- GET /api/v1/users/me/
- PUT /api/v1/users/me/
- PATCH /api/v1/users/me/
"""
import pytest
from rest_framework import status


@pytest.mark.django_db
class TestGetProfileEndpoint:
    """Tests for GET /api/v1/users/me/"""

    def test_get_own_profile_returns_200(self, authenticated_client, user):
        """
        Given: An authenticated user
        When: GET /users/me/
        Then: Returns 200 with user profile data
        """
        response = authenticated_client.get('/api/v1/users/me/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == user.email
        assert response.data['first_name'] == user.first_name
        assert response.data['last_name'] == user.last_name

    def test_get_profile_includes_role(self, authenticated_client, user):
        """
        Given: An authenticated user with a role
        When: GET /users/me/
        Then: Response includes role
        """
        response = authenticated_client.get('/api/v1/users/me/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['role'] == user.role

    def test_get_profile_includes_timezone(self, authenticated_client, user):
        """
        Given: An authenticated user
        When: GET /users/me/
        Then: Response includes timezone
        """
        response = authenticated_client.get('/api/v1/users/me/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['timezone'] == user.timezone

    def test_get_profile_includes_notification_settings(self, authenticated_client, user):
        """
        Given: An authenticated user
        When: GET /users/me/
        Then: Response includes notification settings
        """
        response = authenticated_client.get('/api/v1/users/me/')

        assert response.status_code == status.HTTP_200_OK
        assert 'workflow_notifications_enabled' in response.data
        assert 'security_notifications_enabled' in response.data

    def test_get_profile_includes_company(self, authenticated_client, user):
        """
        Given: An authenticated user with a company
        When: GET /users/me/
        Then: Response includes company reference
        """
        response = authenticated_client.get('/api/v1/users/me/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['company'] == user.company.id

    def test_get_profile_includes_timestamps(self, authenticated_client):
        """
        Given: An authenticated user
        When: GET /users/me/
        Then: Response includes created_at and updated_at
        """
        response = authenticated_client.get('/api/v1/users/me/')

        assert response.status_code == status.HTTP_200_OK
        assert 'created_at' in response.data
        assert 'updated_at' in response.data

    def test_unauthenticated_request_returns_401(self, api_client):
        """
        Given: No authentication token
        When: GET /users/me/
        Then: Returns 401 Unauthorized
        """
        response = api_client.get('/api/v1/users/me/')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestUpdateProfileEndpoint:
    """Tests for PUT /api/v1/users/me/"""

    def test_update_profile_with_valid_data(self, authenticated_client, user):
        """
        Given: An authenticated user
        When: PUT /users/me/ with new first_name and last_name
        Then: Returns 200 and updates the profile
        """
        response = authenticated_client.put('/api/v1/users/me/', {
            'first_name': 'Updated',
            'last_name': 'Name',
            'timezone': 'America/New_York',
            'workflow_notifications_enabled': False,
            'security_notifications_enabled': True,
        })

        assert response.status_code == status.HTTP_200_OK
        assert response.data['first_name'] == 'Updated'
        assert response.data['last_name'] == 'Name'

        user.refresh_from_db()
        assert user.first_name == 'Updated'
        assert user.last_name == 'Name'

    def test_update_timezone_succeeds(self, authenticated_client, user):
        """
        Given: An authenticated user
        When: PUT /users/me/ with valid timezone
        Then: Timezone is updated
        """
        response = authenticated_client.put('/api/v1/users/me/', {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'timezone': 'Europe/London',
            'workflow_notifications_enabled': True,
            'security_notifications_enabled': True,
        })

        assert response.status_code == status.HTTP_200_OK
        assert response.data['timezone'] == 'Europe/London'

    def test_update_notification_preferences(self, authenticated_client, user):
        """
        Given: An authenticated user
        When: PUT /users/me/ with changed notification preferences
        Then: Preferences are updated
        """
        response = authenticated_client.put('/api/v1/users/me/', {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'timezone': user.timezone,
            'workflow_notifications_enabled': False,
            'security_notifications_enabled': False,
        })

        assert response.status_code == status.HTTP_200_OK
        assert response.data['workflow_notifications_enabled'] is False
        assert response.data['security_notifications_enabled'] is False

    def test_cannot_update_email(self, authenticated_client, user):
        """
        Given: An authenticated user
        When: PUT /users/me/ trying to change email
        Then: Email remains unchanged (read-only)
        """
        original_email = user.email

        response = authenticated_client.put('/api/v1/users/me/', {
            'email': 'newemail@example.com',
            'first_name': user.first_name,
            'last_name': user.last_name,
            'timezone': user.timezone,
            'workflow_notifications_enabled': True,
            'security_notifications_enabled': True,
        })

        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == original_email

    def test_cannot_update_role(self, authenticated_client, user):
        """
        Given: An authenticated user with EMPLOYEE role
        When: PUT /users/me/ trying to change role to ADMIN
        Then: Role remains unchanged (read-only)
        """
        from apps.users.models import User

        response = authenticated_client.put('/api/v1/users/me/', {
            'role': User.Role.ADMIN,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'timezone': user.timezone,
            'workflow_notifications_enabled': True,
            'security_notifications_enabled': True,
        })

        assert response.status_code == status.HTTP_200_OK
        assert response.data['role'] == User.Role.EMPLOYEE

    def test_cannot_update_company(self, authenticated_client, user, company):
        """
        Given: An authenticated user
        When: PUT /users/me/ trying to change company
        Then: Company remains unchanged (read-only)
        """
        from apps.companies.factories import CompanyFactory

        other_company = CompanyFactory()
        original_company_id = user.company.id

        response = authenticated_client.put('/api/v1/users/me/', {
            'company': other_company.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'timezone': user.timezone,
            'workflow_notifications_enabled': True,
            'security_notifications_enabled': True,
        })

        assert response.status_code == status.HTTP_200_OK
        assert response.data['company'] == original_company_id

    def test_unauthenticated_request_returns_401(self, api_client):
        """
        Given: No authentication token
        When: PUT /users/me/
        Then: Returns 401 Unauthorized
        """
        response = api_client.put('/api/v1/users/me/', {
            'first_name': 'Test',
            'last_name': 'User',
        })

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestPartialUpdateProfileEndpoint:
    """Tests for PATCH /api/v1/users/me/"""

    def test_partial_update_first_name_only(self, authenticated_client, user):
        """
        Given: An authenticated user
        When: PATCH /users/me/ with only first_name
        Then: Only first_name is updated, other fields unchanged
        """
        original_last_name = user.last_name

        response = authenticated_client.patch('/api/v1/users/me/', {
            'first_name': 'NewFirst',
        })

        assert response.status_code == status.HTTP_200_OK
        assert response.data['first_name'] == 'NewFirst'
        assert response.data['last_name'] == original_last_name

    def test_partial_update_timezone_only(self, authenticated_client, user):
        """
        Given: An authenticated user
        When: PATCH /users/me/ with only timezone
        Then: Only timezone is updated
        """
        response = authenticated_client.patch('/api/v1/users/me/', {
            'timezone': 'Asia/Tokyo',
        })

        assert response.status_code == status.HTTP_200_OK
        assert response.data['timezone'] == 'Asia/Tokyo'

    def test_partial_update_notifications_only(self, authenticated_client, user):
        """
        Given: An authenticated user
        When: PATCH /users/me/ with only notification settings
        Then: Only notification settings are updated
        """
        response = authenticated_client.patch('/api/v1/users/me/', {
            'workflow_notifications_enabled': False,
        })

        assert response.status_code == status.HTTP_200_OK
        assert response.data['workflow_notifications_enabled'] is False

    def test_partial_update_cannot_change_readonly_fields(self, authenticated_client, user):
        """
        Given: An authenticated user
        When: PATCH /users/me/ with read-only fields
        Then: Read-only fields remain unchanged
        """
        from apps.users.models import User

        response = authenticated_client.patch('/api/v1/users/me/', {
            'email': 'hacker@evil.com',
            'role': User.Role.ADMIN,
        })

        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == user.email
        assert response.data['role'] == user.role


@pytest.mark.django_db
class TestProfilePermissions:
    """Tests for profile access permissions."""

    def test_user_can_only_see_own_profile(self, authenticated_client, user_factory):
        """
        Given: Two users A and B
        When: User A requests /users/me/
        Then: Only sees their own profile, not user B's
        """
        other_user = user_factory()

        response = authenticated_client.get('/api/v1/users/me/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] != other_user.email

    def test_manager_sees_own_profile_not_reports(self, authenticated_manager_client, user, manager):
        """
        Given: A manager with direct reports
        When: Manager requests /users/me/
        Then: Sees own profile, not direct reports
        """
        response = authenticated_manager_client.get('/api/v1/users/me/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == manager.email
        assert response.data['email'] != user.email

    def test_admin_sees_own_profile(self, authenticated_admin_client, admin):
        """
        Given: An admin user
        When: Admin requests /users/me/
        Then: Sees own profile
        """
        response = authenticated_admin_client.get('/api/v1/users/me/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == admin.email
