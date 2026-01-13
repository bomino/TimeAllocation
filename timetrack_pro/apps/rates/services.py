"""
Rate resolution service for TimeTrack Pro.

Implements the rate hierarchy:
1. Employee-Project specific rate (highest priority)
2. Project default rate
3. Employee default rate
4. Company default rate (fallback)
"""
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional

from django.db.models import Q

from apps.rates.models import Rate


@dataclass
class RateResolutionResult:
    """Result of rate resolution with source tracking."""

    rate: Decimal
    source: str


class RateResolutionService:
    """Service for resolving applicable billing rates."""

    @classmethod
    def resolve(
        cls,
        user,
        project,
        as_of_date: date,
    ) -> RateResolutionResult:
        """
        Resolve the applicable rate for a user/project combination.

        Args:
            user: The user to resolve rate for
            project: The project to resolve rate for
            as_of_date: The date to check rate effectiveness

        Returns:
            RateResolutionResult with rate and source
        """
        company = project.company

        effective_filter = Q(effective_from__lte=as_of_date) & (
            Q(effective_to__isnull=True) | Q(effective_to__gte=as_of_date)
        )

        employee_project_rate = (
            Rate.objects.filter(
                company=company,
                employee=user,
                project=project,
                rate_type=Rate.RateType.EMPLOYEE_PROJECT,
            )
            .filter(effective_filter)
            .order_by('-effective_from')
            .first()
        )
        if employee_project_rate:
            return RateResolutionResult(
                rate=employee_project_rate.hourly_rate,
                source=Rate.RateType.EMPLOYEE_PROJECT,
            )

        project_rate = (
            Rate.objects.filter(
                company=company,
                project=project,
                rate_type=Rate.RateType.PROJECT,
            )
            .filter(effective_filter)
            .order_by('-effective_from')
            .first()
        )
        if project_rate:
            return RateResolutionResult(
                rate=project_rate.hourly_rate,
                source=Rate.RateType.PROJECT,
            )

        employee_rate = (
            Rate.objects.filter(
                company=company,
                employee=user,
                rate_type=Rate.RateType.EMPLOYEE,
            )
            .filter(effective_filter)
            .order_by('-effective_from')
            .first()
        )
        if employee_rate:
            return RateResolutionResult(
                rate=employee_rate.hourly_rate,
                source=Rate.RateType.EMPLOYEE,
            )

        return RateResolutionResult(
            rate=company.settings.default_hourly_rate,
            source='COMPANY',
        )
