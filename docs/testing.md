# Testing Guide

This guide documents the testing patterns, conventions, and best practices for TimeTrack Pro.

---

## Table of Contents

1. [Overview](#overview)
2. [Test Patterns](#test-patterns)
3. [Fixtures & Factories](#fixtures--factories)
4. [Clock Service](#clock-service)
5. [Celery Task Testing](#celery-task-testing)
6. [Permission Testing](#permission-testing)
7. [Database Considerations](#database-considerations)
8. [Coverage Requirements](#coverage-requirements)

---

## Overview

### Test Stack

| Tool | Purpose |
|------|---------|
| pytest | Test runner |
| pytest-django | Django integration |
| factory_boy | Test data factories |
| Faker | Realistic test data |
| coverage | Code coverage |

### Running Tests

```bash
# Run all tests
pytest

# Run tests for a specific app
pytest apps/users/

# Run with coverage report
pytest --cov=apps --cov-report=term-missing

# Run specific test class
pytest apps/users/tests/test_views.py::TestUserProfileAPI

# Run tests in parallel (if pytest-xdist installed)
pytest -n auto
```

---

## Test Patterns

We use two complementary test patterns. Each app should include examples of both.

### 1. CRUD Pattern

Use for straightforward API endpoint testing.

**Naming Convention:**
- `test_<action>_returns_<status>`
- `test_<action>_with_<condition>_<result>`

**Example:**

```python
class TestUserProfileAPI:
    """Tests for /api/v1/users/me/ endpoint."""

    def test_get_own_profile_returns_200(self, authenticated_client, user):
        """GET /users/me/ returns authenticated user's profile."""
        response = authenticated_client.get('/api/v1/users/me/')

        assert response.status_code == 200
        assert response.data['email'] == user.email
        assert response.data['timezone'] == user.timezone

    def test_update_profile_timezone_succeeds(self, authenticated_client):
        """PUT /users/me/ with valid timezone updates user."""
        response = authenticated_client.put('/api/v1/users/me/', {
            'timezone': 'America/New_York'
        })

        assert response.status_code == 200
        assert response.data['timezone'] == 'America/New_York'

    def test_update_profile_invalid_timezone_returns_400(self, authenticated_client):
        """PUT /users/me/ with invalid timezone returns validation error."""
        response = authenticated_client.put('/api/v1/users/me/', {
            'timezone': 'Invalid/Timezone'
        })

        assert response.status_code == 400
        assert 'timezone' in response.data['error']['details']

    def test_unauthenticated_request_returns_401(self, api_client):
        """GET /users/me/ without token returns 401."""
        response = api_client.get('/api/v1/users/me/')

        assert response.status_code == 401
```

### 2. BDD Pattern

Use for complex business scenarios where the story matters.

**Naming Convention:**
- `test_given_<context>_when_<action>_then_<outcome>`

**Structure:**
- Docstring describes the scenario in Given/When/Then format
- Test body mirrors the docstring structure

**Example:**

```python
class TestTimesheetApprovalScenarios:
    """Business scenario tests for timesheet approval workflow."""

    def test_given_submitted_timesheet_when_manager_approves_then_status_changes(
        self, authenticated_manager_client, submitted_timesheet
    ):
        """
        Given: A timesheet in 'submitted' status
        When: The employee's manager approves it
        Then: Status changes to 'approved' and approved_at is set
        """
        response = authenticated_manager_client.post(
            f'/api/v1/timesheets/{submitted_timesheet.id}/approve/'
        )

        assert response.status_code == 200
        assert response.data['status'] == 'APPROVED'
        assert response.data['approved_at'] is not None

    def test_given_pending_3_days_when_manager_ooo_then_escalates_to_skip_manager(
        self, test_clock, submitted_timesheet, manager, skip_manager, ooo_period_factory
    ):
        """
        Given: A timesheet pending approval for 3 days
        And: The manager is marked as out-of-office
        When: The escalation job runs
        Then: The timesheet is assigned to the skip-level manager
        """
        # Setup: Create OOO period for manager
        ooo_period_factory(user=manager, start_date=test_clock.now().date())

        # Setup: Advance time past escalation threshold
        test_clock.advance(timedelta(days=3))

        # Action: Trigger escalation check
        from apps.timesheets.tasks import check_escalations
        check_escalations()

        # Assert: Timesheet reassigned
        submitted_timesheet.refresh_from_db()
        assert submitted_timesheet.pending_approver == skip_manager

    def test_given_rate_change_when_new_entry_created_then_uses_new_rate(
        self, authenticated_client, project, rate_factory, test_clock
    ):
        """
        Given: An employee-project rate of $100/hr effective Jan 1
        And: A new rate of $125/hr effective Feb 1
        When: Employee creates entry on Feb 15
        Then: Entry snapshots the $125 rate
        """
        # Setup: Old rate
        rate_factory(
            project=project,
            hourly_rate=Decimal('100.00'),
            effective_from=date(2024, 1, 1),
            effective_to=date(2024, 1, 31)
        )

        # Setup: New rate
        rate_factory(
            project=project,
            hourly_rate=Decimal('125.00'),
            effective_from=date(2024, 2, 1)
        )

        # Action: Create entry in February
        test_clock.travel_to(datetime(2024, 2, 15, 12, 0, 0))
        response = authenticated_client.post('/api/v1/time-entries/', {
            'project_id': project.id,
            'date': '2024-02-15',
            'hours': '8.00',
            'description': 'Development work'
        })

        # Assert: Uses new rate
        assert response.status_code == 201
        assert response.data['billing_rate'] == '125.00'
```

---

## Fixtures & Factories

### Factory Organization

Each app has its own `factories.py` file. Cross-app imports are allowed.

```python
# apps/users/factories.py
import factory
from faker import Faker
from apps.users.models import User

fake = Faker()

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.LazyAttribute(lambda _: fake.email())
    username = factory.LazyAttribute(lambda o: o.email)
    first_name = factory.LazyAttribute(lambda _: fake.first_name())
    last_name = factory.LazyAttribute(lambda _: fake.last_name())
    password = factory.PostGenerationMethodCall('set_password', 'ValidPass1!')
    role = User.Role.EMPLOYEE
    timezone = 'UTC'

    @factory.lazy_attribute
    def company(self):
        from apps.companies.factories import CompanyFactory
        return CompanyFactory()
```

### Pytest Fixtures

```python
# conftest.py (root level)
import pytest
from rest_framework.test import APIClient
from apps.infrastructure.clock import TestClock

@pytest.fixture
def api_client():
    """Unauthenticated DRF API client."""
    return APIClient()

@pytest.fixture
def test_clock():
    """Injectable test clock with time travel."""
    from datetime import datetime
    return TestClock(initial=datetime(2024, 1, 15, 12, 0, 0, tzinfo=pytz.UTC))

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
```

### Factory Fixtures Pattern

```python
# apps/users/conftest.py
import pytest
from apps.users.factories import UserFactory

@pytest.fixture
def user_factory(db, company):
    """Factory function for creating users."""
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
    mgr = user_factory(role=User.Role.MANAGER)
    user.manager = mgr
    user.save()
    return mgr

@pytest.fixture
def admin(user_factory):
    """Admin user."""
    return user_factory(role=User.Role.ADMIN)
```

---

## Clock Service

The clock service enables deterministic time-based testing.

### Injection Pattern

```python
# In views/services that need current time
from apps.infrastructure.clock import get_clock

class TimeEntryViewSet(viewsets.ModelViewSet):
    def perform_create(self, serializer):
        clock = get_clock()
        serializer.save(
            user=self.request.user,
            created_at=clock.now()
        )
```

### Test Usage

```python
class TestEscalationLogic:
    def test_escalation_after_3_days(self, test_clock, submitted_timesheet, company_settings):
        """Timesheets escalate after configured number of days."""
        company_settings.escalation_days = 3
        company_settings.save()

        # Initial state: Day 0
        test_clock.travel_to(datetime(2024, 1, 15, 9, 0, 0, tzinfo=pytz.UTC))

        # Advance 2 days - should NOT escalate yet
        test_clock.advance(timedelta(days=2))
        check_escalations(clock=test_clock)
        submitted_timesheet.refresh_from_db()
        assert submitted_timesheet.escalated is False

        # Advance 1 more day (total 3) - should escalate
        test_clock.advance(timedelta(days=1))
        check_escalations(clock=test_clock)
        submitted_timesheet.refresh_from_db()
        assert submitted_timesheet.escalated is True

    def test_rate_effective_date_boundaries(self, test_clock, rate_factory, project, user):
        """Rate resolver respects effective date boundaries."""
        # Rate valid Jan 1 - Jan 31
        rate_factory(
            project=project,
            hourly_rate=Decimal('100.00'),
            effective_from=date(2024, 1, 1),
            effective_to=date(2024, 1, 31)
        )

        resolver = RateResolver(test_clock)

        # Jan 15: Should find rate
        test_clock.travel_to(datetime(2024, 1, 15, tzinfo=pytz.UTC))
        rate, _ = resolver.resolve(user.id, project.id)
        assert rate == Decimal('100.00')

        # Feb 1: Should NOT find rate (expired)
        test_clock.travel_to(datetime(2024, 2, 1, tzinfo=pytz.UTC))
        rate, source = resolver.resolve(user.id, project.id)
        assert source == Rate.Type.COMPANY  # Fell back to default
```

---

## Celery Task Testing

All Celery tasks are tested by mocking `task.delay()`.

### Pattern

```python
from unittest.mock import patch

class TestTimesheetNotifications:
    @patch('apps.infrastructure.notifications.send_notification.delay')
    def test_approval_sends_notification(self, mock_send, authenticated_manager_client, submitted_timesheet):
        """Approving timesheet queues notification to employee."""
        response = authenticated_manager_client.post(
            f'/api/v1/timesheets/{submitted_timesheet.id}/approve/'
        )

        assert response.status_code == 200
        mock_send.assert_called_once()

        # Verify call arguments
        call_args = mock_send.call_args
        assert call_args[0][0] == submitted_timesheet.user.id  # user_id
        assert call_args[0][1] == 'timesheet_approved'  # notification_type

    @patch('apps.infrastructure.notifications.send_notification.delay')
    def test_rejection_sends_notification_with_comments(self, mock_send, authenticated_manager_client, submitted_timesheet):
        """Rejecting timesheet queues notification with rejection reason."""
        response = authenticated_manager_client.post(
            f'/api/v1/timesheets/{submitted_timesheet.id}/reject/',
            {'reason': 'Missing project codes on 3 entries'}
        )

        assert response.status_code == 200
        mock_send.assert_called_once()

        # Verify context includes rejection reason
        call_args = mock_send.call_args
        context = call_args[0][2]  # Third positional arg
        assert 'Missing project codes' in context['reason']
```

### Testing Task Logic Directly

For unit testing task internals (not the queueing):

```python
class TestNotificationTaskLogic:
    def test_workflow_notification_respects_user_preference(self, user):
        """Workflow notifications are skipped when user opts out."""
        user.workflow_notifications_enabled = False
        user.save()

        with patch('django.core.mail.send_mail') as mock_mail:
            # Import and call task function directly (not .delay())
            from apps.infrastructure.notifications import send_notification
            send_notification(user.id, 'timesheet_approved', {})

            mock_mail.assert_not_called()

    def test_security_notification_ignores_preference(self, user):
        """Security notifications are always sent regardless of preference."""
        user.workflow_notifications_enabled = False
        user.security_notifications_enabled = False
        user.save()

        with patch('django.core.mail.send_mail') as mock_mail:
            from apps.infrastructure.notifications import send_notification
            send_notification(user.id, 'password_reset', {'token': 'abc123'})

            mock_mail.assert_called_once()
```

---

## Permission Testing

Every role × action combination needs an explicit test proving unauthorized access returns 403.

### Pattern

```python
class TestTimesheetPermissions:
    """Explicit permission denial tests for timesheet endpoints."""

    # Employee permissions
    def test_employee_cannot_approve_own_timesheet(self, authenticated_client, submitted_timesheet):
        """Employees cannot approve their own timesheets."""
        response = authenticated_client.post(
            f'/api/v1/timesheets/{submitted_timesheet.id}/approve/'
        )
        assert response.status_code == 403

    def test_employee_cannot_view_other_employee_timesheet(self, authenticated_client, user_factory):
        """Employees cannot view other employees' timesheets."""
        other_user = user_factory()
        other_timesheet = TimesheetFactory(user=other_user)

        response = authenticated_client.get(
            f'/api/v1/timesheets/{other_timesheet.id}/'
        )
        assert response.status_code == 403

    # Manager permissions
    def test_manager_cannot_approve_non_direct_report(self, authenticated_manager_client, user_factory):
        """Managers can only approve their direct reports' timesheets."""
        other_employee = user_factory()  # Not managed by this manager
        timesheet = TimesheetFactory(user=other_employee, status=Timesheet.Status.SUBMITTED)

        response = authenticated_manager_client.post(
            f'/api/v1/timesheets/{timesheet.id}/approve/'
        )
        assert response.status_code == 403

    def test_manager_cannot_unlock_timesheet(self, authenticated_manager_client, approved_timesheet):
        """Only admins can unlock approved timesheets."""
        response = authenticated_manager_client.post(
            f'/api/v1/timesheets/{approved_timesheet.id}/unlock/',
            {'reason': 'Need to fix entry'}
        )
        assert response.status_code == 403

    # Admin permissions
    def test_admin_can_unlock_timesheet(self, authenticated_admin_client, approved_timesheet):
        """Admins can unlock approved timesheets."""
        response = authenticated_admin_client.post(
            f'/api/v1/timesheets/{approved_timesheet.id}/unlock/',
            {'reason': 'Correction requested by finance'}
        )
        assert response.status_code == 200
```

### Parameterized Permission Matrix

For comprehensive coverage:

```python
import pytest

class TestEndpointPermissions:
    """Parameterized permission tests across all roles."""

    @pytest.mark.parametrize('role,endpoint,method,expected_status', [
        # Employees
        (User.Role.EMPLOYEE, '/api/v1/users/', 'GET', 403),
        (User.Role.EMPLOYEE, '/api/v1/users/me/', 'GET', 200),
        (User.Role.EMPLOYEE, '/api/v1/timesheets/', 'GET', 200),  # Own only
        (User.Role.EMPLOYEE, '/api/v1/timesheets/{id}/approve/', 'POST', 403),

        # Managers
        (User.Role.MANAGER, '/api/v1/users/', 'GET', 403),
        (User.Role.MANAGER, '/api/v1/timesheets/{id}/approve/', 'POST', 200),  # Direct reports
        (User.Role.MANAGER, '/api/v1/timesheets/{id}/unlock/', 'POST', 403),

        # Admins
        (User.Role.ADMIN, '/api/v1/users/', 'GET', 200),
        (User.Role.ADMIN, '/api/v1/timesheets/{id}/unlock/', 'POST', 200),
    ])
    def test_role_permissions(self, api_client, user_factory, role, endpoint, method, expected_status):
        """Verify role-based access control for each endpoint."""
        user = user_factory(role=role)
        # ... setup and assertions
```

---

## Database Considerations

### Always Use PostgreSQL

Tests always run against PostgreSQL to catch database-specific issues:

```python
# config/settings/test.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'timetrack_test',
        'USER': 'test',
        'PASSWORD': 'test',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Transaction Isolation

pytest-django wraps each test in a transaction that rolls back:

```python
@pytest.fixture
def user(db):  # 'db' fixture enables database access
    return UserFactory()
```

### Reusing Test Database

For faster test runs:

```bash
pytest --reuse-db  # Don't recreate database
pytest --create-db  # Force recreate database
```

---

## Coverage Requirements

### Target

- **100% coverage on business logic**: `models.py`, `services.py`
- **80% overall coverage**: Views, serializers can have some gaps

### Running Coverage

```bash
# Terminal report
pytest --cov=apps --cov-report=term-missing

# HTML report
pytest --cov=apps --cov-report=html
open htmlcov/index.html

# Fail if below threshold
pytest --cov=apps --cov-fail-under=80
```

### Coverage Configuration

```ini
# .coveragerc
[run]
source = apps
omit =
    */migrations/*
    */tests/*
    */__init__.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise NotImplementedError
    if TYPE_CHECKING:
```

---

## Quick Reference

### Test File Naming

```
apps/
└── users/
    └── tests/
        ├── __init__.py
        ├── test_models.py      # Model unit tests
        ├── test_views.py       # API endpoint tests
        ├── test_services.py    # Service layer tests
        └── test_permissions.py # Permission denial tests
```

### Common Assertions

```python
# Status codes
assert response.status_code == 200
assert response.status_code == 201  # Created
assert response.status_code == 400  # Bad Request
assert response.status_code == 401  # Unauthorized
assert response.status_code == 403  # Forbidden
assert response.status_code == 404  # Not Found

# Response data
assert response.data['id'] == expected_id
assert 'error' in response.data
assert response.data['error']['code'] == 'BIZ_003'

# Database state
user.refresh_from_db()
assert user.timezone == 'America/New_York'

# Mock assertions
mock_task.assert_called_once()
mock_task.assert_called_with(user.id, 'notification_type', context)
mock_task.assert_not_called()
```

### Test Markers

```python
import pytest

@pytest.mark.slow
def test_heavy_computation():
    """Skip with: pytest -m 'not slow'"""
    pass

@pytest.mark.django_db(transaction=True)
def test_needs_real_transaction():
    """Use real transactions instead of test transaction."""
    pass

@pytest.mark.parametrize('input,expected', [(1, 2), (2, 4)])
def test_doubling(input, expected):
    assert input * 2 == expected
```
