"""
Tests for TimeEntry API endpoints - TDD approach.

Endpoints:
- GET    /api/v1/time-entries/
- POST   /api/v1/time-entries/
- GET    /api/v1/time-entries/:id/
- PUT    /api/v1/time-entries/:id/
- DELETE /api/v1/time-entries/:id/
"""
from datetime import date
from decimal import Decimal
from unittest.mock import patch

import pytest
from rest_framework import status


@pytest.mark.django_db
class TestListTimeEntriesEndpoint:
    """Tests for GET /api/v1/time-entries/"""

    def test_list_own_entries_returns_200(self, authenticated_client, user, project):
        """
        Given: An authenticated user with time entries
        When: GET /time-entries/
        Then: Returns 200 with user's entries
        """
        from apps.timeentries.models import TimeEntry

        TimeEntry.objects.create(
            user=user, project=project, date=date(2024, 6, 15),
            hours=Decimal('8.00'), billing_rate=Decimal('100.00'),
            rate_source=TimeEntry.RateSource.PROJECT,
        )

        response = authenticated_client.get('/api/v1/time-entries/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['data']) == 1

    def test_list_only_returns_own_entries(
        self, authenticated_client, user, project, user_factory
    ):
        """
        Given: Multiple users with time entries
        When: User A requests /time-entries/
        Then: Only User A's entries are returned
        """
        from apps.timeentries.models import TimeEntry

        other_user = user_factory()

        TimeEntry.objects.create(
            user=user, project=project, date=date(2024, 6, 15),
            hours=Decimal('8.00'), billing_rate=Decimal('100.00'),
            rate_source=TimeEntry.RateSource.PROJECT,
        )
        TimeEntry.objects.create(
            user=other_user, project=project, date=date(2024, 6, 15),
            hours=Decimal('6.00'), billing_rate=Decimal('100.00'),
            rate_source=TimeEntry.RateSource.PROJECT,
        )

        response = authenticated_client.get('/api/v1/time-entries/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['data']) == 1
        assert response.data['data'][0]['user'] == user.id

    def test_list_entries_unauthenticated_returns_401(self, api_client):
        """
        Given: No authentication
        When: GET /time-entries/
        Then: Returns 401 Unauthorized
        """
        response = api_client.get('/api/v1/time-entries/')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_entries_filter_by_date_range(
        self, authenticated_client, user, project
    ):
        """
        Given: Entries across multiple dates
        When: GET /time-entries/?date_from=X&date_to=Y
        Then: Only entries within range returned
        """
        from apps.timeentries.models import TimeEntry

        TimeEntry.objects.create(
            user=user, project=project, date=date(2024, 6, 10),
            hours=Decimal('8.00'), billing_rate=Decimal('100.00'),
            rate_source=TimeEntry.RateSource.PROJECT,
        )
        TimeEntry.objects.create(
            user=user, project=project, date=date(2024, 6, 15),
            hours=Decimal('8.00'), billing_rate=Decimal('100.00'),
            rate_source=TimeEntry.RateSource.PROJECT,
        )
        TimeEntry.objects.create(
            user=user, project=project, date=date(2024, 6, 20),
            hours=Decimal('8.00'), billing_rate=Decimal('100.00'),
            rate_source=TimeEntry.RateSource.PROJECT,
        )

        response = authenticated_client.get(
            '/api/v1/time-entries/',
            {'date_from': '2024-06-12', 'date_to': '2024-06-18'}
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['data']) == 1

    def test_list_entries_filter_by_project(
        self, authenticated_client, user, project, project_factory
    ):
        """
        Given: Entries on different projects
        When: GET /time-entries/?project=X
        Then: Only entries for that project returned
        """
        from apps.timeentries.models import TimeEntry

        other_project = project_factory()

        TimeEntry.objects.create(
            user=user, project=project, date=date(2024, 6, 15),
            hours=Decimal('8.00'), billing_rate=Decimal('100.00'),
            rate_source=TimeEntry.RateSource.PROJECT,
        )
        TimeEntry.objects.create(
            user=user, project=other_project, date=date(2024, 6, 15),
            hours=Decimal('6.00'), billing_rate=Decimal('100.00'),
            rate_source=TimeEntry.RateSource.PROJECT,
        )

        response = authenticated_client.get(
            '/api/v1/time-entries/',
            {'project': project.id}
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['data']) == 1
        assert response.data['data'][0]['project'] == project.id


@pytest.mark.django_db
class TestCreateTimeEntryEndpoint:
    """Tests for POST /api/v1/time-entries/"""

    def test_create_entry_with_valid_data(self, authenticated_client, user, project):
        """
        Given: An authenticated user
        When: POST /time-entries/ with valid data
        Then: Returns 201 and creates entry with snapshotted rate
        """
        user.company.settings.default_hourly_rate = Decimal('75.00')
        user.company.settings.save()

        response = authenticated_client.post('/api/v1/time-entries/', {
            'project': project.id,
            'date': '2024-06-15',
            'hours': '8.00',
            'description': 'Worked on feature X',
        })

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['billing_rate'] == '75.00'
        assert response.data['rate_source'] == 'COMPANY'

    def test_create_entry_uses_employee_project_rate_if_exists(
        self, authenticated_client, user, project, rate_factory
    ):
        """
        Given: Employee-project rate exists
        When: POST /time-entries/
        Then: Uses employee-project rate
        """
        from apps.rates.models import Rate

        rate_factory(
            company=user.company,
            employee=user,
            project=project,
            rate_type=Rate.RateType.EMPLOYEE_PROJECT,
            hourly_rate=Decimal('150.00'),
            effective_from=date(2024, 1, 1),
        )

        response = authenticated_client.post('/api/v1/time-entries/', {
            'project': project.id,
            'date': '2024-06-15',
            'hours': '4.00',
        })

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['billing_rate'] == '150.00'
        assert response.data['rate_source'] == 'EMPLOYEE_PROJECT'

    def test_create_entry_without_project_returns_400(self, authenticated_client):
        """
        Given: Missing project field
        When: POST /time-entries/
        Then: Returns 400 Bad Request
        """
        response = authenticated_client.post('/api/v1/time-entries/', {
            'date': '2024-06-15',
            'hours': '8.00',
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_entry_without_date_returns_400(
        self, authenticated_client, project
    ):
        """
        Given: Missing date field
        When: POST /time-entries/
        Then: Returns 400 Bad Request
        """
        response = authenticated_client.post('/api/v1/time-entries/', {
            'project': project.id,
            'hours': '8.00',
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_entry_without_hours_returns_400(
        self, authenticated_client, project
    ):
        """
        Given: Missing hours field
        When: POST /time-entries/
        Then: Returns 400 Bad Request
        """
        response = authenticated_client.post('/api/v1/time-entries/', {
            'project': project.id,
            'date': '2024-06-15',
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_entry_with_negative_hours_returns_400(
        self, authenticated_client, project
    ):
        """
        Given: Negative hours
        When: POST /time-entries/
        Then: Returns 400 Bad Request
        """
        response = authenticated_client.post('/api/v1/time-entries/', {
            'project': project.id,
            'date': '2024-06-15',
            'hours': '-2.00',
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_entry_with_zero_hours_returns_400(
        self, authenticated_client, project
    ):
        """
        Given: Zero hours
        When: POST /time-entries/
        Then: Returns 400 Bad Request
        """
        response = authenticated_client.post('/api/v1/time-entries/', {
            'project': project.id,
            'date': '2024-06-15',
            'hours': '0.00',
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_entry_exceeding_daily_limit_returns_400(
        self, authenticated_client, user, project
    ):
        """
        Given: User already has 20 hours on a date
        When: POST /time-entries/ with 5 more hours
        Then: Returns 400 (would exceed 24h limit)
        """
        from apps.timeentries.models import TimeEntry

        TimeEntry.objects.create(
            user=user, project=project, date=date(2024, 6, 15),
            hours=Decimal('20.00'), billing_rate=Decimal('100.00'),
            rate_source=TimeEntry.RateSource.PROJECT,
        )

        user.company.settings.default_hourly_rate = Decimal('75.00')
        user.company.settings.save()

        response = authenticated_client.post('/api/v1/time-entries/', {
            'project': project.id,
            'date': '2024-06-15',
            'hours': '5.00',
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'daily' in str(response.data).lower() or 'limit' in str(response.data).lower()

    def test_create_entry_at_daily_limit_succeeds(
        self, authenticated_client, user, project
    ):
        """
        Given: User has 20 hours on a date
        When: POST /time-entries/ with 4 more hours (total 24)
        Then: Returns 201 (exactly at limit)
        """
        from apps.timeentries.models import TimeEntry

        TimeEntry.objects.create(
            user=user, project=project, date=date(2024, 6, 15),
            hours=Decimal('20.00'), billing_rate=Decimal('100.00'),
            rate_source=TimeEntry.RateSource.PROJECT,
        )

        user.company.settings.default_hourly_rate = Decimal('75.00')
        user.company.settings.save()

        response = authenticated_client.post('/api/v1/time-entries/', {
            'project': project.id,
            'date': '2024-06-15',
            'hours': '4.00',
        })

        assert response.status_code == status.HTTP_201_CREATED

    def test_create_entry_unauthenticated_returns_401(self, api_client, project):
        """
        Given: No authentication
        When: POST /time-entries/
        Then: Returns 401 Unauthorized
        """
        response = api_client.post('/api/v1/time-entries/', {
            'project': project.id,
            'date': '2024-06-15',
            'hours': '8.00',
        })

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestRetrieveTimeEntryEndpoint:
    """Tests for GET /api/v1/time-entries/:id/"""

    def test_get_own_entry_returns_200(self, authenticated_client, user, project):
        """
        Given: An authenticated user with a time entry
        When: GET /time-entries/:id/
        Then: Returns 200 with entry details
        """
        from apps.timeentries.models import TimeEntry

        entry = TimeEntry.objects.create(
            user=user, project=project, date=date(2024, 6, 15),
            hours=Decimal('8.00'), billing_rate=Decimal('100.00'),
            rate_source=TimeEntry.RateSource.PROJECT,
            description='My work',
        )

        response = authenticated_client.get(f'/api/v1/time-entries/{entry.id}/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == entry.id
        assert response.data['description'] == 'My work'

    def test_get_other_users_entry_returns_404(
        self, authenticated_client, user, project, user_factory
    ):
        """
        Given: User A authenticated
        When: GET /time-entries/:id/ for User B's entry
        Then: Returns 404 (can't access others' entries)
        """
        from apps.timeentries.models import TimeEntry

        other_user = user_factory()
        entry = TimeEntry.objects.create(
            user=other_user, project=project, date=date(2024, 6, 15),
            hours=Decimal('8.00'), billing_rate=Decimal('100.00'),
            rate_source=TimeEntry.RateSource.PROJECT,
        )

        response = authenticated_client.get(f'/api/v1/time-entries/{entry.id}/')

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_nonexistent_entry_returns_404(self, authenticated_client):
        """
        Given: Entry ID that doesn't exist
        When: GET /time-entries/:id/
        Then: Returns 404 Not Found
        """
        response = authenticated_client.get('/api/v1/time-entries/99999/')

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestUpdateTimeEntryEndpoint:
    """Tests for PUT /api/v1/time-entries/:id/"""

    def test_update_own_entry_returns_200(self, authenticated_client, user, project):
        """
        Given: An authenticated user with a time entry
        When: PUT /time-entries/:id/ with new hours/description
        Then: Returns 200 and updates entry
        """
        from apps.timeentries.models import TimeEntry

        entry = TimeEntry.objects.create(
            user=user, project=project, date=date(2024, 6, 15),
            hours=Decimal('8.00'), billing_rate=Decimal('100.00'),
            rate_source=TimeEntry.RateSource.PROJECT,
            description='Original description',
        )

        response = authenticated_client.put(f'/api/v1/time-entries/{entry.id}/', {
            'project': project.id,
            'date': '2024-06-15',
            'hours': '6.00',
            'description': 'Updated description',
        })

        assert response.status_code == status.HTTP_200_OK
        assert response.data['hours'] == '6.00'
        assert response.data['description'] == 'Updated description'

    def test_update_entry_does_not_recalculate_rate(
        self, authenticated_client, user, project
    ):
        """
        Given: Entry with snapshotted rate of $100
        When: PUT /time-entries/:id/ (even if current rate is different)
        Then: Billing rate remains unchanged
        """
        from apps.timeentries.models import TimeEntry

        entry = TimeEntry.objects.create(
            user=user, project=project, date=date(2024, 6, 15),
            hours=Decimal('8.00'), billing_rate=Decimal('100.00'),
            rate_source=TimeEntry.RateSource.PROJECT,
        )

        user.company.settings.default_hourly_rate = Decimal('200.00')
        user.company.settings.save()

        response = authenticated_client.put(f'/api/v1/time-entries/{entry.id}/', {
            'project': project.id,
            'date': '2024-06-15',
            'hours': '4.00',
        })

        assert response.status_code == status.HTTP_200_OK
        assert response.data['billing_rate'] == '100.00'

    def test_update_other_users_entry_returns_404(
        self, authenticated_client, user, project, user_factory
    ):
        """
        Given: User A authenticated
        When: PUT /time-entries/:id/ for User B's entry
        Then: Returns 404
        """
        from apps.timeentries.models import TimeEntry

        other_user = user_factory()
        entry = TimeEntry.objects.create(
            user=other_user, project=project, date=date(2024, 6, 15),
            hours=Decimal('8.00'), billing_rate=Decimal('100.00'),
            rate_source=TimeEntry.RateSource.PROJECT,
        )

        response = authenticated_client.put(f'/api/v1/time-entries/{entry.id}/', {
            'project': project.id,
            'date': '2024-06-15',
            'hours': '4.00',
        })

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_entry_exceeding_daily_limit_returns_400(
        self, authenticated_client, user, project
    ):
        """
        Given: User has 16 hours total (entry1=8, entry2=8)
        When: PUT entry1 to 20 hours (would make total 28)
        Then: Returns 400
        """
        from apps.timeentries.models import TimeEntry

        entry1 = TimeEntry.objects.create(
            user=user, project=project, date=date(2024, 6, 15),
            hours=Decimal('8.00'), billing_rate=Decimal('100.00'),
            rate_source=TimeEntry.RateSource.PROJECT,
        )
        TimeEntry.objects.create(
            user=user, project=project, date=date(2024, 6, 15),
            hours=Decimal('8.00'), billing_rate=Decimal('100.00'),
            rate_source=TimeEntry.RateSource.PROJECT,
        )

        response = authenticated_client.put(f'/api/v1/time-entries/{entry1.id}/', {
            'project': project.id,
            'date': '2024-06-15',
            'hours': '20.00',
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestDeleteTimeEntryEndpoint:
    """Tests for DELETE /api/v1/time-entries/:id/"""

    def test_delete_own_entry_returns_204(self, authenticated_client, user, project):
        """
        Given: An authenticated user with a time entry
        When: DELETE /time-entries/:id/
        Then: Returns 204 and entry is deleted
        """
        from apps.timeentries.models import TimeEntry

        entry = TimeEntry.objects.create(
            user=user, project=project, date=date(2024, 6, 15),
            hours=Decimal('8.00'), billing_rate=Decimal('100.00'),
            rate_source=TimeEntry.RateSource.PROJECT,
        )
        entry_id = entry.id

        response = authenticated_client.delete(f'/api/v1/time-entries/{entry_id}/')

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not TimeEntry.objects.filter(id=entry_id).exists()

    def test_delete_other_users_entry_returns_404(
        self, authenticated_client, user, project, user_factory
    ):
        """
        Given: User A authenticated
        When: DELETE /time-entries/:id/ for User B's entry
        Then: Returns 404
        """
        from apps.timeentries.models import TimeEntry

        other_user = user_factory()
        entry = TimeEntry.objects.create(
            user=other_user, project=project, date=date(2024, 6, 15),
            hours=Decimal('8.00'), billing_rate=Decimal('100.00'),
            rate_source=TimeEntry.RateSource.PROJECT,
        )

        response = authenticated_client.delete(f'/api/v1/time-entries/{entry.id}/')

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_nonexistent_entry_returns_404(self, authenticated_client):
        """
        Given: Entry ID that doesn't exist
        When: DELETE /time-entries/:id/
        Then: Returns 404
        """
        response = authenticated_client.delete('/api/v1/time-entries/99999/')

        assert response.status_code == status.HTTP_404_NOT_FOUND
