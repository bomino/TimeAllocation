"""
Tests for Timer API endpoints - TDD approach.

Endpoints:
- POST /api/v1/time-entries/timer/start/
- POST /api/v1/time-entries/timer/stop/
- GET  /api/v1/time-entries/timer/active/

Business rules:
- Only one active timer per user at a time
- Block new timer until current stopped
"""
from datetime import date, datetime, timedelta
from decimal import Decimal
from unittest.mock import patch

import pytest
import pytz
from rest_framework import status


@pytest.mark.django_db
class TestStartTimerEndpoint:
    """Tests for POST /api/v1/time-entries/timer/start/"""

    def test_start_timer_returns_201(self, authenticated_client, user, project):
        """
        Given: No active timer
        When: POST /timer/start/ with project
        Then: Returns 201 with timer entry
        """
        user.company.settings.default_hourly_rate = Decimal('75.00')
        user.company.settings.save()

        response = authenticated_client.post('/api/v1/time-entries/timer/start/', {
            'project': project.id,
        })

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['is_timer_entry'] is True
        assert response.data['timer_started_at'] is not None
        assert response.data['timer_stopped_at'] is None

    def test_start_timer_snapshots_rate(
        self, authenticated_client, user, project, rate_factory
    ):
        """
        Given: Employee-project rate exists
        When: POST /timer/start/
        Then: Rate is snapshotted at timer start
        """
        from apps.rates.models import Rate

        rate_factory(
            company=user.company,
            employee=user,
            project=project,
            rate_type=Rate.RateType.EMPLOYEE_PROJECT,
            hourly_rate=Decimal('125.00'),
            effective_from=date(2024, 1, 1),
        )

        response = authenticated_client.post('/api/v1/time-entries/timer/start/', {
            'project': project.id,
        })

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['billing_rate'] == '125.00'
        assert response.data['rate_source'] == 'EMPLOYEE_PROJECT'

    def test_start_timer_with_active_timer_returns_400(
        self, authenticated_client, user, project
    ):
        """
        Given: User already has an active timer
        When: POST /timer/start/
        Then: Returns 400 (must stop current timer first)
        """
        from apps.timeentries.models import TimeEntry

        TimeEntry.objects.create(
            user=user, project=project, date=date.today(),
            hours=Decimal('0.00'), billing_rate=Decimal('100.00'),
            rate_source=TimeEntry.RateSource.PROJECT,
            is_timer_entry=True,
            timer_started_at=datetime.now(pytz.UTC),
        )

        user.company.settings.default_hourly_rate = Decimal('75.00')
        user.company.settings.save()

        response = authenticated_client.post('/api/v1/time-entries/timer/start/', {
            'project': project.id,
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'active' in str(response.data).lower() or 'timer' in str(response.data).lower()

    def test_start_timer_without_project_returns_400(self, authenticated_client):
        """
        Given: No project specified
        When: POST /timer/start/
        Then: Returns 400 Bad Request
        """
        response = authenticated_client.post('/api/v1/time-entries/timer/start/', {})

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_start_timer_unauthenticated_returns_401(self, api_client, project):
        """
        Given: No authentication
        When: POST /timer/start/
        Then: Returns 401 Unauthorized
        """
        response = api_client.post('/api/v1/time-entries/timer/start/', {
            'project': project.id,
        })

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_start_timer_with_description(self, authenticated_client, user, project):
        """
        Given: Starting a timer with description
        When: POST /timer/start/
        Then: Description is saved
        """
        user.company.settings.default_hourly_rate = Decimal('75.00')
        user.company.settings.save()

        response = authenticated_client.post('/api/v1/time-entries/timer/start/', {
            'project': project.id,
            'description': 'Working on authentication feature',
        })

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['description'] == 'Working on authentication feature'


@pytest.mark.django_db
class TestStopTimerEndpoint:
    """Tests for POST /api/v1/time-entries/timer/stop/"""

    def test_stop_timer_returns_200(self, authenticated_client, user, project):
        """
        Given: User has an active timer
        When: POST /timer/stop/
        Then: Returns 200 with calculated hours
        """
        from apps.timeentries.models import TimeEntry

        start_time = datetime.now(pytz.UTC) - timedelta(hours=2, minutes=30)
        TimeEntry.objects.create(
            user=user, project=project, date=date.today(),
            hours=Decimal('0.00'), billing_rate=Decimal('100.00'),
            rate_source=TimeEntry.RateSource.PROJECT,
            is_timer_entry=True,
            timer_started_at=start_time,
        )

        response = authenticated_client.post('/api/v1/time-entries/timer/stop/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['timer_stopped_at'] is not None
        assert Decimal(response.data['hours']) > Decimal('2.00')

    def test_stop_timer_calculates_hours_correctly(
        self, authenticated_client, user, project
    ):
        """
        Given: Timer started 3 hours 15 minutes ago
        When: POST /timer/stop/
        Then: Hours calculated as 3.25
        """
        from apps.timeentries.models import TimeEntry

        start_time = datetime.now(pytz.UTC) - timedelta(hours=3, minutes=15)
        TimeEntry.objects.create(
            user=user, project=project, date=date.today(),
            hours=Decimal('0.00'), billing_rate=Decimal('100.00'),
            rate_source=TimeEntry.RateSource.PROJECT,
            is_timer_entry=True,
            timer_started_at=start_time,
        )

        response = authenticated_client.post('/api/v1/time-entries/timer/stop/')

        assert response.status_code == status.HTTP_200_OK
        hours = Decimal(response.data['hours'])
        assert Decimal('3.20') <= hours <= Decimal('3.30')

    def test_stop_timer_without_active_timer_returns_400(self, authenticated_client):
        """
        Given: No active timer
        When: POST /timer/stop/
        Then: Returns 400 Bad Request
        """
        response = authenticated_client.post('/api/v1/time-entries/timer/stop/')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'no' in str(response.data).lower() or 'timer' in str(response.data).lower()

    def test_stop_timer_respects_daily_limit(
        self, authenticated_client, user, project
    ):
        """
        Given: User has 22 hours logged, timer running 3+ hours
        When: POST /timer/stop/
        Then: Hours capped at 24h total (2h for this entry)
        """
        from apps.timeentries.models import TimeEntry

        TimeEntry.objects.create(
            user=user, project=project, date=date.today(),
            hours=Decimal('22.00'), billing_rate=Decimal('100.00'),
            rate_source=TimeEntry.RateSource.PROJECT,
        )

        start_time = datetime.now(pytz.UTC) - timedelta(hours=3)
        TimeEntry.objects.create(
            user=user, project=project, date=date.today(),
            hours=Decimal('0.00'), billing_rate=Decimal('100.00'),
            rate_source=TimeEntry.RateSource.PROJECT,
            is_timer_entry=True,
            timer_started_at=start_time,
        )

        response = authenticated_client.post('/api/v1/time-entries/timer/stop/')

        assert response.status_code == status.HTTP_200_OK
        assert Decimal(response.data['hours']) == Decimal('2.00')

    def test_stop_timer_unauthenticated_returns_401(self, api_client):
        """
        Given: No authentication
        When: POST /timer/stop/
        Then: Returns 401 Unauthorized
        """
        response = api_client.post('/api/v1/time-entries/timer/stop/')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_stop_timer_allows_update_description(
        self, authenticated_client, user, project
    ):
        """
        Given: Active timer with no description
        When: POST /timer/stop/ with description
        Then: Description is updated
        """
        from apps.timeentries.models import TimeEntry

        start_time = datetime.now(pytz.UTC) - timedelta(hours=1)
        TimeEntry.objects.create(
            user=user, project=project, date=date.today(),
            hours=Decimal('0.00'), billing_rate=Decimal('100.00'),
            rate_source=TimeEntry.RateSource.PROJECT,
            is_timer_entry=True,
            timer_started_at=start_time,
            description='',
        )

        response = authenticated_client.post('/api/v1/time-entries/timer/stop/', {
            'description': 'Completed authentication feature',
        })

        assert response.status_code == status.HTTP_200_OK
        assert response.data['description'] == 'Completed authentication feature'


@pytest.mark.django_db
class TestGetActiveTimerEndpoint:
    """Tests for GET /api/v1/time-entries/timer/active/"""

    def test_get_active_timer_returns_200(self, authenticated_client, user, project):
        """
        Given: User has an active timer
        When: GET /timer/active/
        Then: Returns 200 with timer details
        """
        from apps.timeentries.models import TimeEntry

        start_time = datetime.now(pytz.UTC) - timedelta(hours=1)
        entry = TimeEntry.objects.create(
            user=user, project=project, date=date.today(),
            hours=Decimal('0.00'), billing_rate=Decimal('100.00'),
            rate_source=TimeEntry.RateSource.PROJECT,
            is_timer_entry=True,
            timer_started_at=start_time,
        )

        response = authenticated_client.get('/api/v1/time-entries/timer/active/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == entry.id
        assert response.data['is_timer_entry'] is True

    def test_get_active_timer_no_timer_returns_404(self, authenticated_client):
        """
        Given: No active timer
        When: GET /timer/active/
        Then: Returns 404
        """
        response = authenticated_client.get('/api/v1/time-entries/timer/active/')

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_active_timer_includes_elapsed_time(
        self, authenticated_client, user, project
    ):
        """
        Given: Timer started 2 hours ago
        When: GET /timer/active/
        Then: Response includes elapsed_hours field
        """
        from apps.timeentries.models import TimeEntry

        start_time = datetime.now(pytz.UTC) - timedelta(hours=2)
        TimeEntry.objects.create(
            user=user, project=project, date=date.today(),
            hours=Decimal('0.00'), billing_rate=Decimal('100.00'),
            rate_source=TimeEntry.RateSource.PROJECT,
            is_timer_entry=True,
            timer_started_at=start_time,
        )

        response = authenticated_client.get('/api/v1/time-entries/timer/active/')

        assert response.status_code == status.HTTP_200_OK
        assert 'elapsed_hours' in response.data
        elapsed = Decimal(response.data['elapsed_hours'])
        assert Decimal('1.90') <= elapsed <= Decimal('2.10')

    def test_get_active_timer_unauthenticated_returns_401(self, api_client):
        """
        Given: No authentication
        When: GET /timer/active/
        Then: Returns 401 Unauthorized
        """
        response = api_client.get('/api/v1/time-entries/timer/active/')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
