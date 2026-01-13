"""
Celery tasks for User app - all email notifications.
"""
from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

logger = get_task_logger(__name__)


@shared_task
def send_password_reset_email(user_id: int):
    """
    Send password reset email to user.

    Args:
        user_id: The user's database ID
    """
    from apps.users.models import User

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        logger.warning(f'Password reset requested for non-existent user {user_id}')
        return

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    # In production, replace with your frontend URL
    reset_url = f'{settings.FRONTEND_URL}/reset-password?uid={uid}&token={token}'

    subject = 'Password Reset Request - TimeTrack Pro'
    message = f'''
Hello {user.get_full_name()},

You requested a password reset for your TimeTrack Pro account.

Click the link below to reset your password:
{reset_url}

This link will expire in 24 hours.

If you did not request this reset, please ignore this email.

Thanks,
TimeTrack Pro Team
'''

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )

    logger.info(f'Password reset email sent to {user.email}')


@shared_task
def send_password_changed_notification(user_id: int):
    """
    Send notification when password has been changed.

    Only sends if user has security_notifications_enabled.

    Args:
        user_id: The user's database ID
    """
    from apps.users.models import User

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        logger.warning(f'Password changed notification for non-existent user {user_id}')
        return

    if not user.security_notifications_enabled:
        logger.info(f'Security notifications disabled for user {user.email}')
        return

    subject = 'Password Changed - TimeTrack Pro'
    message = f'''
Hello {user.get_full_name()},

Your TimeTrack Pro password was recently changed.

If you made this change, no action is needed.

If you did NOT make this change, please contact support immediately and reset your password.

Thanks,
TimeTrack Pro Team
'''

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )

    logger.info(f'Password changed notification sent to {user.email}')
