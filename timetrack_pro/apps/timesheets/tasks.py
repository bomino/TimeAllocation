"""
Celery tasks for Timesheet automation.

Tasks:
- create_weekly_timesheets: Auto-create timesheets for all users
- send_timesheet_submitted_notification: Notify manager on submission
- send_timesheet_approved_notification: Notify user on approval
- send_timesheet_rejected_notification: Notify user on rejection
"""
from datetime import date, timedelta

from celery import shared_task
from celery.utils.log import get_task_logger
from django.utils import timezone

logger = get_task_logger(__name__)


def get_week_start(target_date: date, week_start_day: int) -> date:
    """
    Calculate the start of the week containing target_date.

    Args:
        target_date: The date to find the week start for
        week_start_day: The day the week starts (0=Monday, 6=Sunday)

    Returns:
        The date of the week start
    """
    days_since_week_start = (target_date.weekday() - week_start_day) % 7
    return target_date - timedelta(days=days_since_week_start)


@shared_task
def create_weekly_timesheets() -> dict:
    """
    Create timesheets for all active users for the current week.

    Respects each company's week_start_day setting.
    Skips users who already have a timesheet for the current week.

    Returns:
        Dict with created/skipped/failed counts
    """
    from apps.timesheets.models import Timesheet
    from apps.users.models import User

    now = timezone.now()
    today = now.date()

    stats = {'created': 0, 'skipped': 0, 'failed': 0}

    active_users = User.objects.filter(
        is_active=True
    ).select_related('company')

    for user in active_users:
        try:
            week_start_day = user.company.week_start_day
            week_start = get_week_start(today, week_start_day)

            existing = Timesheet.objects.filter(
                user=user,
                week_start=week_start
            ).exists()

            if existing:
                stats['skipped'] += 1
                continue

            Timesheet.objects.create(
                user=user,
                week_start=week_start,
                status=Timesheet.Status.DRAFT,
            )
            stats['created'] += 1

        except Exception as e:
            logger.error(f"Failed to create timesheet for user {user.id}: {e}")
            stats['failed'] += 1

    logger.info(
        f"Weekly timesheets: created={stats['created']}, "
        f"skipped={stats['skipped']}, failed={stats['failed']}"
    )

    return stats


@shared_task
def send_timesheet_submitted_notification(timesheet_id: int) -> bool:
    """
    Send notification to manager when a timesheet is submitted.

    Args:
        timesheet_id: ID of the submitted timesheet

    Returns:
        True if notification was queued, False otherwise
    """
    from apps.infrastructure.notifications import send_notification
    from apps.timesheets.models import Timesheet

    try:
        timesheet = Timesheet.objects.select_related(
            'user', 'user__manager'
        ).get(id=timesheet_id)
    except Timesheet.DoesNotExist:
        logger.error(f"Timesheet {timesheet_id} not found")
        return False

    manager = timesheet.user.manager
    if not manager:
        logger.info(f"No manager for user {timesheet.user.id}, skipping notification")
        return False

    context = {
        'timesheet_id': timesheet.id,
        'employee_name': timesheet.user.get_full_name(),
        'week_start': str(timesheet.week_start),
    }

    send_notification.delay(manager.id, 'timesheet_submitted', context)
    return True


@shared_task
def send_timesheet_approved_notification(timesheet_id: int) -> bool:
    """
    Send notification to user when their timesheet is approved.

    Args:
        timesheet_id: ID of the approved timesheet

    Returns:
        True if notification was queued, False otherwise
    """
    from apps.infrastructure.notifications import send_notification
    from apps.timesheets.models import Timesheet

    try:
        timesheet = Timesheet.objects.select_related(
            'user', 'approved_by'
        ).get(id=timesheet_id)
    except Timesheet.DoesNotExist:
        logger.error(f"Timesheet {timesheet_id} not found")
        return False

    approver_name = ''
    if timesheet.approved_by:
        approver_name = timesheet.approved_by.get_full_name()

    context = {
        'timesheet_id': timesheet.id,
        'week_start': str(timesheet.week_start),
        'approver_name': approver_name,
    }

    send_notification.delay(timesheet.user.id, 'timesheet_approved', context)
    return True


@shared_task
def send_timesheet_rejected_notification(timesheet_id: int) -> bool:
    """
    Send notification to user when their timesheet is rejected.

    Args:
        timesheet_id: ID of the rejected timesheet

    Returns:
        True if notification was queued, False otherwise
    """
    from apps.infrastructure.notifications import send_notification
    from apps.timesheets.models import Timesheet

    try:
        timesheet = Timesheet.objects.select_related('user').prefetch_related(
            'comments'
        ).get(id=timesheet_id)
    except Timesheet.DoesNotExist:
        logger.error(f"Timesheet {timesheet_id} not found")
        return False

    comments = [
        {
            'author': comment.author.get_full_name() if comment.author else 'Unknown',
            'text': comment.text,
        }
        for comment in timesheet.comments.select_related('author').all()
    ]

    context = {
        'timesheet_id': timesheet.id,
        'week_start': str(timesheet.week_start),
        'comments': comments,
    }

    send_notification.delay(timesheet.user.id, 'timesheet_rejected', context)
    return True


@shared_task
def check_pending_escalations() -> dict:
    """
    Check all submitted timesheets and escalate where needed.

    Business Rules:
    - Only checks timesheets with SUBMITTED status
    - Uses company's escalation_logic (OR/AND) to determine if escalation needed
    - Executes escalation for qualifying timesheets

    Returns:
        Dict with checked/escalated/skipped counts
    """
    from apps.timesheets.models import Timesheet
    from apps.timesheets.services import EscalationService

    stats = {'checked': 0, 'escalated': 0, 'skipped': 0}

    submitted_timesheets = Timesheet.objects.filter(
        status=Timesheet.Status.SUBMITTED
    ).select_related('user', 'user__manager', 'user__company__settings')

    for timesheet in submitted_timesheets:
        stats['checked'] += 1

        try:
            if EscalationService.should_escalate(timesheet):
                manager = timesheet.user.manager
                if manager:
                    EscalationService.execute_escalation(timesheet, manager)
                    stats['escalated'] += 1
                else:
                    stats['skipped'] += 1
            else:
                stats['skipped'] += 1
        except Exception as e:
            logger.error(f"Failed to process escalation for timesheet {timesheet.id}: {e}")
            stats['skipped'] += 1

    logger.info(
        f"Escalation check: checked={stats['checked']}, "
        f"escalated={stats['escalated']}, skipped={stats['skipped']}"
    )

    return stats
