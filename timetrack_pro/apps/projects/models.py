"""
Project models for TimeTrack Pro.

Placeholder for Slice 2 implementation.
"""
from django.db import models

from core.models import TimeStampedModel


class Project(TimeStampedModel):
    """Project entity for time tracking."""

    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        INACTIVE = 'INACTIVE', 'Inactive'
        ARCHIVED = 'ARCHIVED', 'Archived'

    name = models.CharField(max_length=255)
    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='projects',
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    description = models.TextField(blank=True)

    class Meta:
        unique_together = ['company', 'name']

    def __str__(self) -> str:
        return self.name
