"""
TimeEntry models for TimeTrack Pro.

Placeholder for Slice 2 implementation.
"""
from decimal import Decimal

from django.conf import settings
from django.db import models

from core.models import TimeStampedModel


class TimeEntry(TimeStampedModel):
    """
    Individual time entry record.

    Rate is snapshotted at creation and never recalculated.
    """

    class RateSource(models.TextChoices):
        EMPLOYEE_PROJECT = 'EMPLOYEE_PROJECT', 'Employee-Project Rate'
        PROJECT = 'PROJECT', 'Project Rate'
        EMPLOYEE = 'EMPLOYEE', 'Employee Rate'
        COMPANY = 'COMPANY', 'Company Default Rate'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='time_entries',
    )
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='time_entries',
    )
    timesheet = models.ForeignKey(
        'timesheets.Timesheet',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='entries',
    )
    date = models.DateField()
    hours = models.DecimalField(max_digits=4, decimal_places=2)
    description = models.TextField(blank=True)

    billing_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Snapshotted rate at entry creation',
    )
    rate_source = models.CharField(
        max_length=20,
        choices=RateSource.choices,
        help_text='Where the billing rate was resolved from',
    )

    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name_plural = 'time entries'

    def __str__(self) -> str:
        return f'{self.user.email} - {self.project.name} - {self.date}'

    @property
    def billable_amount(self) -> Decimal:
        return self.hours * self.billing_rate
