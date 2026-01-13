"""
Tests for Timesheet models - TDD approach.
"""
from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.db import IntegrityError
from django.utils import timezone

from apps.timesheets.models import (
    AdminOverride,
    OOOPeriod,
    Timesheet,
    TimesheetComment,
)


@pytest.mark.django_db
class TestTimesheetModel:
    """Tests for Timesheet model."""

    def test_create_timesheet_with_required_fields(self, user):
        """
        Given: A user
        When: Creating a timesheet with user and week_start
        Then: Timesheet is created successfully
        """
        timesheet = Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
        )

        assert timesheet.pk is not None
        assert timesheet.user == user
        assert timesheet.week_start == date(2024, 6, 10)

    def test_timesheet_default_status_is_draft(self, user):
        """
        Given: Creating a new timesheet
        When: No status specified
        Then: Status defaults to DRAFT
        """
        timesheet = Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
        )

        assert timesheet.status == Timesheet.Status.DRAFT

    def test_timesheet_unique_per_user_and_week(self, user):
        """
        Given: A timesheet for user X week Y
        When: Creating another timesheet for same user and week
        Then: IntegrityError is raised
        """
        Timesheet.objects.create(user=user, week_start=date(2024, 6, 10))

        with pytest.raises(IntegrityError):
            Timesheet.objects.create(user=user, week_start=date(2024, 6, 10))

    def test_same_week_allowed_for_different_users(self, user, user_factory):
        """
        Given: A timesheet for user X week Y
        When: Creating timesheet for user Z same week
        Then: Both are created successfully
        """
        other_user = user_factory()

        ts1 = Timesheet.objects.create(user=user, week_start=date(2024, 6, 10))
        ts2 = Timesheet.objects.create(user=other_user, week_start=date(2024, 6, 10))

        assert ts1.pk != ts2.pk

    def test_timesheet_str_representation(self, user):
        """
        Given: A timesheet
        When: Converting to string
        Then: Shows user email and week start
        """
        timesheet = Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
        )

        assert user.email in str(timesheet)
        assert '2024-06-10' in str(timesheet)

    def test_timesheet_status_choices(self):
        """
        Given: Timesheet status choices
        When: Checking available options
        Then: DRAFT, SUBMITTED, APPROVED, REJECTED are available
        """
        assert Timesheet.Status.DRAFT == 'DRAFT'
        assert Timesheet.Status.SUBMITTED == 'SUBMITTED'
        assert Timesheet.Status.APPROVED == 'APPROVED'
        assert Timesheet.Status.REJECTED == 'REJECTED'

    def test_timesheet_submitted_at_is_optional(self, user):
        """
        Given: Creating a draft timesheet
        When: Not specifying submitted_at
        Then: submitted_at is null
        """
        timesheet = Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
        )

        assert timesheet.submitted_at is None

    def test_timesheet_approved_by_is_optional(self, user):
        """
        Given: Creating a timesheet
        When: Not approved yet
        Then: approved_by and approved_at are null
        """
        timesheet = Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
        )

        assert timesheet.approved_by is None
        assert timesheet.approved_at is None

    def test_timesheet_locked_at_is_optional(self, user):
        """
        Given: Creating a timesheet
        When: Not locked yet
        Then: locked_at is null
        """
        timesheet = Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
        )

        assert timesheet.locked_at is None

    def test_timesheet_ordering_by_week_start_descending(self, user):
        """
        Given: Multiple timesheets with different weeks
        When: Querying timesheets
        Then: Most recent week first
        """
        Timesheet.objects.create(user=user, week_start=date(2024, 6, 3))
        Timesheet.objects.create(user=user, week_start=date(2024, 6, 17))
        Timesheet.objects.create(user=user, week_start=date(2024, 6, 10))

        timesheets = list(Timesheet.objects.filter(user=user))
        assert timesheets[0].week_start == date(2024, 6, 17)
        assert timesheets[1].week_start == date(2024, 6, 10)
        assert timesheets[2].week_start == date(2024, 6, 3)

    def test_timesheet_has_timestamps(self, user):
        """
        Given: A newly created timesheet
        When: Checking timestamps
        Then: created_at and updated_at are set
        """
        timesheet = Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
        )

        assert timesheet.created_at is not None
        assert timesheet.updated_at is not None


@pytest.mark.django_db
class TestTimesheetCommentModel:
    """Tests for TimesheetComment model."""

    def test_create_comment_on_timesheet(self, user, manager):
        """
        Given: A timesheet
        When: Manager adds a comment
        Then: Comment is created successfully
        """
        timesheet = Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
        )

        comment = TimesheetComment.objects.create(
            timesheet=timesheet,
            author=manager,
            text='Please clarify hours on Monday.',
        )

        assert comment.pk is not None
        assert comment.timesheet == timesheet
        assert comment.author == manager

    def test_comment_can_be_on_specific_entry(self, user, manager, project):
        """
        Given: A timesheet with entries
        When: Adding comment on specific entry
        Then: Comment is linked to entry
        """
        from apps.timeentries.models import TimeEntry

        timesheet = Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
        )
        entry = TimeEntry.objects.create(
            user=user,
            project=project,
            timesheet=timesheet,
            date=date(2024, 6, 10),
            hours=Decimal('8.00'),
            billing_rate=Decimal('100.00'),
            rate_source=TimeEntry.RateSource.PROJECT,
        )

        comment = TimesheetComment.objects.create(
            timesheet=timesheet,
            entry=entry,
            author=manager,
            text='8 hours seems high for this task.',
        )

        assert comment.entry == entry

    def test_comment_entry_is_optional(self, user, manager):
        """
        Given: Creating a general timesheet comment
        When: Not specifying entry
        Then: Comment applies to overall timesheet
        """
        timesheet = Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
        )

        comment = TimesheetComment.objects.create(
            timesheet=timesheet,
            author=manager,
            text='General feedback on this week.',
        )

        assert comment.entry is None

    def test_comment_resolved_defaults_to_false(self, user, manager):
        """
        Given: Creating a new comment
        When: Not specifying resolved
        Then: Defaults to False
        """
        timesheet = Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
        )

        comment = TimesheetComment.objects.create(
            timesheet=timesheet,
            author=manager,
            text='Fix this.',
        )

        assert comment.resolved is False
        assert comment.resolved_at is None

    def test_comment_can_be_resolved(self, user, manager):
        """
        Given: An unresolved comment
        When: Marking as resolved
        Then: resolved and resolved_at are updated
        """
        timesheet = Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
        )

        comment = TimesheetComment.objects.create(
            timesheet=timesheet,
            author=manager,
            text='Fix this.',
        )

        comment.resolved = True
        comment.resolved_at = timezone.now()
        comment.save()

        comment.refresh_from_db()
        assert comment.resolved is True
        assert comment.resolved_at is not None

    def test_comment_ordering_by_created_at(self, user, manager):
        """
        Given: Multiple comments on a timesheet
        When: Querying comments
        Then: Oldest first (chronological)
        """
        timesheet = Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
        )

        c1 = TimesheetComment.objects.create(
            timesheet=timesheet,
            author=manager,
            text='First comment',
        )
        c2 = TimesheetComment.objects.create(
            timesheet=timesheet,
            author=manager,
            text='Second comment',
        )
        c3 = TimesheetComment.objects.create(
            timesheet=timesheet,
            author=manager,
            text='Third comment',
        )

        comments = list(timesheet.comments.all())
        assert comments[0] == c1
        assert comments[1] == c2
        assert comments[2] == c3

    def test_comment_str_representation(self, user, manager):
        """
        Given: A comment
        When: Converting to string
        Then: Shows author and timesheet info
        """
        timesheet = Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
        )

        comment = TimesheetComment.objects.create(
            timesheet=timesheet,
            author=manager,
            text='Test comment',
        )

        assert manager.email in str(comment)


@pytest.mark.django_db
class TestOOOPeriodModel:
    """Tests for OOOPeriod (Out-of-Office) model."""

    def test_create_ooo_period(self, user):
        """
        Given: A user
        When: Creating an OOO period
        Then: Period is created successfully
        """
        ooo = OOOPeriod.objects.create(
            user=user,
            start_date=date(2024, 7, 1),
            end_date=date(2024, 7, 14),
        )

        assert ooo.pk is not None
        assert ooo.user == user
        assert ooo.start_date == date(2024, 7, 1)
        assert ooo.end_date == date(2024, 7, 14)

    def test_ooo_ordering_by_start_date(self, user):
        """
        Given: Multiple OOO periods
        When: Querying periods
        Then: Earliest first
        """
        OOOPeriod.objects.create(
            user=user,
            start_date=date(2024, 9, 1),
            end_date=date(2024, 9, 7),
        )
        OOOPeriod.objects.create(
            user=user,
            start_date=date(2024, 7, 1),
            end_date=date(2024, 7, 14),
        )
        OOOPeriod.objects.create(
            user=user,
            start_date=date(2024, 8, 15),
            end_date=date(2024, 8, 20),
        )

        periods = list(user.ooo_periods.all())
        assert periods[0].start_date == date(2024, 7, 1)
        assert periods[1].start_date == date(2024, 8, 15)
        assert periods[2].start_date == date(2024, 9, 1)

    def test_ooo_str_representation(self, user):
        """
        Given: An OOO period
        When: Converting to string
        Then: Shows user and date range
        """
        ooo = OOOPeriod.objects.create(
            user=user,
            start_date=date(2024, 7, 1),
            end_date=date(2024, 7, 14),
        )

        assert user.email in str(ooo)
        assert '2024-07-01' in str(ooo)
        assert '2024-07-14' in str(ooo)

    def test_ooo_has_timestamps(self, user):
        """
        Given: A newly created OOO period
        When: Checking timestamps
        Then: created_at and updated_at are set
        """
        ooo = OOOPeriod.objects.create(
            user=user,
            start_date=date(2024, 7, 1),
            end_date=date(2024, 7, 14),
        )

        assert ooo.created_at is not None
        assert ooo.updated_at is not None


@pytest.mark.django_db
class TestAdminOverrideModel:
    """Tests for AdminOverride model."""

    def test_create_admin_override_unlock(self, user, admin):
        """
        Given: An approved timesheet
        When: Admin unlocks it
        Then: Override is recorded with audit trail
        """
        timesheet = Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
            status=Timesheet.Status.APPROVED,
        )

        override = AdminOverride.objects.create(
            timesheet=timesheet,
            admin=admin,
            action=AdminOverride.Action.UNLOCK,
            reason='Employee needs to correct an entry.',
            previous_status=Timesheet.Status.APPROVED,
        )

        assert override.pk is not None
        assert override.action == AdminOverride.Action.UNLOCK
        assert override.previous_status == Timesheet.Status.APPROVED

    def test_admin_override_action_choices(self):
        """
        Given: AdminOverride action choices
        When: Checking available options
        Then: UNLOCK, FORCE_APPROVE, FORCE_REJECT are available
        """
        assert AdminOverride.Action.UNLOCK == 'UNLOCK'
        assert AdminOverride.Action.FORCE_APPROVE == 'FORCE_APPROVE'
        assert AdminOverride.Action.FORCE_REJECT == 'FORCE_REJECT'

    def test_admin_override_ordering_by_created_at_descending(self, user, admin):
        """
        Given: Multiple overrides on a timesheet
        When: Querying overrides
        Then: Most recent first
        """
        timesheet = Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
        )

        o1 = AdminOverride.objects.create(
            timesheet=timesheet,
            admin=admin,
            action=AdminOverride.Action.UNLOCK,
            reason='First unlock',
            previous_status=Timesheet.Status.APPROVED,
        )
        o2 = AdminOverride.objects.create(
            timesheet=timesheet,
            admin=admin,
            action=AdminOverride.Action.FORCE_APPROVE,
            reason='Force approve after fix',
            previous_status=Timesheet.Status.DRAFT,
        )

        overrides = list(timesheet.admin_overrides.all())
        assert overrides[0] == o2
        assert overrides[1] == o1

    def test_admin_override_str_representation(self, user, admin):
        """
        Given: An admin override
        When: Converting to string
        Then: Shows action and admin
        """
        timesheet = Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
        )

        override = AdminOverride.objects.create(
            timesheet=timesheet,
            admin=admin,
            action=AdminOverride.Action.UNLOCK,
            reason='Test',
            previous_status=Timesheet.Status.APPROVED,
        )

        assert 'UNLOCK' in str(override)
        assert admin.email in str(override)

    def test_admin_override_has_timestamps(self, user, admin):
        """
        Given: A newly created override
        When: Checking timestamps
        Then: created_at and updated_at are set
        """
        timesheet = Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
        )

        override = AdminOverride.objects.create(
            timesheet=timesheet,
            admin=admin,
            action=AdminOverride.Action.UNLOCK,
            reason='Test',
            previous_status=Timesheet.Status.APPROVED,
        )

        assert override.created_at is not None
        assert override.updated_at is not None


@pytest.mark.django_db
class TestTimesheetRelationships:
    """Tests for Timesheet model relationships."""

    def test_user_can_have_multiple_timesheets(self, user):
        """
        Given: A user
        When: Creating timesheets for different weeks
        Then: All accessible via user.timesheets
        """
        Timesheet.objects.create(user=user, week_start=date(2024, 6, 3))
        Timesheet.objects.create(user=user, week_start=date(2024, 6, 10))
        Timesheet.objects.create(user=user, week_start=date(2024, 6, 17))

        assert user.timesheets.count() == 3

    def test_deleting_user_cascades_to_timesheets(self, user):
        """
        Given: A user with timesheets
        When: User is deleted
        Then: All timesheets are deleted
        """
        Timesheet.objects.create(user=user, week_start=date(2024, 6, 10))
        user_id = user.id

        user.delete()

        assert Timesheet.objects.filter(user_id=user_id).count() == 0

    def test_timesheet_entries_relationship(self, user, project):
        """
        Given: A timesheet with time entries
        When: Accessing entries
        Then: All entries are accessible via timesheet.entries
        """
        from apps.timeentries.models import TimeEntry

        timesheet = Timesheet.objects.create(
            user=user,
            week_start=date(2024, 6, 10),
        )

        TimeEntry.objects.create(
            user=user,
            project=project,
            timesheet=timesheet,
            date=date(2024, 6, 10),
            hours=Decimal('8.00'),
            billing_rate=Decimal('100.00'),
            rate_source=TimeEntry.RateSource.PROJECT,
        )
        TimeEntry.objects.create(
            user=user,
            project=project,
            timesheet=timesheet,
            date=date(2024, 6, 11),
            hours=Decimal('7.00'),
            billing_rate=Decimal('100.00'),
            rate_source=TimeEntry.RateSource.PROJECT,
        )

        assert timesheet.entries.count() == 2
