"""
Tests for TimeEntry models - TDD approach.
"""
from datetime import date
from decimal import Decimal

import pytest

from apps.timeentries.models import TimeEntry


@pytest.mark.django_db
class TestTimeEntryModel:
    """Tests for TimeEntry model."""

    def test_create_time_entry_with_required_fields(self, user, project):
        """
        Given: A user and project
        When: Creating a time entry with all required fields
        Then: Entry is created successfully
        """
        entry = TimeEntry.objects.create(
            user=user,
            project=project,
            date=date(2024, 6, 15),
            hours=Decimal('8.00'),
            billing_rate=Decimal('100.00'),
            rate_source=TimeEntry.RateSource.PROJECT,
        )

        assert entry.pk is not None
        assert entry.user == user
        assert entry.project == project
        assert entry.hours == Decimal('8.00')

    def test_time_entry_billing_rate_is_snapshotted(self, user, project):
        """
        Given: Creating a time entry with specific billing rate
        When: Entry is saved
        Then: Billing rate is stored immutably
        """
        entry = TimeEntry.objects.create(
            user=user,
            project=project,
            date=date(2024, 6, 15),
            hours=Decimal('4.00'),
            billing_rate=Decimal('150.00'),
            rate_source=TimeEntry.RateSource.EMPLOYEE_PROJECT,
        )

        assert entry.billing_rate == Decimal('150.00')

    def test_time_entry_rate_source_tracks_origin(self, user, project):
        """
        Given: Creating a time entry
        When: Specifying rate source
        Then: Source is recorded for audit trail
        """
        entry = TimeEntry.objects.create(
            user=user,
            project=project,
            date=date(2024, 6, 15),
            hours=Decimal('2.00'),
            billing_rate=Decimal('75.00'),
            rate_source=TimeEntry.RateSource.COMPANY,
        )

        assert entry.rate_source == TimeEntry.RateSource.COMPANY

    def test_time_entry_billable_amount_calculation(self, user, project):
        """
        Given: A time entry with hours and rate
        When: Accessing billable_amount
        Then: Returns hours * billing_rate
        """
        entry = TimeEntry.objects.create(
            user=user,
            project=project,
            date=date(2024, 6, 15),
            hours=Decimal('8.00'),
            billing_rate=Decimal('100.00'),
            rate_source=TimeEntry.RateSource.PROJECT,
        )

        assert entry.billable_amount == Decimal('800.00')

    def test_time_entry_description_optional(self, user, project):
        """
        Given: Creating a time entry
        When: No description provided
        Then: Description defaults to empty string
        """
        entry = TimeEntry.objects.create(
            user=user,
            project=project,
            date=date(2024, 6, 15),
            hours=Decimal('1.00'),
            billing_rate=Decimal('50.00'),
            rate_source=TimeEntry.RateSource.COMPANY,
        )

        assert entry.description == ''

    def test_time_entry_with_description(self, user, project):
        """
        Given: Creating a time entry
        When: Providing a description
        Then: Description is saved
        """
        entry = TimeEntry.objects.create(
            user=user,
            project=project,
            date=date(2024, 6, 15),
            hours=Decimal('4.00'),
            billing_rate=Decimal('100.00'),
            rate_source=TimeEntry.RateSource.PROJECT,
            description='Implemented user authentication feature',
        )

        assert entry.description == 'Implemented user authentication feature'

    def test_time_entry_str_representation(self, user, project):
        """
        Given: A time entry
        When: Converting to string
        Then: Shows user, project, and date
        """
        entry = TimeEntry.objects.create(
            user=user,
            project=project,
            date=date(2024, 6, 15),
            hours=Decimal('8.00'),
            billing_rate=Decimal('100.00'),
            rate_source=TimeEntry.RateSource.PROJECT,
        )

        expected = f'{user.email} - {project.name} - 2024-06-15'
        assert str(entry) == expected

    def test_time_entry_has_timestamps(self, user, project):
        """
        Given: A newly created time entry
        When: Checking timestamps
        Then: created_at and updated_at are set
        """
        entry = TimeEntry.objects.create(
            user=user,
            project=project,
            date=date(2024, 6, 15),
            hours=Decimal('8.00'),
            billing_rate=Decimal('100.00'),
            rate_source=TimeEntry.RateSource.PROJECT,
        )

        assert entry.created_at is not None
        assert entry.updated_at is not None

    def test_time_entry_ordering_by_date_descending(self, user, project):
        """
        Given: Multiple time entries with different dates
        When: Querying entries
        Then: Most recent date first
        """
        TimeEntry.objects.create(
            user=user,
            project=project,
            date=date(2024, 6, 15),
            hours=Decimal('8.00'),
            billing_rate=Decimal('100.00'),
            rate_source=TimeEntry.RateSource.PROJECT,
        )
        TimeEntry.objects.create(
            user=user,
            project=project,
            date=date(2024, 6, 17),
            hours=Decimal('6.00'),
            billing_rate=Decimal('100.00'),
            rate_source=TimeEntry.RateSource.PROJECT,
        )
        TimeEntry.objects.create(
            user=user,
            project=project,
            date=date(2024, 6, 16),
            hours=Decimal('7.00'),
            billing_rate=Decimal('100.00'),
            rate_source=TimeEntry.RateSource.PROJECT,
        )

        entries = list(TimeEntry.objects.filter(user=user))
        assert entries[0].date == date(2024, 6, 17)
        assert entries[1].date == date(2024, 6, 16)
        assert entries[2].date == date(2024, 6, 15)


@pytest.mark.django_db
class TestTimeEntryTimer:
    """Tests for timer-related functionality."""

    def test_time_entry_is_timer_entry_default_false(self, user, project):
        """
        Given: Creating a manual time entry
        When: Not specifying is_timer_entry
        Then: Defaults to False
        """
        entry = TimeEntry.objects.create(
            user=user,
            project=project,
            date=date(2024, 6, 15),
            hours=Decimal('8.00'),
            billing_rate=Decimal('100.00'),
            rate_source=TimeEntry.RateSource.PROJECT,
        )

        assert entry.is_timer_entry is False

    def test_time_entry_timer_fields_optional(self, user, project):
        """
        Given: Creating a manual time entry
        When: Not specifying timer fields
        Then: Timer fields are null
        """
        entry = TimeEntry.objects.create(
            user=user,
            project=project,
            date=date(2024, 6, 15),
            hours=Decimal('8.00'),
            billing_rate=Decimal('100.00'),
            rate_source=TimeEntry.RateSource.PROJECT,
        )

        assert entry.timer_started_at is None
        assert entry.timer_stopped_at is None

    def test_time_entry_timesheet_optional(self, user, project):
        """
        Given: Creating a time entry
        When: Not associated with a timesheet
        Then: Timesheet is null
        """
        entry = TimeEntry.objects.create(
            user=user,
            project=project,
            date=date(2024, 6, 15),
            hours=Decimal('8.00'),
            billing_rate=Decimal('100.00'),
            rate_source=TimeEntry.RateSource.PROJECT,
        )

        assert entry.timesheet is None


@pytest.mark.django_db
class TestTimeEntryRateSourceChoices:
    """Tests for RateSource choices."""

    def test_rate_source_employee_project(self):
        assert TimeEntry.RateSource.EMPLOYEE_PROJECT == 'EMPLOYEE_PROJECT'

    def test_rate_source_project(self):
        assert TimeEntry.RateSource.PROJECT == 'PROJECT'

    def test_rate_source_employee(self):
        assert TimeEntry.RateSource.EMPLOYEE == 'EMPLOYEE'

    def test_rate_source_company(self):
        assert TimeEntry.RateSource.COMPANY == 'COMPANY'


@pytest.mark.django_db
class TestTimeEntryRelationships:
    """Tests for TimeEntry model relationships."""

    def test_user_can_have_multiple_entries(self, user, project):
        """
        Given: A user
        When: Creating multiple time entries
        Then: All accessible via user.time_entries
        """
        TimeEntry.objects.create(
            user=user, project=project, date=date(2024, 6, 15),
            hours=Decimal('8.00'), billing_rate=Decimal('100.00'),
            rate_source=TimeEntry.RateSource.PROJECT,
        )
        TimeEntry.objects.create(
            user=user, project=project, date=date(2024, 6, 16),
            hours=Decimal('8.00'), billing_rate=Decimal('100.00'),
            rate_source=TimeEntry.RateSource.PROJECT,
        )

        assert user.time_entries.count() == 2

    def test_project_can_have_multiple_entries(self, user, project, user_factory):
        """
        Given: A project
        When: Multiple users log time
        Then: All accessible via project.time_entries
        """
        other_user = user_factory(company=project.company)

        TimeEntry.objects.create(
            user=user, project=project, date=date(2024, 6, 15),
            hours=Decimal('8.00'), billing_rate=Decimal('100.00'),
            rate_source=TimeEntry.RateSource.PROJECT,
        )
        TimeEntry.objects.create(
            user=other_user, project=project, date=date(2024, 6, 15),
            hours=Decimal('6.00'), billing_rate=Decimal('100.00'),
            rate_source=TimeEntry.RateSource.PROJECT,
        )

        assert project.time_entries.count() == 2

    def test_deleting_user_cascades_to_entries(self, user, project):
        """
        Given: A user with time entries
        When: User is deleted
        Then: All entries are deleted
        """
        TimeEntry.objects.create(
            user=user, project=project, date=date(2024, 6, 15),
            hours=Decimal('8.00'), billing_rate=Decimal('100.00'),
            rate_source=TimeEntry.RateSource.PROJECT,
        )
        user_id = user.id

        user.delete()

        assert TimeEntry.objects.filter(user_id=user_id).count() == 0

    def test_deleting_project_cascades_to_entries(self, user, project):
        """
        Given: A project with time entries
        When: Project is deleted
        Then: All entries are deleted
        """
        TimeEntry.objects.create(
            user=user, project=project, date=date(2024, 6, 15),
            hours=Decimal('8.00'), billing_rate=Decimal('100.00'),
            rate_source=TimeEntry.RateSource.PROJECT,
        )
        project_id = project.id

        project.delete()

        assert TimeEntry.objects.filter(project_id=project_id).count() == 0
