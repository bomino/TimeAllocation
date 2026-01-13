"""
Timesheet models for TimeTrack Pro.

Placeholder for Slice 3 implementation.
"""
from django.conf import settings
from django.db import models

from core.models import TimeStampedModel


class Timesheet(TimeStampedModel):
    """
    Weekly timesheet for approval workflow.

    Auto-created via Celery cron. Full week submission only.
    """

    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        SUBMITTED = 'SUBMITTED', 'Submitted'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='timesheets',
    )
    week_start = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    submitted_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_timesheets',
    )
    locked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['user', 'week_start']
        ordering = ['-week_start']

    def __str__(self) -> str:
        return f'{self.user.email} - Week of {self.week_start}'


class TimesheetComment(TimeStampedModel):
    """
    Line-item conversation on timesheet rejection.

    Comments can be tied to a specific entry or the overall timesheet.
    Collapsed on approval but preserved.
    """

    timesheet = models.ForeignKey(
        Timesheet,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    entry = models.ForeignKey(
        'timeentries.TimeEntry',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='comments',
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='timesheet_comments',
    )
    text = models.TextField()
    resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self) -> str:
        return f'Comment by {self.author.email} on {self.timesheet}'


class OOOPeriod(TimeStampedModel):
    """
    Out-of-Office period for a user.

    Max: 1 active + 1 future per user.
    Used for escalation logic.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ooo_periods',
    )
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        ordering = ['start_date']

    def __str__(self) -> str:
        return f'{self.user.email} OOO: {self.start_date} to {self.end_date}'


class AdminOverride(TimeStampedModel):
    """
    Admin override action on a timesheet.

    Records administrative actions with full audit trail.
    """

    class Action(models.TextChoices):
        UNLOCK = 'UNLOCK', 'Unlock'
        FORCE_APPROVE = 'FORCE_APPROVE', 'Force Approve'
        FORCE_REJECT = 'FORCE_REJECT', 'Force Reject'

    timesheet = models.ForeignKey(
        Timesheet,
        on_delete=models.CASCADE,
        related_name='admin_overrides',
    )
    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='admin_overrides',
    )
    action = models.CharField(max_length=20, choices=Action.choices)
    reason = models.TextField()
    previous_status = models.CharField(max_length=20)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'{self.action} by {self.admin.email} on {self.timesheet}'


class ApprovalDelegation(TimeStampedModel):
    """
    Delegation of approval authority from one manager to another.

    Allows managers to delegate their approval responsibilities
    during absences (OOO, vacation, etc.).
    """

    delegator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='delegations_given',
        help_text='Manager delegating their approval authority',
    )
    delegate = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='delegations_received',
        help_text='Manager receiving approval authority',
    )
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        ordering = ['-start_date']

    def __str__(self) -> str:
        return f'{self.delegator.email} delegated to {self.delegate.email}'

    def is_active(self, as_of_date=None) -> bool:
        """Check if delegation is active for given date."""
        from datetime import date
        if as_of_date is None:
            as_of_date = date.today()
        return self.start_date <= as_of_date <= self.end_date
