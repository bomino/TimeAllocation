"""
Notification service for TimeTrack Pro.

All notifications are sent asynchronously via Celery tasks.
"""
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string


class NotificationType:
    """Notification type constants."""
    TIMESHEET_SUBMITTED = 'timesheet_submitted'
    TIMESHEET_APPROVED = 'timesheet_approved'
    TIMESHEET_REJECTED = 'timesheet_rejected'
    ESCALATION_ALERT = 'escalation_alert'
    PASSWORD_RESET = 'password_reset'
    ACCOUNT_LOCKED = 'account_locked'
    DAILY_REMINDER = 'daily_reminder'
    WEEKLY_REMINDER = 'weekly_reminder'


NOTIFICATION_SUBJECTS = {
    NotificationType.TIMESHEET_SUBMITTED: 'Timesheet Submitted for Approval',
    NotificationType.TIMESHEET_APPROVED: 'Your Timesheet Has Been Approved',
    NotificationType.TIMESHEET_REJECTED: 'Your Timesheet Requires Attention',
    NotificationType.ESCALATION_ALERT: 'Timesheet Requires Your Approval',
    NotificationType.PASSWORD_RESET: 'Password Reset Request',
    NotificationType.ACCOUNT_LOCKED: 'Account Security Alert',
    NotificationType.DAILY_REMINDER: 'Time Entry Reminder',
    NotificationType.WEEKLY_REMINDER: 'Timesheet Submission Reminder',
}

SECURITY_NOTIFICATIONS = {
    NotificationType.PASSWORD_RESET,
    NotificationType.ACCOUNT_LOCKED,
}


@shared_task
def send_notification(user_id: int, notification_type: str, context: dict) -> bool:
    """
    Send a notification to a user.

    Args:
        user_id: ID of the user to notify
        notification_type: Type of notification (from NotificationType)
        context: Template context for the notification

    Returns:
        True if notification was sent, False if skipped due to preferences
    """
    from apps.users.models import User

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return False

    is_security = notification_type in SECURITY_NOTIFICATIONS

    if is_security:
        if not user.security_notifications_enabled:
            return False
    else:
        if not user.workflow_notifications_enabled:
            return False

    subject = NOTIFICATION_SUBJECTS.get(
        notification_type,
        'TimeTrack Pro Notification'
    )

    context['user'] = user
    context['notification_type'] = notification_type

    try:
        html_content = render_to_string(
            f'emails/{notification_type}.html',
            context
        )
        text_content = render_to_string(
            f'emails/{notification_type}.txt',
            context
        )
    except Exception:
        html_content = None
        text_content = _generate_fallback_message(notification_type, context)

    send_mail(
        subject=subject,
        message=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_content,
        fail_silently=False,
    )

    return True


def _generate_fallback_message(notification_type: str, context: dict) -> str:
    """Generate a fallback plain text message when template is missing."""
    messages = {
        NotificationType.TIMESHEET_SUBMITTED: (
            "A timesheet has been submitted for your approval."
        ),
        NotificationType.TIMESHEET_APPROVED: (
            "Your timesheet has been approved."
        ),
        NotificationType.TIMESHEET_REJECTED: (
            "Your timesheet requires attention. Please review the comments."
        ),
        NotificationType.ESCALATION_ALERT: (
            "A timesheet has been escalated to you for approval."
        ),
        NotificationType.PASSWORD_RESET: (
            f"Your password reset link: {context.get('reset_url', 'N/A')}"
        ),
        NotificationType.ACCOUNT_LOCKED: (
            "Your account has been locked due to security concerns."
        ),
        NotificationType.DAILY_REMINDER: (
            "Reminder: Please log your time entries for today."
        ),
        NotificationType.WEEKLY_REMINDER: (
            "Reminder: Please submit your timesheet for this week."
        ),
    }
    return messages.get(notification_type, "You have a new notification.")


def queue_notification(user_id: int, notification_type: str, context: dict) -> None:
    """
    Queue a notification for async delivery.

    This is the primary interface for sending notifications.
    """
    send_notification.delay(user_id, notification_type, context)


def queue_bulk_notifications(
    user_ids: list[int],
    notification_type: str,
    context: dict
) -> None:
    """
    Queue notifications for multiple users.

    Args:
        user_ids: List of user IDs to notify
        notification_type: Type of notification
        context: Shared context for all notifications
    """
    for user_id in user_ids:
        send_notification.delay(user_id, notification_type, context)
