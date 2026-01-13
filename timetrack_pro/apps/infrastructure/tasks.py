"""
Shared Celery task utilities for TimeTrack Pro.
"""
from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@shared_task(bind=True, max_retries=3)
def retry_on_failure(self, task_name: str, *args, **kwargs):
    """
    Generic retry wrapper for tasks.

    Usage:
        retry_on_failure.delay('apps.timesheets.tasks.send_reminder', user_id=123)
    """
    from django.utils.module_loading import import_string

    try:
        task_func = import_string(task_name)
        return task_func(*args, **kwargs)
    except Exception as exc:
        logger.error(f"Task {task_name} failed: {exc}")
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))
