"""
Company models for TimeTrack Pro.

Contains:
- Company: Organization entity
- CompanySettings: Configurable settings per company
- CompanySettingsAudit: Full audit trail for settings changes
"""
from decimal import Decimal

from django.conf import settings
from django.db import models

from core.models import TimeStampedModel


class Company(TimeStampedModel):
    """
    Organization entity that owns users, projects, and configuration.

    All business entities belong to a company for multi-tenancy support.
    """

    class WeekDay(models.IntegerChoices):
        MONDAY = 0, 'Monday'
        TUESDAY = 1, 'Tuesday'
        WEDNESDAY = 2, 'Wednesday'
        THURSDAY = 3, 'Thursday'
        FRIDAY = 4, 'Friday'
        SATURDAY = 5, 'Saturday'
        SUNDAY = 6, 'Sunday'

    name = models.CharField(max_length=255, unique=True)
    week_start_day = models.IntegerField(
        choices=WeekDay.choices,
        default=WeekDay.MONDAY,
    )
    timezone = models.CharField(max_length=50, default='UTC')

    class Meta:
        verbose_name_plural = 'companies'

    def __str__(self) -> str:
        return self.name


class CompanySettings(TimeStampedModel):
    """
    Configurable settings for a company.

    One-to-one relationship with Company. All changes are audited.
    """

    class EscalationLogic(models.TextChoices):
        OR = 'OR', 'OOO OR Pending Days'
        AND = 'AND', 'OOO AND Pending Days'

    company = models.OneToOneField(
        Company,
        on_delete=models.CASCADE,
        related_name='settings',
    )
    unlock_window_days = models.PositiveIntegerField(default=7)
    daily_warning_threshold = models.PositiveIntegerField(default=8)
    escalation_days = models.PositiveIntegerField(default=3)
    escalation_logic = models.CharField(
        max_length=10,
        choices=EscalationLogic.choices,
        default=EscalationLogic.OR,
    )
    default_hourly_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
    )

    class Meta:
        verbose_name_plural = 'company settings'

    def __str__(self) -> str:
        return f'Settings for {self.company.name}'


class CompanySettingsAudit(models.Model):
    """
    Audit trail for CompanySettings changes.

    Records who changed what, when, and the before/after values.
    """

    company_settings = models.ForeignKey(
        CompanySettings,
        on_delete=models.CASCADE,
        related_name='audit_logs',
    )
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    field_name = models.CharField(max_length=100)
    old_value = models.TextField(blank=True)
    new_value = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'{self.field_name}: {self.old_value} → {self.new_value}'
