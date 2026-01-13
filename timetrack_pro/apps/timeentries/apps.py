"""TimeEntries app configuration."""
from django.apps import AppConfig


class TimeentriesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.timeentries'
    verbose_name = 'Time Entries'
