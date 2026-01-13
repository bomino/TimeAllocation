"""
User model for TimeTrack Pro.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models

from core.models import TimeStampedModel


class User(AbstractUser, TimeStampedModel):
    """
    Custom user model for TimeTrack Pro.

    Extends Django's AbstractUser with additional fields for:
    - Role-based access control
    - Manager hierarchy
    - Notification preferences
    - Company membership
    """

    class Role(models.TextChoices):
        EMPLOYEE = 'EMPLOYEE', 'Employee'
        MANAGER = 'MANAGER', 'Manager'
        ADMIN = 'ADMIN', 'Admin'

    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.EMPLOYEE
    )
    manager = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='direct_reports'
    )
    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='employees'
    )
    timezone = models.CharField(max_length=50, default='UTC')
    workflow_notifications_enabled = models.BooleanField(default=True)
    security_notifications_enabled = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['company', 'role']),
        ]

    def __str__(self):
        return self.get_full_name()

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'.strip()

    @property
    def is_manager(self) -> bool:
        """Check if user can approve timesheets (manager or admin)."""
        return self.role in (self.Role.MANAGER, self.Role.ADMIN)

    @property
    def is_admin(self) -> bool:
        """Check if user has admin privileges."""
        return self.role == self.Role.ADMIN

    def get_approval_chain(self) -> list['User']:
        """
        Get the chain of managers up to the top.

        Returns list starting with direct manager up to top-level manager.
        """
        chain = []
        current = self.manager
        seen = set()

        while current and current.id not in seen:
            chain.append(current)
            seen.add(current.id)
            current = current.manager

        return chain


class UserDeactivationAudit(models.Model):
    """
    Audit record for user deactivation.

    Stores exported user data (JSON + base64 CSV) for compliance.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='deactivation_audits',
    )
    admin = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='deactivations_performed',
    )
    reason = models.TextField()
    was_forced = models.BooleanField(default=False)
    pending_timesheets_at_deactivation = models.IntegerField(default=0)
    export_data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'User Deactivation Audit'
        verbose_name_plural = 'User Deactivation Audits'

    def __str__(self) -> str:
        return f'Deactivation of {self.user.email} by {self.admin.email if self.admin else "Unknown"}'
