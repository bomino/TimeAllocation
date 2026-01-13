"""
Rate models for TimeTrack Pro.

Placeholder for Slice 2 implementation.
Rate hierarchy: employee-project → project → employee → company
"""
from decimal import Decimal

from django.conf import settings
from django.db import models

from core.models import TimeStampedModel


class Rate(TimeStampedModel):
    """
    Billing rate configuration.

    Rates can be set at multiple levels:
    - Employee-Project specific (highest priority)
    - Project default
    - Employee default
    - Company default (fallback)
    """

    class RateType(models.TextChoices):
        EMPLOYEE_PROJECT = 'EMPLOYEE_PROJECT', 'Employee-Project'
        PROJECT = 'PROJECT', 'Project'
        EMPLOYEE = 'EMPLOYEE', 'Employee'

    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='rates',
    )
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='rates',
    )
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='rates',
    )
    rate_type = models.CharField(max_length=20, choices=RateType.choices)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-effective_from']

    def __str__(self) -> str:
        return f'{self.rate_type}: ${self.hourly_rate}/hr'
