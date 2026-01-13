"""
Tests for Rate models - TDD approach.
"""
from datetime import date
from decimal import Decimal

import pytest

from apps.rates.models import Rate


@pytest.mark.django_db
class TestRateModel:
    """Tests for Rate model."""

    def test_create_employee_project_rate(self, company, user, project):
        """
        Given: A company, user, and project
        When: Creating an employee-project specific rate
        Then: Rate is created with correct type
        """
        rate = Rate.objects.create(
            company=company,
            employee=user,
            project=project,
            rate_type=Rate.RateType.EMPLOYEE_PROJECT,
            hourly_rate=Decimal('150.00'),
            effective_from=date(2024, 1, 1),
        )

        assert rate.pk is not None
        assert rate.rate_type == Rate.RateType.EMPLOYEE_PROJECT
        assert rate.hourly_rate == Decimal('150.00')

    def test_create_project_rate(self, company, project):
        """
        Given: A company and project
        When: Creating a project-level rate
        Then: Rate is created without employee
        """
        rate = Rate.objects.create(
            company=company,
            project=project,
            rate_type=Rate.RateType.PROJECT,
            hourly_rate=Decimal('100.00'),
            effective_from=date(2024, 1, 1),
        )

        assert rate.employee is None
        assert rate.project == project
        assert rate.rate_type == Rate.RateType.PROJECT

    def test_create_employee_rate(self, company, user):
        """
        Given: A company and user
        When: Creating an employee-level rate
        Then: Rate is created without project
        """
        rate = Rate.objects.create(
            company=company,
            employee=user,
            rate_type=Rate.RateType.EMPLOYEE,
            hourly_rate=Decimal('125.00'),
            effective_from=date(2024, 1, 1),
        )

        assert rate.project is None
        assert rate.employee == user
        assert rate.rate_type == Rate.RateType.EMPLOYEE

    def test_rate_effective_to_is_optional(self, company):
        """
        Given: Creating a rate
        When: No effective_to date provided
        Then: Rate is created with null effective_to (open-ended)
        """
        rate = Rate.objects.create(
            company=company,
            rate_type=Rate.RateType.PROJECT,
            hourly_rate=Decimal('100.00'),
            effective_from=date(2024, 1, 1),
        )

        assert rate.effective_to is None

    def test_rate_with_effective_date_range(self, company):
        """
        Given: Creating a rate with date range
        When: Both effective_from and effective_to provided
        Then: Both dates are saved
        """
        rate = Rate.objects.create(
            company=company,
            rate_type=Rate.RateType.PROJECT,
            hourly_rate=Decimal('100.00'),
            effective_from=date(2024, 1, 1),
            effective_to=date(2024, 12, 31),
        )

        assert rate.effective_from == date(2024, 1, 1)
        assert rate.effective_to == date(2024, 12, 31)

    def test_rate_str_representation(self, company):
        """
        Given: A rate
        When: Converting to string
        Then: Shows rate type and hourly rate
        """
        rate = Rate.objects.create(
            company=company,
            rate_type=Rate.RateType.PROJECT,
            hourly_rate=Decimal('100.00'),
            effective_from=date(2024, 1, 1),
        )

        assert str(rate) == 'PROJECT: $100.00/hr'

    def test_rates_ordered_by_effective_from_descending(self, company):
        """
        Given: Multiple rates with different effective dates
        When: Querying rates
        Then: Most recent effective_from first
        """
        Rate.objects.create(
            company=company,
            rate_type=Rate.RateType.PROJECT,
            hourly_rate=Decimal('100.00'),
            effective_from=date(2024, 1, 1),
        )
        Rate.objects.create(
            company=company,
            rate_type=Rate.RateType.PROJECT,
            hourly_rate=Decimal('110.00'),
            effective_from=date(2024, 6, 1),
        )
        Rate.objects.create(
            company=company,
            rate_type=Rate.RateType.PROJECT,
            hourly_rate=Decimal('105.00'),
            effective_from=date(2024, 3, 1),
        )

        rates = list(Rate.objects.filter(company=company))
        assert rates[0].hourly_rate == Decimal('110.00')
        assert rates[1].hourly_rate == Decimal('105.00')
        assert rates[2].hourly_rate == Decimal('100.00')

    def test_rate_has_timestamps(self, company):
        """
        Given: A newly created rate
        When: Checking timestamps
        Then: created_at and updated_at are set
        """
        rate = Rate.objects.create(
            company=company,
            rate_type=Rate.RateType.PROJECT,
            hourly_rate=Decimal('100.00'),
            effective_from=date(2024, 1, 1),
        )

        assert rate.created_at is not None
        assert rate.updated_at is not None


@pytest.mark.django_db
class TestRateTypeChoices:
    """Tests for Rate type choices."""

    def test_rate_type_employee_project(self):
        assert Rate.RateType.EMPLOYEE_PROJECT == 'EMPLOYEE_PROJECT'

    def test_rate_type_project(self):
        assert Rate.RateType.PROJECT == 'PROJECT'

    def test_rate_type_employee(self):
        assert Rate.RateType.EMPLOYEE == 'EMPLOYEE'
