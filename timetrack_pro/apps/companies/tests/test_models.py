"""
Tests for Company models - TDD approach.

Following the CRUD + BDD test patterns from docs/testing.md.
"""
import pytest
from datetime import timedelta
from django.db import IntegrityError
from django.core.exceptions import ValidationError


@pytest.mark.django_db
class TestCompanyModel:
    """Tests for the Company model."""

    def test_company_creation_with_required_fields(self):
        """Company can be created with name only."""
        from apps.companies.models import Company

        company = Company.objects.create(name='Acme Corp')
        assert company.id is not None
        assert company.name == 'Acme Corp'

    def test_company_default_week_start_is_monday(self):
        """Company defaults to Monday as week start."""
        from apps.companies.models import Company

        company = Company.objects.create(name='Test Corp')
        assert company.week_start_day == Company.WeekDay.MONDAY

    def test_company_default_timezone_is_utc(self):
        """Company defaults to UTC timezone."""
        from apps.companies.models import Company

        company = Company.objects.create(name='Test Corp')
        assert company.timezone == 'UTC'

    def test_company_name_must_be_unique(self):
        """Company name must be unique."""
        from apps.companies.models import Company

        Company.objects.create(name='Unique Corp')
        with pytest.raises(IntegrityError):
            Company.objects.create(name='Unique Corp')

    def test_company_string_representation(self):
        """Company string representation is the name."""
        from apps.companies.models import Company

        company = Company.objects.create(name='Display Corp')
        assert str(company) == 'Display Corp'

    def test_company_week_start_choices(self):
        """Company can have any day as week start."""
        from apps.companies.models import Company

        company = Company.objects.create(
            name='Sunday Start Corp',
            week_start_day=Company.WeekDay.SUNDAY
        )
        assert company.week_start_day == Company.WeekDay.SUNDAY

    def test_company_has_timestamps(self):
        """Company has created_at and updated_at fields."""
        from apps.companies.models import Company

        company = Company.objects.create(name='Timestamp Corp')
        assert company.created_at is not None
        assert company.updated_at is not None


@pytest.mark.django_db
class TestCompanySettingsModel:
    """Tests for the CompanySettings model."""

    def test_settings_created_with_company(self):
        """CompanySettings can be created for a company."""
        from apps.companies.models import Company, CompanySettings

        company = Company.objects.create(name='Settings Corp')
        settings = CompanySettings.objects.create(company=company)
        assert settings.id is not None
        assert settings.company == company

    def test_settings_default_unlock_window_is_7_days(self):
        """Default unlock window is 7 days."""
        from apps.companies.models import Company, CompanySettings

        company = Company.objects.create(name='Unlock Corp')
        settings = CompanySettings.objects.create(company=company)
        assert settings.unlock_window_days == 7

    def test_settings_default_daily_warning_threshold_is_8(self):
        """Default daily warning threshold is 8 hours."""
        from apps.companies.models import Company, CompanySettings

        company = Company.objects.create(name='Warning Corp')
        settings = CompanySettings.objects.create(company=company)
        assert settings.daily_warning_threshold == 8

    def test_settings_default_escalation_days_is_3(self):
        """Default escalation days is 3."""
        from apps.companies.models import Company, CompanySettings

        company = Company.objects.create(name='Escalation Corp')
        settings = CompanySettings.objects.create(company=company)
        assert settings.escalation_days == 3

    def test_settings_default_escalation_logic_is_or(self):
        """Default escalation logic is OR."""
        from apps.companies.models import Company, CompanySettings

        company = Company.objects.create(name='Logic Corp')
        settings = CompanySettings.objects.create(company=company)
        assert settings.escalation_logic == CompanySettings.EscalationLogic.OR

    def test_settings_one_to_one_with_company(self):
        """Each company has only one settings record."""
        from apps.companies.models import Company, CompanySettings

        company = Company.objects.create(name='One Corp')
        CompanySettings.objects.create(company=company)
        with pytest.raises(IntegrityError):
            CompanySettings.objects.create(company=company)

    def test_settings_string_representation(self):
        """Settings string representation includes company name."""
        from apps.companies.models import Company, CompanySettings

        company = Company.objects.create(name='Display Corp')
        settings = CompanySettings.objects.create(company=company)
        assert 'Display Corp' in str(settings)

    def test_settings_default_company_rate_required(self):
        """Default company rate defaults to zero (must be set at setup)."""
        from apps.companies.models import Company, CompanySettings
        from decimal import Decimal

        company = Company.objects.create(name='Rate Corp')
        settings = CompanySettings.objects.create(company=company)
        assert settings.default_hourly_rate == Decimal('0.00')


@pytest.mark.django_db
class TestCompanySettingsAuditModel:
    """Tests for the CompanySettingsAudit model."""

    def test_audit_record_created_on_settings_change(self):
        """Audit record captures settings changes."""
        from apps.companies.models import Company, CompanySettings, CompanySettingsAudit

        company = Company.objects.create(name='Audit Corp')
        settings = CompanySettings.objects.create(company=company)

        audit = CompanySettingsAudit.objects.create(
            company_settings=settings,
            changed_by=None,  # System change
            field_name='unlock_window_days',
            old_value='7',
            new_value='14'
        )
        assert audit.id is not None
        assert audit.field_name == 'unlock_window_days'

    def test_audit_tracks_who_made_change(self):
        """Audit record tracks the user who made the change."""
        from apps.companies.models import Company, CompanySettings, CompanySettingsAudit
        from apps.users.factories import UserFactory

        company = Company.objects.create(name='Track Corp')
        settings = CompanySettings.objects.create(company=company)
        user = UserFactory(company=company)

        audit = CompanySettingsAudit.objects.create(
            company_settings=settings,
            changed_by=user,
            field_name='daily_warning_threshold',
            old_value='8',
            new_value='10'
        )
        assert audit.changed_by == user

    def test_audit_has_timestamp(self):
        """Audit record has created_at timestamp."""
        from apps.companies.models import Company, CompanySettings, CompanySettingsAudit

        company = Company.objects.create(name='Time Corp')
        settings = CompanySettings.objects.create(company=company)

        audit = CompanySettingsAudit.objects.create(
            company_settings=settings,
            field_name='escalation_days',
            old_value='3',
            new_value='5'
        )
        assert audit.created_at is not None

    def test_audit_string_representation(self):
        """Audit string shows field and change summary."""
        from apps.companies.models import Company, CompanySettings, CompanySettingsAudit

        company = Company.objects.create(name='Summary Corp')
        settings = CompanySettings.objects.create(company=company)

        audit = CompanySettingsAudit.objects.create(
            company_settings=settings,
            field_name='unlock_window_days',
            old_value='7',
            new_value='14'
        )
        repr_str = str(audit)
        assert 'unlock_window_days' in repr_str


@pytest.mark.django_db
class TestCompanySettingsEscalationScenarios:
    """BDD-style tests for escalation configuration."""

    def test_given_or_logic_when_ooo_then_escalates(self):
        """
        Given: Company with OR escalation logic
        When: Manager is OOO
        Then: Should escalate (OOO OR pending_days)
        """
        from apps.companies.models import Company, CompanySettings

        company = Company.objects.create(name='OR Corp')
        settings = CompanySettings.objects.create(
            company=company,
            escalation_logic=CompanySettings.EscalationLogic.OR,
            escalation_days=3
        )

        # Escalation check: OOO=True OR pending_days>=3
        manager_is_ooo = True
        pending_days = 1  # Less than threshold

        should_escalate = (
            settings.escalation_logic == CompanySettings.EscalationLogic.OR
            and (manager_is_ooo or pending_days >= settings.escalation_days)
        )
        assert should_escalate is True

    def test_given_and_logic_when_only_ooo_then_no_escalation(self):
        """
        Given: Company with AND escalation logic
        When: Manager is OOO but pending days < threshold
        Then: Should NOT escalate (requires both conditions)
        """
        from apps.companies.models import Company, CompanySettings

        company = Company.objects.create(name='AND Corp')
        settings = CompanySettings.objects.create(
            company=company,
            escalation_logic=CompanySettings.EscalationLogic.AND,
            escalation_days=3
        )

        manager_is_ooo = True
        pending_days = 1  # Less than threshold

        should_escalate = (
            settings.escalation_logic == CompanySettings.EscalationLogic.AND
            and (manager_is_ooo and pending_days >= settings.escalation_days)
        )
        assert should_escalate is False

    def test_given_and_logic_when_both_conditions_then_escalates(self):
        """
        Given: Company with AND escalation logic
        When: Manager is OOO AND pending days >= threshold
        Then: Should escalate
        """
        from apps.companies.models import Company, CompanySettings

        company = Company.objects.create(name='Both Corp')
        settings = CompanySettings.objects.create(
            company=company,
            escalation_logic=CompanySettings.EscalationLogic.AND,
            escalation_days=3
        )

        manager_is_ooo = True
        pending_days = 5  # Exceeds threshold

        should_escalate = (
            settings.escalation_logic == CompanySettings.EscalationLogic.AND
            and (manager_is_ooo and pending_days >= settings.escalation_days)
        )
        assert should_escalate is True
