"""
Tests for Rate resolution service - TDD approach.

Rate hierarchy (highest to lowest priority):
1. Employee-Project specific rate
2. Project default rate
3. Employee default rate
4. Company default rate (fallback)

All rates are filtered by effective date.
"""
from datetime import date
from decimal import Decimal

import pytest

from apps.rates.models import Rate
from apps.rates.services import RateResolutionService, RateResolutionResult


@pytest.mark.django_db
class TestRateResolutionService:
    """Tests for rate resolution logic."""

    def test_resolve_employee_project_rate_highest_priority(
        self, company, user, project, rate_factory
    ):
        """
        Given: Rates at all levels for same employee/project
        When: Resolving rate
        Then: Employee-project rate is returned
        """
        rate_factory(
            company=company,
            employee=user,
            project=project,
            rate_type=Rate.RateType.EMPLOYEE_PROJECT,
            hourly_rate=Decimal('150.00'),
            effective_from=date(2024, 1, 1),
        )
        rate_factory(
            company=company,
            project=project,
            rate_type=Rate.RateType.PROJECT,
            hourly_rate=Decimal('100.00'),
            effective_from=date(2024, 1, 1),
        )
        rate_factory(
            company=company,
            employee=user,
            rate_type=Rate.RateType.EMPLOYEE,
            hourly_rate=Decimal('125.00'),
            effective_from=date(2024, 1, 1),
        )

        result = RateResolutionService.resolve(
            user=user,
            project=project,
            as_of_date=date(2024, 6, 15),
        )

        assert result.rate == Decimal('150.00')
        assert result.source == Rate.RateType.EMPLOYEE_PROJECT

    def test_resolve_project_rate_when_no_employee_project_rate(
        self, company, user, project, rate_factory
    ):
        """
        Given: Project and employee rates, but no employee-project rate
        When: Resolving rate
        Then: Project rate is returned
        """
        rate_factory(
            company=company,
            project=project,
            rate_type=Rate.RateType.PROJECT,
            hourly_rate=Decimal('100.00'),
            effective_from=date(2024, 1, 1),
        )
        rate_factory(
            company=company,
            employee=user,
            rate_type=Rate.RateType.EMPLOYEE,
            hourly_rate=Decimal('125.00'),
            effective_from=date(2024, 1, 1),
        )

        result = RateResolutionService.resolve(
            user=user,
            project=project,
            as_of_date=date(2024, 6, 15),
        )

        assert result.rate == Decimal('100.00')
        assert result.source == Rate.RateType.PROJECT

    def test_resolve_employee_rate_when_no_project_rate(
        self, company, user, project, rate_factory
    ):
        """
        Given: Only employee rate exists
        When: Resolving rate
        Then: Employee rate is returned
        """
        rate_factory(
            company=company,
            employee=user,
            rate_type=Rate.RateType.EMPLOYEE,
            hourly_rate=Decimal('125.00'),
            effective_from=date(2024, 1, 1),
        )

        result = RateResolutionService.resolve(
            user=user,
            project=project,
            as_of_date=date(2024, 6, 15),
        )

        assert result.rate == Decimal('125.00')
        assert result.source == Rate.RateType.EMPLOYEE

    def test_resolve_company_default_rate_as_fallback(self, company, user, project):
        """
        Given: No specific rates exist
        When: Resolving rate
        Then: Company default rate is returned
        """
        company.settings.default_hourly_rate = Decimal('75.00')
        company.settings.save()

        result = RateResolutionService.resolve(
            user=user,
            project=project,
            as_of_date=date(2024, 6, 15),
        )

        assert result.rate == Decimal('75.00')
        assert result.source == 'COMPANY'

    def test_resolve_filters_by_effective_date(
        self, company, user, project, rate_factory
    ):
        """
        Given: Rates with different effective date ranges
        When: Resolving rate for specific date
        Then: Only rate effective on that date is used
        """
        rate_factory(
            company=company,
            employee=user,
            project=project,
            rate_type=Rate.RateType.EMPLOYEE_PROJECT,
            hourly_rate=Decimal('100.00'),
            effective_from=date(2024, 1, 1),
            effective_to=date(2024, 3, 31),
        )
        rate_factory(
            company=company,
            employee=user,
            project=project,
            rate_type=Rate.RateType.EMPLOYEE_PROJECT,
            hourly_rate=Decimal('120.00'),
            effective_from=date(2024, 4, 1),
        )

        result_q1 = RateResolutionService.resolve(
            user=user,
            project=project,
            as_of_date=date(2024, 2, 15),
        )
        result_q2 = RateResolutionService.resolve(
            user=user,
            project=project,
            as_of_date=date(2024, 5, 15),
        )

        assert result_q1.rate == Decimal('100.00')
        assert result_q2.rate == Decimal('120.00')

    def test_resolve_ignores_future_rates(self, company, user, project, rate_factory):
        """
        Given: A rate that starts in the future
        When: Resolving rate for today
        Then: Future rate is not used
        """
        rate_factory(
            company=company,
            employee=user,
            project=project,
            rate_type=Rate.RateType.EMPLOYEE_PROJECT,
            hourly_rate=Decimal('200.00'),
            effective_from=date(2025, 1, 1),
        )

        company.settings.default_hourly_rate = Decimal('50.00')
        company.settings.save()

        result = RateResolutionService.resolve(
            user=user,
            project=project,
            as_of_date=date(2024, 6, 15),
        )

        assert result.rate == Decimal('50.00')
        assert result.source == 'COMPANY'

    def test_resolve_ignores_expired_rates(self, company, user, project, rate_factory):
        """
        Given: A rate that has expired
        When: Resolving rate for date after expiry
        Then: Expired rate is not used
        """
        rate_factory(
            company=company,
            employee=user,
            project=project,
            rate_type=Rate.RateType.EMPLOYEE_PROJECT,
            hourly_rate=Decimal('150.00'),
            effective_from=date(2023, 1, 1),
            effective_to=date(2023, 12, 31),
        )

        company.settings.default_hourly_rate = Decimal('50.00')
        company.settings.save()

        result = RateResolutionService.resolve(
            user=user,
            project=project,
            as_of_date=date(2024, 6, 15),
        )

        assert result.rate == Decimal('50.00')
        assert result.source == 'COMPANY'

    def test_resolve_open_ended_rate_no_effective_to(
        self, company, user, project, rate_factory
    ):
        """
        Given: A rate with no effective_to (open-ended)
        When: Resolving rate for any future date
        Then: Rate is used
        """
        rate_factory(
            company=company,
            employee=user,
            project=project,
            rate_type=Rate.RateType.EMPLOYEE_PROJECT,
            hourly_rate=Decimal('175.00'),
            effective_from=date(2024, 1, 1),
            effective_to=None,
        )

        result = RateResolutionService.resolve(
            user=user,
            project=project,
            as_of_date=date(2030, 12, 31),
        )

        assert result.rate == Decimal('175.00')

    def test_resolve_most_recent_rate_when_multiple_effective(
        self, company, user, project, rate_factory
    ):
        """
        Given: Multiple overlapping rates at same level
        When: Resolving rate
        Then: Most recent effective_from is used
        """
        rate_factory(
            company=company,
            employee=user,
            project=project,
            rate_type=Rate.RateType.EMPLOYEE_PROJECT,
            hourly_rate=Decimal('100.00'),
            effective_from=date(2024, 1, 1),
        )
        rate_factory(
            company=company,
            employee=user,
            project=project,
            rate_type=Rate.RateType.EMPLOYEE_PROJECT,
            hourly_rate=Decimal('110.00'),
            effective_from=date(2024, 3, 1),
        )

        result = RateResolutionService.resolve(
            user=user,
            project=project,
            as_of_date=date(2024, 6, 15),
        )

        assert result.rate == Decimal('110.00')

    def test_resolve_null_company_default_rate(self, company, user, project):
        """
        Given: No rates exist and company default is 0
        When: Resolving rate
        Then: Returns 0 with COMPANY source
        """
        company.settings.default_hourly_rate = Decimal('0.00')
        company.settings.save()

        result = RateResolutionService.resolve(
            user=user,
            project=project,
            as_of_date=date(2024, 6, 15),
        )

        assert result.rate == Decimal('0.00')
        assert result.source == 'COMPANY'


@pytest.mark.django_db
class TestRateResolutionResult:
    """Tests for RateResolutionResult data class."""

    def test_result_has_rate_and_source(self):
        """
        Given: Creating a RateResolutionResult
        When: Accessing attributes
        Then: rate and source are available
        """
        result = RateResolutionResult(
            rate=Decimal('100.00'),
            source='EMPLOYEE_PROJECT',
        )

        assert result.rate == Decimal('100.00')
        assert result.source == 'EMPLOYEE_PROJECT'
