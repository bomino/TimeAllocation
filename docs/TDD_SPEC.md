# TDD Implementation Specification: TimeTrack Pro MVP

**Version:** 1.0
**Scope:** Core-First (Auth + Time Entry + Timesheet)
**Framework:** Django 5.x + Django REST Framework
**Test Framework:** pytest-django + factory_boy + Faker

---

## Table of Contents

1. [Overview](#1-overview)
2. [Interview Decisions](#2-interview-decisions)
3. [Project Structure](#3-project-structure)
4. [Vertical Slices](#4-vertical-slices)
5. [Infrastructure Layer](#5-infrastructure-layer)
6. [Testing Strategy](#6-testing-strategy)
7. [CI/CD Pipeline](#7-cicd-pipeline)
8. [Process & Documentation](#8-process--documentation)
9. [Verification Checklist](#9-verification-checklist)

---

## 1. Overview

### Objective

Build the TimeTrack Pro MVP using strict Test-Driven Development (TDD). The MVP covers three vertical slices:

1. **Auth + Profile** - Authentication stack proof-of-concept
2. **Time Entry + Timer** - Core domain with rate snapshotting
3. **Timesheet + Approval** - Workflow with escalation chain

### Guiding Principles

- **Red-Green-Refactor**: Write failing test first, make it pass, then refactor
- **100% Business Logic Coverage**: All models and services fully tested
- **Vertical Slices**: Build thin end-to-end features, not horizontal layers
- **PostgreSQL Always**: Use real database in tests (Docker)

---

## 2. Interview Decisions

These decisions were gathered through detailed stakeholder interviews and are **binding** for implementation.

### 2.1 Business Logic

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Rate snapshotting | Absolute snapshot at entry creation | Rates never recalculated, ensures billing consistency |
| Timesheet rejection | Line-item conversation | Threaded comments per entry for precise feedback |
| Conversation history | Collapse on approval | Preserved but hidden for clean approved view |
| Daily hour limit | Strict calendar day | 24h max across all projects per calendar day |
| Limit warning | Hierarchical threshold | Company → Project → Employee override chain |
| Threshold override | Admin approval for higher | Can lower freely, exceeding company limit needs admin |
| Timer conflict | Block new timer | Must stop current timer before starting new |
| Approval model | Primary manager | Single manager approves all employee time |
| Delegation | Approval chain with escalation | Auto-escalate when manager unavailable |
| Escalation trigger | Configurable AND/OR | OOO status OR pending X days (company chooses logic) |
| Chain terminus | Notify admin | When no higher manager, notify system admin |
| Unlock window | Configurable days | Company sets max days to unlock after approval |
| Company default rate | Required | Must set default rate at company setup |
| Timesheet lifecycle | Auto-create weekly | Celery cron creates timesheets at week start |
| Week boundary | Configurable per company | Week start day in company timezone |
| Partial submission | Full week only | Cannot submit partial weeks |

### 2.2 Testing Strategy

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Test database | PostgreSQL always | Catches DB-specific issues, matches production |
| Coverage target | 100% business logic | Full coverage on models.py, services.py |
| Contract tests | Combined with behavior | Behavior tests implicitly validate schema |
| Test data | Realistic with Faker | Better readability, realistic edge cases |
| Time mocking | Injected clock service | `now()`, `travel_to()`, `advance()` methods |
| Celery testing | Mock task.delay() | Verify task queued with correct args |
| Rate edge cases | Full coverage | Hierarchy + effective dates + null handling |
| Performance tests | Deferred to post-MVP | Focus on correctness first |
| Fixture organization | Per-app factories | Cross-import allowed between apps |
| Timezone tests | Fixed timezones | UTC, EST, JST for predictable tests |
| Permission tests | Explicit denial tests | Every role × action = 403 test |
| Test patterns | Both CRUD + BDD | Documented examples of each style |

### 2.3 Architecture

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Build order | Vertical slices | End-to-end features, not horizontal layers |
| First slice | Auth + Profile | Proves auth stack works |
| Migrations | Per-slice | Committed with each slice PR |
| Clock service | Dedicated infra app | `apps/infrastructure/` for cross-cutting |
| Infra scope | Full layer | Clock, notifications, file storage |
| Storage | django-storages | Local dev, S3 prod |
| Email | Always Celery | All notifications via background tasks |
| JWT | Direct simplejwt | No wrapper, use library directly |
| Password hashing | Django default | PBKDF2, battle-tested |

### 2.4 Process

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Done criteria | PR template per slice | Checklist ensures completeness |
| PR template naming | Numbered + name | `01_auth.md`, `02_timeentry.md`, etc. |
| Slice boundaries | Iterative refinement | Slice 1 fixed, later slices adjust based on learnings |
| Learning capture | ADR per learning | Custom lightweight format |
| Test docs | Dedicated guide | `docs/testing.md` with patterns |
| Test quantity | Coverage metric only | 100% business logic, not test count |

### 2.5 Data Model Details

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Notification toggles | User model fields | `workflow_notifications_enabled`, `security_notifications_enabled` |
| Company settings | Dedicated table | `CompanySettings` with full audit log |
| OOO model | Date range | `start_date`, `end_date`; max 1 active + 1 future |
| Deactivation | Force approval first | Admin override with export if needed |
| Export format | JSON + base64 CSV | Blob in audit table for compliance |
| Error field paths | Flat field names | Simple `hours`, not `entries/0/hours` |

---

## 3. Project Structure

```
timetrack_pro/
├── config/
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py              # Shared settings
│   │   ├── development.py       # Dev overrides (DEBUG=True)
│   │   ├── production.py        # Prod settings
│   │   └── test.py              # Test settings (PostgreSQL)
│   ├── urls.py                  # Root URL config
│   └── celery.py                # Celery app config
│
├── apps/
│   ├── infrastructure/          # Cross-cutting concerns
│   │   ├── __init__.py
│   │   ├── clock.py             # Clock protocol + implementations
│   │   ├── storage.py           # Storage backend abstraction
│   │   ├── notifications.py     # Email/notification service
│   │   └── tasks.py             # Shared Celery utilities
│   │
│   ├── users/                   # Slice 1
│   │   ├── __init__.py
│   │   ├── models.py            # User, extends AbstractUser
│   │   ├── serializers.py       # DRF serializers
│   │   ├── views.py             # ViewSets
│   │   ├── permissions.py       # IsEmployee, IsManager, IsAdmin
│   │   ├── urls.py              # App URLs
│   │   ├── factories.py         # Test factories
│   │   └── tests/
│   │       ├── __init__.py
│   │       ├── test_models.py
│   │       ├── test_views.py
│   │       └── test_permissions.py
│   │
│   ├── companies/               # Slice 1
│   │   ├── __init__.py
│   │   ├── models.py            # Company, CompanySettings, Audit
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── factories.py
│   │   └── tests/
│   │
│   ├── projects/                # Slice 2
│   │   ├── __init__.py
│   │   ├── models.py            # Project
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── factories.py
│   │   └── tests/
│   │
│   ├── rates/                   # Slice 2
│   │   ├── __init__.py
│   │   ├── models.py            # Rate
│   │   ├── services.py          # RateResolver service
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── factories.py
│   │   └── tests/
│   │       ├── test_models.py
│   │       ├── test_services.py # Rate resolution tests
│   │       └── test_views.py
│   │
│   ├── timeentries/             # Slice 2
│   │   ├── __init__.py
│   │   ├── models.py            # TimeEntry
│   │   ├── serializers.py       # Handles rate snapshotting
│   │   ├── views.py             # Timer start/stop actions
│   │   ├── factories.py
│   │   └── tests/
│   │
│   └── timesheets/              # Slice 3
│       ├── __init__.py
│       ├── models.py            # Timesheet, Comment, OOO, Override
│       ├── services.py          # ApprovalChainService
│       ├── serializers.py
│       ├── views.py
│       ├── tasks.py             # Celery tasks (create weekly, escalate)
│       ├── factories.py
│       └── tests/
│
├── core/                        # Shared utilities
│   ├── __init__.py
│   ├── models.py                # TimeStampedModel base class
│   ├── exceptions.py            # Custom API exceptions
│   └── pagination.py            # Custom pagination classes
│
├── docs/
│   ├── TDD_SPEC.md              # This file
│   ├── testing.md               # Testing patterns guide
│   └── adr/
│       └── 0001-template.md     # ADR template
│
├── .github/
│   ├── workflows/
│   │   └── ci.yml               # GitHub Actions CI
│   └── PULL_REQUEST_TEMPLATE/
│       ├── 01_auth.md
│       ├── 02_timeentry.md
│       └── 03_timesheet.md
│
├── docker-compose.yml           # Postgres + Redis for dev
├── requirements.txt             # Production dependencies
├── requirements-dev.txt         # Dev/test dependencies
├── pytest.ini                   # Pytest configuration
├── pyproject.toml               # Ruff, mypy config
└── manage.py
```

---

## 4. Vertical Slices

### 4.1 Slice 1: Auth + Profile (FIXED)

**Goal:** Prove authentication stack works end-to-end.

#### Models

```python
# apps/users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Role(models.TextChoices):
        EMPLOYEE = 'EMPLOYEE', 'Employee'
        MANAGER = 'MANAGER', 'Manager'
        ADMIN = 'ADMIN', 'Admin'

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.EMPLOYEE)
    manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE)
    timezone = models.CharField(max_length=50, default='UTC')
    workflow_notifications_enabled = models.BooleanField(default=True)
    security_notifications_enabled = models.BooleanField(default=True)

# apps/companies/models.py
class Company(models.Model):
    name = models.CharField(max_length=255)
    week_start_day = models.IntegerField(default=0)  # 0=Monday, 6=Sunday
    timezone = models.CharField(max_length=50, default='UTC')
    default_hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

class CompanySettings(models.Model):
    class EscalationLogic(models.TextChoices):
        AND = 'AND', 'Both conditions'
        OR = 'OR', 'Either condition'

    company = models.OneToOneField(Company, on_delete=models.CASCADE)
    unlock_window_days = models.IntegerField(default=30)
    daily_warning_threshold = models.DecimalField(max_digits=4, decimal_places=2, default=12.0)
    escalation_days = models.IntegerField(default=3)
    escalation_logic = models.CharField(max_length=3, choices=EscalationLogic.choices, default=EscalationLogic.OR)
    updated_at = models.DateTimeField(auto_now=True)

class CompanySettingsAudit(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    changed_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    field_name = models.CharField(max_length=100)
    old_value = models.TextField(null=True)
    new_value = models.TextField()
```

#### API Endpoints

```
POST /api/v1/auth/login/           # Obtain JWT tokens
POST /api/v1/auth/logout/          # Blacklist refresh token
POST /api/v1/auth/refresh/         # Refresh access token
POST /api/v1/auth/password/reset/           # Request reset email
POST /api/v1/auth/password/reset/confirm/   # Complete reset
GET  /api/v1/users/me/             # Get current user profile
PUT  /api/v1/users/me/             # Update current user profile
```

#### Test Cases

```python
# apps/users/tests/test_views.py

# CRUD Pattern Examples
class TestUserProfileAPI:
    """Tests for /api/v1/users/me/ endpoint."""

    def test_get_own_profile_returns_200(self, authenticated_client, user):
        """GET /users/me/ returns authenticated user's profile."""
        response = authenticated_client.get('/api/v1/users/me/')
        assert response.status_code == 200
        assert response.data['email'] == user.email

    def test_update_profile_timezone_succeeds(self, authenticated_client):
        """PUT /users/me/ with valid timezone updates user."""
        response = authenticated_client.put('/api/v1/users/me/', {'timezone': 'America/New_York'})
        assert response.status_code == 200
        assert response.data['timezone'] == 'America/New_York'

    def test_unauthenticated_request_returns_401(self, api_client):
        """GET /users/me/ without token returns 401."""
        response = api_client.get('/api/v1/users/me/')
        assert response.status_code == 401


# BDD Pattern Examples
class TestLoginScenarios:
    """Business scenario tests for authentication."""

    def test_given_valid_credentials_when_login_then_returns_tokens(self, api_client, user_factory):
        """
        Given: A user with email 'test@example.com' and password 'ValidPass1!'
        When: POST /auth/login/ with those credentials
        Then: Response contains access and refresh tokens
        """
        user = user_factory(email='test@example.com', password='ValidPass1!')

        response = api_client.post('/api/v1/auth/login/', {
            'email': 'test@example.com',
            'password': 'ValidPass1!'
        })

        assert response.status_code == 200
        assert 'access' in response.data
        assert 'refresh' in response.data

    def test_given_locked_account_when_login_then_returns_auth_004(self, api_client, user_factory):
        """
        Given: A user whose account is locked
        When: POST /auth/login/ with correct credentials
        Then: Response is 403 with error code AUTH_004
        """
        user = user_factory(is_active=False)

        response = api_client.post('/api/v1/auth/login/', {
            'email': user.email,
            'password': 'ValidPass1!'
        })

        assert response.status_code == 403
        assert response.data['error']['code'] == 'AUTH_004'


# Permission Denial Tests
class TestProfilePermissions:
    """Explicit permission denial tests."""

    def test_employee_cannot_view_other_user_profile(self, authenticated_client, user_factory):
        """Employee role cannot access another user's profile."""
        other_user = user_factory()
        response = authenticated_client.get(f'/api/v1/users/{other_user.id}/')
        assert response.status_code == 403

    def test_employee_cannot_update_other_user_profile(self, authenticated_client, user_factory):
        """Employee role cannot modify another user's profile."""
        other_user = user_factory()
        response = authenticated_client.put(f'/api/v1/users/{other_user.id}/', {'timezone': 'UTC'})
        assert response.status_code == 403
```

#### Acceptance Criteria (PR Checklist)

- [ ] Login endpoint returns access + refresh tokens
- [ ] Logout endpoint blacklists refresh token
- [ ] Token refresh endpoint works
- [ ] Password reset flow sends email (mocked)
- [ ] Password reset confirm updates password
- [ ] GET /users/me/ returns current user
- [ ] PUT /users/me/ updates allowed fields
- [ ] 401 tests for unauthenticated requests
- [ ] 403 tests for unauthorized access
- [ ] All tests pass with PostgreSQL
- [ ] 100% coverage on models.py
- [ ] Migrations committed

---

### 4.2 Slice 2: Time Entry + Timer (To Be Refined)

**Goal:** Implement core domain with rate snapshotting.

#### Models

```python
# apps/projects/models.py
class Project(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        ARCHIVED = 'ARCHIVED', 'Archived'

    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)

# apps/rates/models.py
class Rate(models.Model):
    class Type(models.TextChoices):
        COMPANY = 'COMPANY', 'Company Default'
        EMPLOYEE = 'EMPLOYEE', 'Employee Rate'
        PROJECT = 'PROJECT', 'Project Rate'
        EMPLOYEE_PROJECT = 'EMPLOYEE_PROJECT', 'Employee-Project Rate'

    type = models.CharField(max_length=20, choices=Type.choices)
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE)
    employee = models.ForeignKey('users.User', on_delete=models.CASCADE, null=True, blank=True)
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, null=True, blank=True)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='rates_created')
    created_at = models.DateTimeField(auto_now_add=True)

# apps/timeentries/models.py
class TimeEntry(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE)
    date = models.DateField()
    hours = models.DecimalField(max_digits=4, decimal_places=2)
    description = models.TextField(blank=True)

    # Rate snapshot (immutable after creation)
    billing_rate = models.DecimalField(max_digits=10, decimal_places=2)
    rate_source = models.CharField(max_length=20, choices=Rate.Type.choices)

    # Timer support
    timer_started_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['project', 'date']),
        ]
```

#### Rate Resolution Service

```python
# apps/rates/services.py
from decimal import Decimal
from typing import Optional, Tuple
from django.db.models import Q

class RateResolver:
    """Resolves the effective billing rate for an employee-project combination."""

    def __init__(self, clock):
        self.clock = clock

    def resolve(self, employee_id: int, project_id: int, date=None) -> Tuple[Decimal, str]:
        """
        Resolve rate using hierarchy: employee-project → project → employee → company.

        Returns:
            Tuple of (hourly_rate, rate_source)
        """
        date = date or self.clock.now().date()

        # Try employee-project rate
        rate = self._find_rate(Rate.Type.EMPLOYEE_PROJECT, employee_id, project_id, date)
        if rate:
            return rate.hourly_rate, Rate.Type.EMPLOYEE_PROJECT

        # Try project rate
        rate = self._find_rate(Rate.Type.PROJECT, None, project_id, date)
        if rate:
            return rate.hourly_rate, Rate.Type.PROJECT

        # Try employee rate
        rate = self._find_rate(Rate.Type.EMPLOYEE, employee_id, None, date)
        if rate:
            return rate.hourly_rate, Rate.Type.EMPLOYEE

        # Fall back to company default
        company = Project.objects.get(id=project_id).company
        return company.default_hourly_rate, Rate.Type.COMPANY

    def _find_rate(self, rate_type, employee_id, project_id, date) -> Optional[Rate]:
        filters = Q(type=rate_type, effective_from__lte=date)
        filters &= Q(effective_to__isnull=True) | Q(effective_to__gte=date)

        if employee_id:
            filters &= Q(employee_id=employee_id)
        if project_id:
            filters &= Q(project_id=project_id)

        return Rate.objects.filter(filters).order_by('-effective_from').first()
```

#### API Endpoints

```
GET    /api/v1/time-entries/              # List user's entries
POST   /api/v1/time-entries/              # Create entry (snapshots rate)
GET    /api/v1/time-entries/:id/          # Get entry details
PUT    /api/v1/time-entries/:id/          # Update entry (rate immutable)
DELETE /api/v1/time-entries/:id/          # Delete entry
POST   /api/v1/time-entries/timer/start/  # Start timer
POST   /api/v1/time-entries/timer/stop/   # Stop timer, create entry
GET    /api/v1/rates/effective/:userId/:projectId/  # Get effective rate
```

#### Key Test Cases

```python
# apps/rates/tests/test_services.py
class TestRateResolver:
    """Unit tests for rate resolution service."""

    def test_employee_project_rate_takes_priority(self, rate_factory, user, project, test_clock):
        """Employee-project rate overrides all other rates."""
        rate_factory(type=Rate.Type.COMPANY, hourly_rate=50)
        rate_factory(type=Rate.Type.EMPLOYEE, employee=user, hourly_rate=75)
        rate_factory(type=Rate.Type.PROJECT, project=project, hourly_rate=100)
        rate_factory(type=Rate.Type.EMPLOYEE_PROJECT, employee=user, project=project, hourly_rate=125)

        resolver = RateResolver(test_clock)
        rate, source = resolver.resolve(user.id, project.id)

        assert rate == Decimal('125.00')
        assert source == Rate.Type.EMPLOYEE_PROJECT

    def test_expired_rate_not_used(self, rate_factory, user, project, test_clock):
        """Rates with effective_to in the past are ignored."""
        test_clock.travel_to(datetime(2024, 6, 15))
        rate_factory(
            type=Rate.Type.EMPLOYEE_PROJECT,
            employee=user,
            project=project,
            hourly_rate=100,
            effective_from=date(2024, 1, 1),
            effective_to=date(2024, 5, 31)  # Expired
        )
        rate_factory(type=Rate.Type.COMPANY, hourly_rate=50)

        resolver = RateResolver(test_clock)
        rate, source = resolver.resolve(user.id, project.id)

        assert rate == Decimal('50.00')
        assert source == Rate.Type.COMPANY

    def test_falls_back_to_company_default(self, company_factory, project_factory, user, test_clock):
        """When no rates exist, uses company default."""
        company = company_factory(default_hourly_rate=Decimal('75.00'))
        project = project_factory(company=company)

        resolver = RateResolver(test_clock)
        rate, source = resolver.resolve(user.id, project.id)

        assert rate == Decimal('75.00')
        assert source == Rate.Type.COMPANY


# apps/timeentries/tests/test_views.py
class TestTimerAPI:
    """Tests for timer start/stop functionality."""

    def test_start_timer_when_no_active_timer_succeeds(self, authenticated_client, project):
        """Starting timer when no timer running creates timer entry."""
        response = authenticated_client.post('/api/v1/time-entries/timer/start/', {
            'project_id': project.id
        })
        assert response.status_code == 201
        assert response.data['timer_started_at'] is not None

    def test_start_timer_when_timer_active_returns_error(self, authenticated_client, project, time_entry_factory, user):
        """Cannot start new timer when one is already running."""
        time_entry_factory(user=user, timer_started_at=datetime.now())

        response = authenticated_client.post('/api/v1/time-entries/timer/start/', {
            'project_id': project.id
        })

        assert response.status_code == 400
        assert response.data['error']['code'] == 'BIZ_005'  # Timer already active

    def test_stop_timer_calculates_hours_and_snapshots_rate(self, authenticated_client, user, project, test_clock):
        """Stopping timer calculates hours and snapshots current rate."""
        # Start timer
        test_clock.travel_to(datetime(2024, 1, 15, 9, 0, 0))
        start_response = authenticated_client.post('/api/v1/time-entries/timer/start/', {
            'project_id': project.id
        })
        entry_id = start_response.data['id']

        # Stop timer 2 hours later
        test_clock.advance(timedelta(hours=2))
        stop_response = authenticated_client.post('/api/v1/time-entries/timer/stop/', {
            'entry_id': entry_id
        })

        assert stop_response.status_code == 200
        assert stop_response.data['hours'] == '2.00'
        assert stop_response.data['billing_rate'] is not None


class TestDailyLimitValidation:
    """Tests for 24-hour daily limit enforcement."""

    def test_entry_exceeding_24h_blocked(self, authenticated_client, user, project, time_entry_factory):
        """Cannot create entry that would exceed 24h for the day."""
        time_entry_factory(user=user, date=date(2024, 1, 15), hours=Decimal('20.00'))

        response = authenticated_client.post('/api/v1/time-entries/', {
            'project_id': project.id,
            'date': '2024-01-15',
            'hours': '5.00',  # Would total 25h
            'description': 'Test'
        })

        assert response.status_code == 400
        assert response.data['error']['code'] == 'BIZ_003'

    def test_warning_returned_at_threshold(self, authenticated_client, user, project, company_settings):
        """Response includes warning when approaching threshold."""
        company_settings.daily_warning_threshold = Decimal('10.00')
        company_settings.save()

        response = authenticated_client.post('/api/v1/time-entries/', {
            'project_id': project.id,
            'date': '2024-01-15',
            'hours': '11.00',
            'description': 'Test'
        })

        assert response.status_code == 201
        assert 'warning' in response.data
        assert response.data['warning']['code'] == 'THRESHOLD_EXCEEDED'
```

---

### 4.3 Slice 3: Timesheet + Approval (To Be Refined)

**Goal:** Implement workflow with escalation chain.

#### Models

```python
# apps/timesheets/models.py
class Timesheet(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        SUBMITTED = 'SUBMITTED', 'Submitted'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'

    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    week_start = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)

    submitted_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='approved_timesheets')
    rejected_at = models.DateTimeField(null=True, blank=True)
    rejected_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='rejected_timesheets')

    locked_at = models.DateTimeField(null=True, blank=True)
    locked_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='locked_timesheets')
    unlock_reason = models.TextField(blank=True)
    unlocked_at = models.DateTimeField(null=True, blank=True)
    unlocked_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='unlocked_timesheets')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'week_start']


class TimesheetComment(models.Model):
    timesheet = models.ForeignKey(Timesheet, on_delete=models.CASCADE, related_name='comments')
    entry = models.ForeignKey('timeentries.TimeEntry', on_delete=models.CASCADE, null=True, blank=True)
    author = models.ForeignKey('users.User', on_delete=models.CASCADE)
    text = models.TextField()
    mentioned_users = models.ManyToManyField('users.User', related_name='mentions', blank=True)
    resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class OOOPeriod(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['start_date']


class AdminOverride(models.Model):
    class Action(models.TextChoices):
        UNLOCK = 'UNLOCK', 'Unlock'
        EDIT = 'EDIT', 'Edit'
        DELETE = 'DELETE', 'Delete'

    timesheet = models.ForeignKey(Timesheet, on_delete=models.CASCADE)
    action = models.CharField(max_length=20, choices=Action.choices)
    reason = models.TextField()
    performed_by = models.ForeignKey('users.User', on_delete=models.CASCADE)
    performed_at = models.DateTimeField(auto_now_add=True)
    previous_state = models.JSONField()
    export_data = models.BinaryField(null=True, blank=True)  # JSON + base64 CSV blob
```

#### API Endpoints

```
GET    /api/v1/timesheets/                    # List user's timesheets
GET    /api/v1/timesheets/:id/                # Get timesheet details
POST   /api/v1/timesheets/:id/submit/         # Submit for approval
POST   /api/v1/timesheets/:id/approve/        # Approve (manager)
POST   /api/v1/timesheets/:id/reject/         # Reject with comments (manager)
POST   /api/v1/timesheets/:id/unlock/         # Unlock (admin only)
GET    /api/v1/timesheets/:id/comments/       # List comments
POST   /api/v1/timesheets/:id/comments/       # Add comment
PUT    /api/v1/timesheets/:id/comments/:cid/  # Update comment
DELETE /api/v1/timesheets/:id/comments/:cid/  # Delete comment
```

---

## 5. Infrastructure Layer

### 5.1 Clock Service

```python
# apps/infrastructure/clock.py
from datetime import datetime, timedelta
from typing import Protocol
import pytz

class Clock(Protocol):
    """Protocol for time operations, enabling test injection."""

    def now(self) -> datetime:
        """Get current UTC datetime."""
        ...

    def travel_to(self, dt: datetime) -> None:
        """Set current time (test only)."""
        ...

    def advance(self, delta: timedelta) -> None:
        """Advance time by delta (test only)."""
        ...


class SystemClock:
    """Production clock using actual system time."""

    def now(self) -> datetime:
        return datetime.now(pytz.UTC)

    def travel_to(self, dt: datetime) -> None:
        raise NotImplementedError("Cannot travel in production")

    def advance(self, delta: timedelta) -> None:
        raise NotImplementedError("Cannot advance in production")


class TestClock:
    """Test clock with time travel capabilities."""

    def __init__(self, initial: datetime = None):
        self._current = initial or datetime.now(pytz.UTC)

    def now(self) -> datetime:
        return self._current

    def travel_to(self, dt: datetime) -> None:
        self._current = dt

    def advance(self, delta: timedelta) -> None:
        self._current += delta


# Dependency injection setup
def get_clock() -> Clock:
    """Get clock instance based on settings."""
    from django.conf import settings
    if getattr(settings, 'TESTING', False):
        return TestClock()
    return SystemClock()
```

### 5.2 Storage Service

```python
# apps/infrastructure/storage.py
from django.conf import settings
from django.core.files.storage import default_storage

def get_storage():
    """Get configured storage backend."""
    return default_storage

# Settings configuration
# config/settings/development.py
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
MEDIA_ROOT = BASE_DIR / 'media'

# config/settings/production.py
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
```

### 5.3 Notification Service

```python
# apps/infrastructure/notifications.py
from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string

class NotificationType:
    TIMESHEET_SUBMITTED = 'timesheet_submitted'
    TIMESHEET_APPROVED = 'timesheet_approved'
    TIMESHEET_REJECTED = 'timesheet_rejected'
    ESCALATION_ALERT = 'escalation_alert'
    PASSWORD_RESET = 'password_reset'


@shared_task
def send_notification(user_id: int, notification_type: str, context: dict):
    """Send notification via appropriate channel."""
    from apps.users.models import User
    user = User.objects.get(id=user_id)

    # Check notification preferences
    if notification_type in [NotificationType.PASSWORD_RESET]:
        # Security notifications always sent
        pass
    elif not user.workflow_notifications_enabled:
        return  # User opted out

    # Render and send email
    template = f'emails/{notification_type}.html'
    subject = get_subject(notification_type)
    html_content = render_to_string(template, context)

    send_mail(
        subject=subject,
        message='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_content,
    )
```

---

## 6. Testing Strategy

### 6.1 Test Configuration

```python
# config/settings/test.py
from .base import *

TESTING = True

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

# Faster password hashing for tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Celery eager mode disabled - we mock tasks
CELERY_TASK_ALWAYS_EAGER = False
```

```ini
# pytest.ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings.test
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = --reuse-db --tb=short
filterwarnings =
    ignore::DeprecationWarning
```

### 6.2 Fixtures

```python
# conftest.py (root)
import pytest
from datetime import datetime
from rest_framework.test import APIClient

from apps.infrastructure.clock import TestClock


@pytest.fixture
def api_client():
    """Unauthenticated API client."""
    return APIClient()


@pytest.fixture
def test_clock():
    """Injectable test clock."""
    return TestClock(initial=datetime(2024, 1, 15, 12, 0, 0))


@pytest.fixture
def authenticated_client(api_client, user):
    """API client authenticated as user."""
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


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
    workflow_notifications_enabled = True
    security_notifications_enabled = True


@pytest.fixture
def user_factory(db, company):
    """Factory fixture for creating users."""
    def create(**kwargs):
        kwargs.setdefault('company', company)
        return UserFactory(**kwargs)
    return create


@pytest.fixture
def user(user_factory):
    """Default test user."""
    return user_factory()
```

### 6.3 Test Patterns

See [docs/testing.md](testing.md) for comprehensive patterns guide.

---

## 7. CI/CD Pipeline

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  PYTHON_VERSION: '3.12'

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: timetrack_test
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

      redis:
        image: redis:7
        ports:
          - 6379:6379

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: 'pip'

      - name: Install dependencies
        run: |
          pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Run migrations
        env:
          DATABASE_URL: postgres://test:test@localhost:5432/timetrack_test
          REDIS_URL: redis://localhost:6379/0
        run: python manage.py migrate

      - name: Run tests with coverage
        env:
          DATABASE_URL: postgres://test:test@localhost:5432/timetrack_test
          REDIS_URL: redis://localhost:6379/0
          DJANGO_SETTINGS_MODULE: config.settings.test
        run: |
          pytest \
            --cov=apps \
            --cov-report=xml \
            --cov-report=term-missing \
            --cov-fail-under=80

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage.xml
          fail_ci_if_error: true

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Install linters
        run: pip install ruff mypy

      - name: Run Ruff check
        run: ruff check .

      - name: Run Ruff format check
        run: ruff format --check .

      - name: Run mypy
        run: mypy apps/ --ignore-missing-imports

  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Install safety
        run: pip install safety

      - name: Check for vulnerabilities
        run: safety check -r requirements.txt
```

---

## 8. Process & Documentation

### 8.1 ADR Template

```markdown
# ADR-XXXX: [Title]

## Problem
[What problem are we solving?]

## Decision
[What did we decide?]

## Rationale
[Why did we make this decision?]

## Consequences
[What are the implications?]
```

### 8.2 PR Templates

Located in `.github/PULL_REQUEST_TEMPLATE/`:

- `01_auth.md` - Auth + Profile slice checklist
- `02_timeentry.md` - Time Entry + Timer slice checklist
- `03_timesheet.md` - Timesheet + Approval slice checklist

---

## 9. Verification Checklist

### Per-Slice

- [ ] All slice tests pass: `pytest apps/<slice>/`
- [ ] Coverage ≥ 100% on models.py, services.py
- [ ] PR checklist complete
- [ ] Migrations committed
- [ ] ADR written for any significant learnings

### Integration

- [ ] Full test suite passes: `pytest`
- [ ] CI pipeline green on PR
- [ ] No type errors: `mypy apps/`
- [ ] No lint errors: `ruff check .`

### Manual Smoke Test

1. Login with test user
2. Create time entry (verify rate snapshot)
3. Start/stop timer
4. Submit timesheet
5. Login as manager, approve timesheet
6. Verify notifications sent (check Celery logs)

---

## Next Steps

1. **Create Django project skeleton** - `django-admin startproject config .`
2. **Set up Docker Compose** - Postgres + Redis containers
3. **Implement infrastructure app** - Clock, storage, notifications
4. **Begin Slice 1** - Write failing tests, then implement Auth + Profile
