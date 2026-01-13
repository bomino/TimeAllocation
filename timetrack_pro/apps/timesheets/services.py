"""
Services for Timesheet business logic.

Includes:
- EscalationService: Handles approval chain escalation
- OOOService: Manages Out-of-Office period constraints
"""
from datetime import date
from typing import Optional

from django.db.models import Q
from django.utils import timezone

from apps.companies.models import CompanySettings
from apps.infrastructure.notifications import send_notification
from apps.timesheets.models import ApprovalDelegation, OOOPeriod, Timesheet
from apps.users.models import User


class EscalationService:
    """
    Service for handling timesheet approval escalation.

    Business Rules:
    - Escalation triggered by: OOO status OR/AND pending X days (configurable)
    - Escalation chain: user.manager → manager.manager → ... → admin notification
    - Skips OOO managers in the chain
    - Notifies admin when chain ends with no available approver
    """

    @classmethod
    def is_user_ooo(cls, user: User, check_date: date = None) -> bool:
        """
        Check if a user is currently Out-of-Office.

        Args:
            user: The user to check
            check_date: Date to check (defaults to today)

        Returns:
            True if user has an active OOO period, False otherwise
        """
        if check_date is None:
            check_date = date.today()

        return OOOPeriod.objects.filter(
            user=user,
            start_date__lte=check_date,
            end_date__gte=check_date,
        ).exists()

    @classmethod
    def is_pending_too_long(cls, timesheet: Timesheet) -> bool:
        """
        Check if a timesheet has been pending longer than the threshold.

        Args:
            timesheet: The submitted timesheet to check

        Returns:
            True if pending days exceed company threshold, False otherwise
        """
        if not timesheet.submitted_at:
            return False

        escalation_days = timesheet.user.company.settings.escalation_days
        days_pending = (timezone.now() - timesheet.submitted_at).days

        return days_pending > escalation_days

    @classmethod
    def should_escalate(cls, timesheet: Timesheet) -> bool:
        """
        Determine if a timesheet should be escalated.

        Uses company's escalation_logic setting:
        - OR: Escalate if manager is OOO OR pending too long
        - AND: Escalate only if manager is OOO AND pending too long

        Args:
            timesheet: The submitted timesheet to check

        Returns:
            True if escalation should occur, False otherwise
        """
        if timesheet.status != Timesheet.Status.SUBMITTED:
            return False

        manager = timesheet.user.manager
        if not manager:
            return False

        is_ooo = cls.is_user_ooo(manager)
        is_pending = cls.is_pending_too_long(timesheet)

        escalation_logic = timesheet.user.company.settings.escalation_logic

        if escalation_logic == CompanySettings.EscalationLogic.OR:
            return is_ooo or is_pending
        else:  # AND logic
            return is_ooo and is_pending

    @classmethod
    def get_next_approver(
        cls,
        timesheet: Timesheet,
        current_approver: User
    ) -> Optional[User]:
        """
        Find the next available approver in the chain.

        Skips managers who are currently OOO.

        Args:
            timesheet: The timesheet needing approval
            current_approver: The current approver to escalate from

        Returns:
            Next available approver, or None if chain ends
        """
        next_manager = current_approver.manager

        while next_manager:
            if not cls.is_user_ooo(next_manager):
                return next_manager
            next_manager = next_manager.manager

        return None

    @classmethod
    def execute_escalation(
        cls,
        timesheet: Timesheet,
        from_approver: User
    ) -> dict:
        """
        Execute an escalation for a timesheet.

        Finds the next approver and sends notifications.
        If no approver is available, notifies admins.

        Args:
            timesheet: The timesheet to escalate
            from_approver: The approver to escalate from

        Returns:
            Dict with escalation details
        """
        next_approver = cls.get_next_approver(timesheet, from_approver)

        result = {
            'timesheet_id': timesheet.id,
            'escalated_from': from_approver,
            'escalated_to': next_approver,
            'admin_notified': False,
        }

        context = {
            'timesheet_id': timesheet.id,
            'employee_name': timesheet.user.get_full_name(),
            'week_start': str(timesheet.week_start),
            'escalated_from': from_approver.get_full_name(),
        }

        if next_approver:
            send_notification.delay(
                next_approver.id,
                'escalation_alert',
                context,
            )
        else:
            cls._notify_admins(timesheet, context)
            result['admin_notified'] = True

        return result

    @classmethod
    def _notify_admins(cls, timesheet: Timesheet, context: dict) -> None:
        """
        Notify all admins in the company about an unresolved escalation.

        Args:
            timesheet: The timesheet that couldn't be escalated
            context: Notification context
        """
        admins = User.objects.filter(
            company=timesheet.user.company,
            role=User.Role.ADMIN,
            is_active=True,
        )

        for admin in admins:
            send_notification.delay(
                admin.id,
                'escalation_alert',
                {
                    **context,
                    'chain_exhausted': True,
                },
            )


class OOOService:
    """
    Service for managing Out-of-Office periods.

    Business Rules:
    - Max 1 active OOO period per user
    - Max 1 future OOO period per user
    - Active + Future = max 2 total
    """

    @classmethod
    def create_ooo_period(
        cls,
        user: User,
        start_date: date,
        end_date: date
    ) -> OOOPeriod:
        """
        Create an OOO period with constraint validation.

        Args:
            user: The user going OOO
            start_date: Start of OOO period
            end_date: End of OOO period

        Returns:
            Created OOOPeriod instance

        Raises:
            ValueError: If constraints are violated
        """
        today = date.today()

        is_active = start_date <= today <= end_date
        is_future = start_date > today

        active_count = OOOPeriod.objects.filter(
            user=user,
            start_date__lte=today,
            end_date__gte=today,
        ).count()

        future_count = OOOPeriod.objects.filter(
            user=user,
            start_date__gt=today,
        ).count()

        if is_active and active_count >= 1:
            raise ValueError(
                'User already has an active OOO period. '
                'Only one active period is allowed.'
            )

        if is_future and future_count >= 1:
            raise ValueError(
                'User already has a future OOO period scheduled. '
                'Only one future period is allowed.'
            )

        return OOOPeriod.objects.create(
            user=user,
            start_date=start_date,
            end_date=end_date,
        )

    @classmethod
    def get_user_ooo_periods(cls, user: User) -> dict:
        """
        Get a user's OOO periods categorized by status.

        Args:
            user: The user to check

        Returns:
            Dict with 'active', 'future', and 'past' period lists
        """
        today = date.today()
        periods = OOOPeriod.objects.filter(user=user)

        return {
            'active': periods.filter(
                start_date__lte=today,
                end_date__gte=today,
            ),
            'future': periods.filter(start_date__gt=today),
            'past': periods.filter(end_date__lt=today),
        }

    @classmethod
    def cancel_ooo_period(cls, ooo_period: OOOPeriod) -> bool:
        """
        Cancel an OOO period.

        Args:
            ooo_period: The period to cancel

        Returns:
            True if cancelled, False if already past
        """
        if ooo_period.end_date < date.today():
            return False

        ooo_period.delete()
        return True


class DelegationService:
    """
    Service for managing approval delegations.

    Business Rules:
    - Only managers can delegate
    - Can only delegate to other managers
    - Delegates can approve timesheets of the delegator's reports
    """

    @classmethod
    def has_active_delegation(
        cls,
        delegator: User,
        delegate: User,
        as_of_date: date = None
    ) -> bool:
        """
        Check if there's an active delegation between two users.

        Args:
            delegator: The manager who delegated authority
            delegate: The manager who received authority
            as_of_date: Date to check (defaults to today)

        Returns:
            True if active delegation exists, False otherwise
        """
        if as_of_date is None:
            as_of_date = date.today()

        return ApprovalDelegation.objects.filter(
            delegator=delegator,
            delegate=delegate,
            start_date__lte=as_of_date,
            end_date__gte=as_of_date,
        ).exists()

    @classmethod
    def can_approve_via_delegation(
        cls,
        approver: User,
        timesheet: Timesheet
    ) -> bool:
        """
        Check if a user can approve a timesheet via delegation.

        Args:
            approver: The user attempting to approve
            timesheet: The timesheet being approved

        Returns:
            True if user has delegation authority, False otherwise
        """
        employee_manager = timesheet.user.manager
        if not employee_manager:
            return False

        return cls.has_active_delegation(employee_manager, approver)

    @classmethod
    def get_delegators(cls, delegate: User, as_of_date: date = None) -> list[User]:
        """
        Get all users who have delegated to a given user.

        Args:
            delegate: The manager who received delegations
            as_of_date: Date to check (defaults to today)

        Returns:
            List of users who delegated to this user
        """
        if as_of_date is None:
            as_of_date = date.today()

        delegations = ApprovalDelegation.objects.filter(
            delegate=delegate,
            start_date__lte=as_of_date,
            end_date__gte=as_of_date,
        ).select_related('delegator')

        return [d.delegator for d in delegations]
