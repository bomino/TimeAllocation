"""
Tests for Escalation Service - TDD approach.

Business Rules:
- Escalation trigger: OOO status OR pending X days (configurable AND/OR)
- Escalation chain: user.manager → manager.manager → ... → admin notification
- Chain terminus: Notify admin when no higher manager
"""
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import patch

import pytest
from django.utils import timezone

from apps.companies.models import CompanySettings
from apps.timesheets.models import OOOPeriod, Timesheet


@pytest.mark.django_db
class TestEscalationServiceOOOCheck:
    """Tests for OOO-based escalation logic."""

    def test_manager_is_ooo_returns_true(self, user, manager):
        """
        Given: Manager has an active OOO period
        When: Checking if manager is OOO
        Then: Returns True
        """
        from apps.timesheets.services import EscalationService

        OOOPeriod.objects.create(
            user=manager,
            start_date=date.today() - timedelta(days=1),
            end_date=date.today() + timedelta(days=5),
        )

        assert EscalationService.is_user_ooo(manager) is True

    def test_manager_not_ooo_returns_false(self, user, manager):
        """
        Given: Manager has no active OOO period
        When: Checking if manager is OOO
        Then: Returns False
        """
        from apps.timesheets.services import EscalationService

        assert EscalationService.is_user_ooo(manager) is False

    def test_manager_ooo_in_past_returns_false(self, user, manager):
        """
        Given: Manager's OOO period ended yesterday
        When: Checking if manager is OOO
        Then: Returns False
        """
        from apps.timesheets.services import EscalationService

        OOOPeriod.objects.create(
            user=manager,
            start_date=date.today() - timedelta(days=10),
            end_date=date.today() - timedelta(days=1),
        )

        assert EscalationService.is_user_ooo(manager) is False

    def test_manager_ooo_in_future_returns_false(self, user, manager):
        """
        Given: Manager's OOO period starts tomorrow
        When: Checking if manager is OOO
        Then: Returns False
        """
        from apps.timesheets.services import EscalationService

        OOOPeriod.objects.create(
            user=manager,
            start_date=date.today() + timedelta(days=1),
            end_date=date.today() + timedelta(days=7),
        )

        assert EscalationService.is_user_ooo(manager) is False

    def test_ooo_check_on_boundary_start_date(self, user, manager):
        """
        Given: Manager's OOO starts today
        When: Checking if manager is OOO
        Then: Returns True
        """
        from apps.timesheets.services import EscalationService

        OOOPeriod.objects.create(
            user=manager,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=5),
        )

        assert EscalationService.is_user_ooo(manager) is True

    def test_ooo_check_on_boundary_end_date(self, user, manager):
        """
        Given: Manager's OOO ends today
        When: Checking if manager is OOO
        Then: Returns True (inclusive)
        """
        from apps.timesheets.services import EscalationService

        OOOPeriod.objects.create(
            user=manager,
            start_date=date.today() - timedelta(days=5),
            end_date=date.today(),
        )

        assert EscalationService.is_user_ooo(manager) is True


@pytest.mark.django_db
class TestEscalationServicePendingDays:
    """Tests for pending days escalation logic."""

    def test_timesheet_pending_over_threshold_returns_true(self, user):
        """
        Given: Timesheet submitted 5 days ago, threshold is 3 days
        When: Checking if pending too long
        Then: Returns True
        """
        from apps.timesheets.services import EscalationService

        user.company.settings.escalation_days = 3
        user.company.settings.save()

        timesheet = Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
            status=Timesheet.Status.SUBMITTED,
            submitted_at=timezone.now() - timedelta(days=5),
        )

        assert EscalationService.is_pending_too_long(timesheet) is True

    def test_timesheet_pending_under_threshold_returns_false(self, user):
        """
        Given: Timesheet submitted 1 day ago, threshold is 3 days
        When: Checking if pending too long
        Then: Returns False
        """
        from apps.timesheets.services import EscalationService

        user.company.settings.escalation_days = 3
        user.company.settings.save()

        timesheet = Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
            status=Timesheet.Status.SUBMITTED,
            submitted_at=timezone.now() - timedelta(days=1),
        )

        assert EscalationService.is_pending_too_long(timesheet) is False

    def test_timesheet_pending_exactly_threshold_returns_false(self, user):
        """
        Given: Timesheet submitted exactly 3 days ago, threshold is 3 days
        When: Checking if pending too long
        Then: Returns False (must exceed, not equal)
        """
        from apps.timesheets.services import EscalationService

        user.company.settings.escalation_days = 3
        user.company.settings.save()

        timesheet = Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
            status=Timesheet.Status.SUBMITTED,
            submitted_at=timezone.now() - timedelta(days=3),
        )

        assert EscalationService.is_pending_too_long(timesheet) is False


@pytest.mark.django_db
class TestEscalationServiceTriggerLogic:
    """Tests for OR/AND escalation logic configuration."""

    def test_or_logic_ooo_only_triggers(self, user, manager):
        """
        Given: OR logic, manager is OOO, timesheet not pending too long
        When: Checking if should escalate
        Then: Returns True (OOO alone triggers)
        """
        from apps.timesheets.services import EscalationService

        user.company.settings.escalation_logic = CompanySettings.EscalationLogic.OR
        user.company.settings.escalation_days = 3
        user.company.settings.save()

        OOOPeriod.objects.create(
            user=manager,
            start_date=date.today() - timedelta(days=1),
            end_date=date.today() + timedelta(days=5),
        )

        timesheet = Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
            status=Timesheet.Status.SUBMITTED,
            submitted_at=timezone.now() - timedelta(days=1),
        )

        assert EscalationService.should_escalate(timesheet) is True

    def test_or_logic_pending_only_triggers(self, user, manager):
        """
        Given: OR logic, manager not OOO, timesheet pending too long
        When: Checking if should escalate
        Then: Returns True (pending alone triggers)
        """
        from apps.timesheets.services import EscalationService

        user.company.settings.escalation_logic = CompanySettings.EscalationLogic.OR
        user.company.settings.escalation_days = 3
        user.company.settings.save()

        timesheet = Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
            status=Timesheet.Status.SUBMITTED,
            submitted_at=timezone.now() - timedelta(days=5),
        )

        assert EscalationService.should_escalate(timesheet) is True

    def test_or_logic_neither_does_not_trigger(self, user, manager):
        """
        Given: OR logic, manager not OOO, timesheet not pending too long
        When: Checking if should escalate
        Then: Returns False
        """
        from apps.timesheets.services import EscalationService

        user.company.settings.escalation_logic = CompanySettings.EscalationLogic.OR
        user.company.settings.escalation_days = 3
        user.company.settings.save()

        timesheet = Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
            status=Timesheet.Status.SUBMITTED,
            submitted_at=timezone.now() - timedelta(days=1),
        )

        assert EscalationService.should_escalate(timesheet) is False

    def test_and_logic_both_required_triggers(self, user, manager):
        """
        Given: AND logic, manager is OOO AND timesheet pending too long
        When: Checking if should escalate
        Then: Returns True
        """
        from apps.timesheets.services import EscalationService

        user.company.settings.escalation_logic = CompanySettings.EscalationLogic.AND
        user.company.settings.escalation_days = 3
        user.company.settings.save()

        OOOPeriod.objects.create(
            user=manager,
            start_date=date.today() - timedelta(days=1),
            end_date=date.today() + timedelta(days=5),
        )

        timesheet = Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
            status=Timesheet.Status.SUBMITTED,
            submitted_at=timezone.now() - timedelta(days=5),
        )

        assert EscalationService.should_escalate(timesheet) is True

    def test_and_logic_ooo_only_does_not_trigger(self, user, manager):
        """
        Given: AND logic, manager is OOO, timesheet NOT pending too long
        When: Checking if should escalate
        Then: Returns False (both required)
        """
        from apps.timesheets.services import EscalationService

        user.company.settings.escalation_logic = CompanySettings.EscalationLogic.AND
        user.company.settings.escalation_days = 3
        user.company.settings.save()

        OOOPeriod.objects.create(
            user=manager,
            start_date=date.today() - timedelta(days=1),
            end_date=date.today() + timedelta(days=5),
        )

        timesheet = Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
            status=Timesheet.Status.SUBMITTED,
            submitted_at=timezone.now() - timedelta(days=1),
        )

        assert EscalationService.should_escalate(timesheet) is False

    def test_and_logic_pending_only_does_not_trigger(self, user, manager):
        """
        Given: AND logic, manager NOT OOO, timesheet pending too long
        When: Checking if should escalate
        Then: Returns False (both required)
        """
        from apps.timesheets.services import EscalationService

        user.company.settings.escalation_logic = CompanySettings.EscalationLogic.AND
        user.company.settings.escalation_days = 3
        user.company.settings.save()

        timesheet = Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
            status=Timesheet.Status.SUBMITTED,
            submitted_at=timezone.now() - timedelta(days=5),
        )

        assert EscalationService.should_escalate(timesheet) is False


@pytest.mark.django_db
class TestEscalationServiceChain:
    """Tests for escalation chain traversal."""

    def test_escalate_to_next_manager_in_chain(self, user, manager, user_factory):
        """
        Given: User → Manager → Senior Manager chain
        When: Escalating from manager
        Then: Returns senior manager
        """
        from apps.timesheets.services import EscalationService
        from apps.users.models import User

        senior_manager = user_factory(role=User.Role.MANAGER)
        manager.manager = senior_manager
        manager.save()

        timesheet = Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
            status=Timesheet.Status.SUBMITTED,
        )

        next_approver = EscalationService.get_next_approver(timesheet, manager)
        assert next_approver == senior_manager

    def test_escalate_returns_none_at_chain_end(self, user, manager):
        """
        Given: Manager has no manager (top of chain)
        When: Getting next approver
        Then: Returns None
        """
        from apps.timesheets.services import EscalationService

        timesheet = Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
            status=Timesheet.Status.SUBMITTED,
        )

        next_approver = EscalationService.get_next_approver(timesheet, manager)
        assert next_approver is None

    def test_escalate_skips_ooo_manager(self, user, manager, user_factory):
        """
        Given: Manager → Senior (OOO) → Director chain
        When: Escalating, senior is OOO
        Then: Skips senior, returns director
        """
        from apps.timesheets.services import EscalationService
        from apps.users.models import User

        senior_manager = user_factory(role=User.Role.MANAGER)
        director = user_factory(role=User.Role.MANAGER)

        manager.manager = senior_manager
        manager.save()
        senior_manager.manager = director
        senior_manager.save()

        OOOPeriod.objects.create(
            user=senior_manager,
            start_date=date.today() - timedelta(days=1),
            end_date=date.today() + timedelta(days=5),
        )

        timesheet = Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
            status=Timesheet.Status.SUBMITTED,
        )

        next_approver = EscalationService.get_next_approver(timesheet, manager)
        assert next_approver == director

    def test_escalate_all_ooo_returns_none(self, user, manager, user_factory):
        """
        Given: All managers in chain are OOO
        When: Getting next approver
        Then: Returns None (will notify admin)
        """
        from apps.timesheets.services import EscalationService
        from apps.users.models import User

        senior_manager = user_factory(role=User.Role.MANAGER)
        manager.manager = senior_manager
        manager.save()

        OOOPeriod.objects.create(
            user=senior_manager,
            start_date=date.today() - timedelta(days=1),
            end_date=date.today() + timedelta(days=5),
        )

        timesheet = Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
            status=Timesheet.Status.SUBMITTED,
        )

        next_approver = EscalationService.get_next_approver(timesheet, manager)
        assert next_approver is None


@pytest.mark.django_db
class TestEscalationServiceExecute:
    """Tests for executing escalation."""

    @patch('apps.infrastructure.notifications.send_notification.delay')
    def test_execute_escalation_notifies_next_approver(
        self, mock_notify, user, manager, user_factory
    ):
        """
        Given: Timesheet needs escalation
        When: Executing escalation
        Then: Next approver is notified
        """
        from apps.timesheets.services import EscalationService
        from apps.users.models import User

        senior_manager = user_factory(role=User.Role.MANAGER)
        manager.manager = senior_manager
        manager.save()

        timesheet = Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
            status=Timesheet.Status.SUBMITTED,
        )

        result = EscalationService.execute_escalation(timesheet, manager)

        assert result['escalated_to'] == senior_manager
        mock_notify.assert_called_once()
        call_args = mock_notify.call_args
        assert call_args[0][0] == senior_manager.id
        assert call_args[0][1] == 'escalation_alert'

    @patch('apps.infrastructure.notifications.send_notification.delay')
    def test_execute_escalation_notifies_admins_at_chain_end(
        self, mock_notify, user, manager, admin
    ):
        """
        Given: No more managers in chain
        When: Executing escalation
        Then: Admin is notified
        """
        from apps.timesheets.services import EscalationService

        timesheet = Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
            status=Timesheet.Status.SUBMITTED,
        )

        result = EscalationService.execute_escalation(timesheet, manager)

        assert result['escalated_to'] is None
        assert result['admin_notified'] is True
        mock_notify.assert_called()

    def test_execute_escalation_returns_result(self, user, manager, user_factory):
        """
        Given: Timesheet escalation
        When: Executing
        Then: Returns dict with escalation details
        """
        from apps.timesheets.services import EscalationService
        from apps.users.models import User

        senior_manager = user_factory(role=User.Role.MANAGER)
        manager.manager = senior_manager
        manager.save()

        timesheet = Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
            status=Timesheet.Status.SUBMITTED,
        )

        with patch('apps.infrastructure.notifications.send_notification.delay'):
            result = EscalationService.execute_escalation(timesheet, manager)

        assert 'escalated_to' in result
        assert 'escalated_from' in result
        assert 'timesheet_id' in result


@pytest.mark.django_db
class TestCheckPendingEscalationsTask:
    """Tests for the Celery task that checks for escalations."""

    def test_task_finds_submitted_timesheets(self, user, manager):
        """
        Given: Multiple submitted timesheets
        When: Running check_pending_escalations task
        Then: All submitted timesheets are checked
        """
        from apps.timesheets.tasks import check_pending_escalations

        user.company.settings.escalation_logic = CompanySettings.EscalationLogic.OR
        user.company.settings.escalation_days = 3
        user.company.settings.save()

        Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
            status=Timesheet.Status.SUBMITTED,
            submitted_at=timezone.now() - timedelta(days=5),
        )
        Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 17),
            status=Timesheet.Status.DRAFT,
        )

        with patch('apps.timesheets.services.EscalationService.execute_escalation') as mock_exec:
            result = check_pending_escalations()

        assert result['checked'] >= 1
        assert mock_exec.called

    def test_task_skips_non_submitted_timesheets(self, user):
        """
        Given: Timesheets in draft/approved/rejected status
        When: Running check_pending_escalations task
        Then: Only submitted timesheets are processed
        """
        from apps.timesheets.tasks import check_pending_escalations

        Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 3),
            status=Timesheet.Status.DRAFT,
        )
        Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
            status=Timesheet.Status.APPROVED,
        )
        Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 17),
            status=Timesheet.Status.REJECTED,
        )

        with patch('apps.timesheets.services.EscalationService.should_escalate') as mock_check:
            result = check_pending_escalations()

        assert result['checked'] == 0
        mock_check.assert_not_called()

    def test_task_returns_summary(self, user, manager):
        """
        Given: Mix of escalatable and non-escalatable timesheets
        When: Running check_pending_escalations task
        Then: Returns summary with checked/escalated/failed counts
        """
        from apps.timesheets.tasks import check_pending_escalations

        user.company.settings.escalation_logic = CompanySettings.EscalationLogic.OR
        user.company.settings.escalation_days = 3
        user.company.settings.save()

        Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
            status=Timesheet.Status.SUBMITTED,
            submitted_at=timezone.now() - timedelta(days=5),
        )

        with patch('apps.timesheets.services.EscalationService.execute_escalation'):
            result = check_pending_escalations()

        assert 'checked' in result
        assert 'escalated' in result
        assert 'skipped' in result


@pytest.mark.django_db
class TestOOOPeriodConstraints:
    """Tests for OOO period business rules."""

    def test_user_can_have_one_active_ooo(self, user):
        """
        Given: User with active OOO
        When: Creating another active OOO
        Then: Validation error
        """
        from apps.timesheets.services import OOOService

        OOOPeriod.objects.create(
            user=user,
            start_date=date.today() - timedelta(days=1),
            end_date=date.today() + timedelta(days=5),
        )

        with pytest.raises(ValueError, match='active'):
            OOOService.create_ooo_period(
                user=user,
                start_date=date.today(),
                end_date=date.today() + timedelta(days=3),
            )

    def test_user_can_have_one_future_ooo(self, user):
        """
        Given: User with active OOO + future OOO
        When: Creating another future OOO
        Then: Validation error
        """
        from apps.timesheets.services import OOOService

        OOOPeriod.objects.create(
            user=user,
            start_date=date.today() - timedelta(days=1),
            end_date=date.today() + timedelta(days=5),
        )
        OOOPeriod.objects.create(
            user=user,
            start_date=date.today() + timedelta(days=10),
            end_date=date.today() + timedelta(days=15),
        )

        with pytest.raises(ValueError, match='future'):
            OOOService.create_ooo_period(
                user=user,
                start_date=date.today() + timedelta(days=20),
                end_date=date.today() + timedelta(days=25),
            )

    def test_user_can_have_active_plus_future(self, user):
        """
        Given: User with active OOO
        When: Creating one future OOO
        Then: Succeeds
        """
        from apps.timesheets.services import OOOService

        OOOPeriod.objects.create(
            user=user,
            start_date=date.today() - timedelta(days=1),
            end_date=date.today() + timedelta(days=5),
        )

        future_ooo = OOOService.create_ooo_period(
            user=user,
            start_date=date.today() + timedelta(days=10),
            end_date=date.today() + timedelta(days=15),
        )

        assert future_ooo.pk is not None
