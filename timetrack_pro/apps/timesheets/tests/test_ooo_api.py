"""
Tests for OOO Period API endpoints - TDD approach.

Endpoints:
- GET    /api/v1/ooo-periods/
- POST   /api/v1/ooo-periods/
- DELETE /api/v1/ooo-periods/:id/
"""
from datetime import date, timedelta

import pytest
from rest_framework import status

from apps.timesheets.models import OOOPeriod


@pytest.mark.django_db
class TestListOOOPeriodsEndpoint:
    """Tests for GET /api/v1/ooo-periods/"""

    def test_list_own_ooo_periods_returns_200(self, authenticated_client, user):
        """
        Given: An authenticated user with OOO periods
        When: GET /ooo-periods/
        Then: Returns 200 with user's OOO periods
        """
        OOOPeriod.objects.create(
            user=user,
            start_date=date.today() - timedelta(days=5),
            end_date=date.today() + timedelta(days=5),
        )

        response = authenticated_client.get('/api/v1/ooo-periods/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['data']) == 1

    def test_list_only_returns_own_ooo_periods(
        self, authenticated_client, user, user_factory
    ):
        """
        Given: Multiple users with OOO periods
        When: User A requests /ooo-periods/
        Then: Only User A's OOO periods are returned
        """
        other_user = user_factory()

        OOOPeriod.objects.create(
            user=user,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=5),
        )
        OOOPeriod.objects.create(
            user=other_user,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=5),
        )

        response = authenticated_client.get('/api/v1/ooo-periods/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['data']) == 1
        assert response.data['data'][0]['user'] == user.id

    def test_list_ooo_periods_unauthenticated_returns_401(self, api_client):
        """
        Given: No authentication
        When: GET /ooo-periods/
        Then: Returns 401 Unauthorized
        """
        response = api_client.get('/api/v1/ooo-periods/')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_includes_categorized_periods(self, authenticated_client, user):
        """
        Given: User with active, future, and past OOO periods
        When: GET /ooo-periods/
        Then: Response includes all categorized periods
        """
        OOOPeriod.objects.create(
            user=user,
            start_date=date.today() - timedelta(days=5),
            end_date=date.today() + timedelta(days=5),
        )
        OOOPeriod.objects.create(
            user=user,
            start_date=date.today() + timedelta(days=10),
            end_date=date.today() + timedelta(days=15),
        )
        OOOPeriod.objects.create(
            user=user,
            start_date=date.today() - timedelta(days=30),
            end_date=date.today() - timedelta(days=20),
        )

        response = authenticated_client.get('/api/v1/ooo-periods/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['data']) == 3


@pytest.mark.django_db
class TestCreateOOOPeriodEndpoint:
    """Tests for POST /api/v1/ooo-periods/"""

    def test_create_ooo_period_returns_201(self, authenticated_client, user):
        """
        Given: Authenticated user with no OOO periods
        When: POST /ooo-periods/ with valid dates
        Then: Returns 201 with created OOO period
        """
        payload = {
            'start_date': str(date.today() + timedelta(days=10)),
            'end_date': str(date.today() + timedelta(days=15)),
        }

        response = authenticated_client.post('/api/v1/ooo-periods/', payload)

        assert response.status_code == status.HTTP_201_CREATED
        assert OOOPeriod.objects.filter(user=user).count() == 1

    def test_create_ooo_period_fails_if_active_exists(self, authenticated_client, user):
        """
        Given: User with active OOO period
        When: Creating another active OOO period
        Then: Returns 400 with validation error
        """
        OOOPeriod.objects.create(
            user=user,
            start_date=date.today() - timedelta(days=1),
            end_date=date.today() + timedelta(days=5),
        )

        payload = {
            'start_date': str(date.today()),
            'end_date': str(date.today() + timedelta(days=3)),
        }

        response = authenticated_client.post('/api/v1/ooo-periods/', payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'active' in str(response.data).lower()

    def test_create_ooo_period_fails_if_future_exists(self, authenticated_client, user):
        """
        Given: User with active + future OOO periods
        When: Creating another future OOO period
        Then: Returns 400 with validation error
        """
        OOOPeriod.objects.create(
            user=user,
            start_date=date.today() - timedelta(days=1),
            end_date=date.today() + timedelta(days=5),
        )
        OOOPeriod.objects.create(
            user=user,
            start_date=date.today() + timedelta(days=10),
            end_date=date.today() + timedelta(days=15),
        )

        payload = {
            'start_date': str(date.today() + timedelta(days=20)),
            'end_date': str(date.today() + timedelta(days=25)),
        }

        response = authenticated_client.post('/api/v1/ooo-periods/', payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'future' in str(response.data).lower()

    def test_create_ooo_period_requires_valid_dates(self, authenticated_client):
        """
        Given: Authenticated user
        When: POST with end_date before start_date
        Then: Returns 400 with validation error
        """
        payload = {
            'start_date': str(date.today() + timedelta(days=10)),
            'end_date': str(date.today() + timedelta(days=5)),
        }

        response = authenticated_client.post('/api/v1/ooo-periods/', payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_ooo_period_unauthenticated_returns_401(self, api_client):
        """
        Given: No authentication
        When: POST /ooo-periods/
        Then: Returns 401 Unauthorized
        """
        payload = {
            'start_date': str(date.today() + timedelta(days=10)),
            'end_date': str(date.today() + timedelta(days=15)),
        }

        response = api_client.post('/api/v1/ooo-periods/', payload)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestDeleteOOOPeriodEndpoint:
    """Tests for DELETE /api/v1/ooo-periods/:id/"""

    def test_delete_own_ooo_period_returns_204(self, authenticated_client, user):
        """
        Given: User with OOO period
        When: DELETE /ooo-periods/:id/
        Then: Returns 204 and period is deleted
        """
        ooo = OOOPeriod.objects.create(
            user=user,
            start_date=date.today() + timedelta(days=10),
            end_date=date.today() + timedelta(days=15),
        )

        response = authenticated_client.delete(f'/api/v1/ooo-periods/{ooo.id}/')

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not OOOPeriod.objects.filter(id=ooo.id).exists()

    def test_delete_past_ooo_period_fails(self, authenticated_client, user):
        """
        Given: User with past OOO period
        When: DELETE /ooo-periods/:id/
        Then: Returns 400 (cannot delete past periods)
        """
        ooo = OOOPeriod.objects.create(
            user=user,
            start_date=date.today() - timedelta(days=30),
            end_date=date.today() - timedelta(days=20),
        )

        response = authenticated_client.delete(f'/api/v1/ooo-periods/{ooo.id}/')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert OOOPeriod.objects.filter(id=ooo.id).exists()

    def test_delete_other_users_ooo_period_returns_404(
        self, authenticated_client, user, user_factory
    ):
        """
        Given: OOO period belonging to another user
        When: User A tries to delete it
        Then: Returns 404 (not found)
        """
        other_user = user_factory()
        ooo = OOOPeriod.objects.create(
            user=other_user,
            start_date=date.today() + timedelta(days=10),
            end_date=date.today() + timedelta(days=15),
        )

        response = authenticated_client.delete(f'/api/v1/ooo-periods/{ooo.id}/')

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert OOOPeriod.objects.filter(id=ooo.id).exists()

    def test_delete_ooo_period_unauthenticated_returns_401(self, api_client, user):
        """
        Given: No authentication
        When: DELETE /ooo-periods/:id/
        Then: Returns 401 Unauthorized
        """
        ooo = OOOPeriod.objects.create(
            user=user,
            start_date=date.today() + timedelta(days=10),
            end_date=date.today() + timedelta(days=15),
        )

        response = api_client.delete(f'/api/v1/ooo-periods/{ooo.id}/')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert OOOPeriod.objects.filter(id=ooo.id).exists()
