"""
Celery configuration for TimeTrack Pro.
"""
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

app = Celery('timetrack_pro')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'create-weekly-timesheets': {
        'task': 'apps.timesheets.tasks.create_weekly_timesheets',
        'schedule': crontab(hour=0, minute=5, day_of_week=1),  # Monday 00:05
    },
    'check-pending-escalations': {
        'task': 'apps.timesheets.tasks.check_pending_escalations',
        'schedule': crontab(hour=9, minute=0),  # Daily at 09:00
    },
}


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
