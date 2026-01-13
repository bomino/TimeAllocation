"""
Root pytest configuration for TimeTrack Pro.

Contains shared fixtures used across all test modules.
"""
import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
from rest_framework.test import APIClient
import pytz

from apps.infrastructure.clock import TestClock, set_clock, reset_clock


@pytest.fixture(autouse=True)
def reset_clock_after_test():
    """Reset clock after each test to prevent test pollution."""
    yield
    reset_clock()


@pytest.fixture(autouse=True)
def mock_celery_tasks():
    """
    Mock all Celery task.delay() calls to prevent broker connection.

    Per TDD plan: "Test by mocking task.delay() calls"
    """
    with patch('apps.timesheets.tasks.send_timesheet_submitted_notification.delay') as mock_submitted, \
         patch('apps.timesheets.tasks.send_timesheet_approved_notification.delay') as mock_approved, \
         patch('apps.timesheets.tasks.send_timesheet_rejected_notification.delay') as mock_rejected:
        yield {
            'submitted': mock_submitted,
            'approved': mock_approved,
            'rejected': mock_rejected,
        }


@pytest.fixture
def api_client():
    """Unauthenticated DRF API client."""
    return APIClient()


@pytest.fixture
def test_clock():
    """
    Injectable test clock with time travel capabilities.

    Default time: 2024-01-15 12:00:00 UTC
    """
    clock = TestClock(initial=datetime(2024, 1, 15, 12, 0, 0, tzinfo=pytz.UTC))
    set_clock(clock)
    return clock


@pytest.fixture
def authenticated_client(api_client, user):
    """API client authenticated as default user."""
    from rest_framework_simplejwt.tokens import RefreshToken

    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.fixture
def authenticated_manager_client(api_client, manager):
    """API client authenticated as manager."""
    from rest_framework_simplejwt.tokens import RefreshToken

    refresh = RefreshToken.for_user(manager)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.fixture
def authenticated_admin_client(api_client, admin):
    """API client authenticated as admin."""
    from rest_framework_simplejwt.tokens import RefreshToken

    refresh = RefreshToken.for_user(admin)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.fixture
def company(db):
    """Default test company."""
    from apps.companies.factories import CompanyFactory
    return CompanyFactory()


@pytest.fixture
def company_settings(company):
    """Company settings for the default company."""
    from apps.companies.factories import CompanySettingsFactory
    return CompanySettingsFactory(company=company)


@pytest.fixture
def user_factory(db, company):
    """Factory function for creating users."""
    from apps.users.factories import UserFactory

    def create(**kwargs):
        kwargs.setdefault('company', company)
        return UserFactory(**kwargs)

    return create


@pytest.fixture
def user(user_factory):
    """Default test user (employee role)."""
    return user_factory()


@pytest.fixture
def manager(user_factory, user):
    """Manager who manages the default user."""
    from apps.users.models import User

    mgr = user_factory(role=User.Role.MANAGER)
    user.manager = mgr
    user.save()
    return mgr


@pytest.fixture
def admin(user_factory):
    """Admin user."""
    from apps.users.models import User
    return user_factory(role=User.Role.ADMIN)


@pytest.fixture
def company_factory(db):
    """Factory function for creating companies."""
    from apps.companies.factories import CompanyFactory

    def create(**kwargs):
        return CompanyFactory(**kwargs)

    return create


@pytest.fixture
def project_factory(db, company):
    """Factory function for creating projects."""
    from apps.projects.factories import ProjectFactory

    def create(**kwargs):
        kwargs.setdefault('company', company)
        return ProjectFactory(**kwargs)

    return create


@pytest.fixture
def project(project_factory):
    """Default test project."""
    return project_factory()


@pytest.fixture
def rate_factory(db, company):
    """Factory function for creating rates."""
    from apps.rates.factories import RateFactory

    def create(**kwargs):
        kwargs.setdefault('company', company)
        return RateFactory(**kwargs)

    return create


@pytest.fixture
def time_entry_factory(db, user, project):
    """Factory function for creating time entries."""
    from apps.timeentries.factories import TimeEntryFactory

    def create(**kwargs):
        kwargs.setdefault('user', user)
        kwargs.setdefault('project', project)
        return TimeEntryFactory(**kwargs)

    return create


@pytest.fixture
def timesheet_factory(db, user):
    """Factory function for creating timesheets."""
    from apps.timesheets.factories import TimesheetFactory

    def create(**kwargs):
        kwargs.setdefault('user', user)
        return TimesheetFactory(**kwargs)

    return create
