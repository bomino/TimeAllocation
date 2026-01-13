"""
Tests for Timesheet Celery tasks - TDD approach.

Tasks:
- create_weekly_timesheets: Auto-create timesheets for all users at week start
- send_timesheet_submitted_notification: Notify manager when timesheet submitted
- send_timesheet_approved_notification: Notify user when timesheet approved
- send_timesheet_rejected_notification: Notify user when timesheet rejected
"""
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import patch, MagicMock

import pytest
import pytz
from django.utils import timezone

from apps.timesheets.models import Timesheet


@pytest.mark.django_db
class TestCreateWeeklyTimesheetsTask:
    """Tests for create_weekly_timesheets Celery task."""

    def test_creates_timesheets_for_all_active_users(
        self, user_factory, company
    ):
        """
        Given: Multiple active users in a company
        When: Running create_weekly_timesheets task
        Then: Timesheet created for each user
        """
        from apps.timesheets.tasks import create_weekly_timesheets

        user1 = user_factory()
        user2 = user_factory()
        user3 = user_factory()

        result = create_weekly_timesheets()

        assert Timesheet.objects.filter(user=user1).exists()
        assert Timesheet.objects.filter(user=user2).exists()
        assert Timesheet.objects.filter(user=user3).exists()
        assert result['created'] == 3

    def test_uses_company_week_start_day(self, user_factory, company):
        """
        Given: Company with week_start_day = MONDAY (0)
        When: Running task on Wednesday
        Then: Timesheet week_start is the previous Monday
        """
        from apps.timesheets.tasks import create_weekly_timesheets
        from apps.companies.models import Company

        company.week_start_day = Company.WeekDay.MONDAY
        company.save()

        user = user_factory(company=company)

        with patch('apps.timesheets.tasks.timezone.now') as mock_now:
            mock_now.return_value = timezone.make_aware(
                timezone.datetime(2024, 6, 12, 10, 0, 0),  # Wednesday
                pytz.UTC
            )
            create_weekly_timesheets()

        timesheet = Timesheet.objects.get(user=user)
        assert timesheet.week_start == date(2024, 6, 10)  # Monday

    def test_skips_existing_timesheets(self, user_factory, company):
        """
        Given: User already has timesheet for current week
        When: Running create_weekly_timesheets task
        Then: No duplicate created
        """
        from apps.timesheets.tasks import create_weekly_timesheets

        user = user_factory()
        week_start = date(2024, 6, 10)
        Timesheet.objects.create(user=user, week_start=week_start)

        with patch('apps.timesheets.tasks.timezone.now') as mock_now:
            mock_now.return_value = timezone.make_aware(
                timezone.datetime(2024, 6, 12, 10, 0, 0),
                pytz.UTC
            )
            result = create_weekly_timesheets()

        assert Timesheet.objects.filter(user=user).count() == 1
        assert result['skipped'] == 1

    def test_skips_inactive_users(self, user_factory, company):
        """
        Given: An inactive user
        When: Running create_weekly_timesheets task
        Then: No timesheet created for inactive user
        """
        from apps.timesheets.tasks import create_weekly_timesheets

        active_user = user_factory(is_active=True)
        inactive_user = user_factory(is_active=False)

        result = create_weekly_timesheets()

        assert Timesheet.objects.filter(user=active_user).exists()
        assert not Timesheet.objects.filter(user=inactive_user).exists()

    def test_handles_multiple_companies(self, user_factory, company_factory):
        """
        Given: Users in different companies with different week starts
        When: Running create_weekly_timesheets task
        Then: Each user gets timesheet with their company's week start
        """
        from apps.timesheets.tasks import create_weekly_timesheets
        from apps.companies.models import Company

        company1 = company_factory(week_start_day=Company.WeekDay.MONDAY)
        company2 = company_factory(week_start_day=Company.WeekDay.SUNDAY)

        user1 = user_factory(company=company1)
        user2 = user_factory(company=company2)

        with patch('apps.timesheets.tasks.timezone.now') as mock_now:
            mock_now.return_value = timezone.make_aware(
                timezone.datetime(2024, 6, 12, 10, 0, 0),  # Wednesday
                pytz.UTC
            )
            create_weekly_timesheets()

        ts1 = Timesheet.objects.get(user=user1)
        ts2 = Timesheet.objects.get(user=user2)

        assert ts1.week_start == date(2024, 6, 10)  # Monday
        assert ts2.week_start == date(2024, 6, 9)   # Sunday

    def test_returns_summary_stats(self, user_factory):
        """
        Given: Mix of new and existing users
        When: Running create_weekly_timesheets task
        Then: Returns dict with created/skipped/failed counts
        """
        from apps.timesheets.tasks import create_weekly_timesheets

        user1 = user_factory()
        user2 = user_factory()

        week_start = date.today() - timedelta(days=date.today().weekday())
        Timesheet.objects.create(user=user1, week_start=week_start)

        result = create_weekly_timesheets()

        assert 'created' in result
        assert 'skipped' in result
        assert 'failed' in result
        assert result['created'] == 1
        assert result['skipped'] == 1


@pytest.mark.django_db
class TestSendTimesheetSubmittedNotification:
    """Tests for send_timesheet_submitted_notification task."""

    @patch('apps.infrastructure.notifications.send_notification.delay')
    def test_notifies_manager_on_submission(
        self, mock_send, user, manager
    ):
        """
        Given: User submits timesheet
        When: Task is called
        Then: Manager receives notification
        """
        from apps.timesheets.tasks import send_timesheet_submitted_notification

        timesheet = Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
            status=Timesheet.Status.SUBMITTED,
        )

        send_timesheet_submitted_notification(timesheet.id)

        mock_send.assert_called_once()
        call_args = mock_send.call_args
        assert call_args[0][0] == manager.id
        assert call_args[0][1] == 'timesheet_submitted'

    @patch('apps.infrastructure.notifications.send_notification.delay')
    def test_includes_timesheet_details_in_context(
        self, mock_send, user, manager
    ):
        """
        Given: User submits timesheet
        When: Task is called
        Then: Notification context includes timesheet details
        """
        from apps.timesheets.tasks import send_timesheet_submitted_notification

        timesheet = Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
            status=Timesheet.Status.SUBMITTED,
        )

        send_timesheet_submitted_notification(timesheet.id)

        call_args = mock_send.call_args
        context = call_args[0][2]
        assert 'timesheet_id' in context
        assert 'employee_name' in context
        assert 'week_start' in context

    @patch('apps.infrastructure.notifications.send_notification.delay')
    def test_no_notification_if_no_manager(self, mock_send, user_factory):
        """
        Given: User has no manager
        When: Task is called
        Then: No notification sent
        """
        from apps.timesheets.tasks import send_timesheet_submitted_notification

        user = user_factory(manager=None)
        timesheet = Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
            status=Timesheet.Status.SUBMITTED,
        )

        send_timesheet_submitted_notification(timesheet.id)

        mock_send.assert_not_called()


@pytest.mark.django_db
class TestSendTimesheetApprovedNotification:
    """Tests for send_timesheet_approved_notification task."""

    @patch('apps.infrastructure.notifications.send_notification.delay')
    def test_notifies_user_on_approval(self, mock_send, user, manager):
        """
        Given: Manager approves timesheet
        When: Task is called
        Then: User receives approval notification
        """
        from apps.timesheets.tasks import send_timesheet_approved_notification

        timesheet = Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
            status=Timesheet.Status.APPROVED,
            approved_by=manager,
        )

        send_timesheet_approved_notification(timesheet.id)

        mock_send.assert_called_once()
        call_args = mock_send.call_args
        assert call_args[0][0] == user.id
        assert call_args[0][1] == 'timesheet_approved'

    @patch('apps.infrastructure.notifications.send_notification.delay')
    def test_includes_approver_in_context(self, mock_send, user, manager):
        """
        Given: Manager approves timesheet
        When: Task is called
        Then: Context includes approver name
        """
        from apps.timesheets.tasks import send_timesheet_approved_notification

        timesheet = Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
            status=Timesheet.Status.APPROVED,
            approved_by=manager,
        )

        send_timesheet_approved_notification(timesheet.id)

        call_args = mock_send.call_args
        context = call_args[0][2]
        assert 'approver_name' in context


@pytest.mark.django_db
class TestSendTimesheetRejectedNotification:
    """Tests for send_timesheet_rejected_notification task."""

    @patch('apps.infrastructure.notifications.send_notification.delay')
    def test_notifies_user_on_rejection(self, mock_send, user, manager):
        """
        Given: Manager rejects timesheet
        When: Task is called
        Then: User receives rejection notification
        """
        from apps.timesheets.tasks import send_timesheet_rejected_notification

        timesheet = Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
            status=Timesheet.Status.REJECTED,
        )

        send_timesheet_rejected_notification(timesheet.id)

        mock_send.assert_called_once()
        call_args = mock_send.call_args
        assert call_args[0][0] == user.id
        assert call_args[0][1] == 'timesheet_rejected'

    @patch('apps.infrastructure.notifications.send_notification.delay')
    def test_includes_rejection_comments(self, mock_send, user, manager):
        """
        Given: Manager rejects timesheet with comments
        When: Task is called
        Then: Context includes comments
        """
        from apps.timesheets.tasks import send_timesheet_rejected_notification
        from apps.timesheets.models import TimesheetComment

        timesheet = Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
            status=Timesheet.Status.REJECTED,
        )
        TimesheetComment.objects.create(
            timesheet=timesheet,
            author=manager,
            text='Please fix hours on Monday.',
        )

        send_timesheet_rejected_notification(timesheet.id)

        call_args = mock_send.call_args
        context = call_args[0][2]
        assert 'comments' in context
        assert len(context['comments']) == 1


@pytest.mark.django_db
class TestTimesheetTaskIntegration:
    """Integration tests for timesheet task triggering."""

    @patch('apps.timesheets.tasks.send_timesheet_submitted_notification.delay')
    def test_submit_action_queues_notification(
        self, mock_task, authenticated_client, user, manager, project
    ):
        """
        Given: User submits timesheet via API
        When: Submit endpoint is called
        Then: Notification task is queued
        """
        from apps.timeentries.models import TimeEntry

        timesheet = Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
            status=Timesheet.Status.DRAFT,
        )
        TimeEntry.objects.create(
            user=user, project=project, timesheet=timesheet,
            date=date(2024, 6, 10), hours=Decimal('8.00'),
            billing_rate=Decimal('100.00'),
            rate_source=TimeEntry.RateSource.PROJECT,
        )

        response = authenticated_client.post(f'/api/v1/timesheets/{timesheet.id}/submit/')

        assert response.status_code == 200
        mock_task.assert_called_once_with(timesheet.id)

    @patch('apps.timesheets.tasks.send_timesheet_approved_notification.delay')
    def test_approve_action_queues_notification(
        self, mock_task, authenticated_manager_client, user
    ):
        """
        Given: Manager approves timesheet via API
        When: Approve endpoint is called
        Then: Notification task is queued
        """
        timesheet = Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
            status=Timesheet.Status.SUBMITTED,
            submitted_at=timezone.now(),
        )

        response = authenticated_manager_client.post(
            f'/api/v1/timesheets/{timesheet.id}/approve/'
        )

        assert response.status_code == 200
        mock_task.assert_called_once_with(timesheet.id)

    @patch('apps.timesheets.tasks.send_timesheet_rejected_notification.delay')
    def test_reject_action_queues_notification(
        self, mock_task, authenticated_manager_client, user
    ):
        """
        Given: Manager rejects timesheet via API
        When: Reject endpoint is called
        Then: Notification task is queued
        """
        timesheet = Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
            status=Timesheet.Status.SUBMITTED,
        )

        response = authenticated_manager_client.post(
            f'/api/v1/timesheets/{timesheet.id}/reject/',
            {'comment': 'Please fix the hours.'},
        )

        assert response.status_code == 200
        mock_task.assert_called_once_with(timesheet.id)
