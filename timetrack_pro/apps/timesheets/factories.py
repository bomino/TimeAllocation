"""Factory Boy factories for Timesheets app."""
import factory
from datetime import date, timedelta
from faker import Faker

from apps.timesheets.models import Timesheet, TimesheetComment, OOOPeriod, AdminOverride
from apps.users.factories import UserFactory

fake = Faker()


def get_week_start(d: date = None) -> date:
    """Get the Monday of the week containing the given date."""
    if d is None:
        d = date.today()
    return d - timedelta(days=d.weekday())


class TimesheetFactory(factory.django.DjangoModelFactory):
    """Factory for creating Timesheet instances."""

    class Meta:
        model = Timesheet

    user = factory.SubFactory(UserFactory)
    week_start = factory.LazyAttribute(lambda _: get_week_start())
    status = Timesheet.Status.DRAFT


class TimesheetCommentFactory(factory.django.DjangoModelFactory):
    """Factory for creating TimesheetComment instances."""

    class Meta:
        model = TimesheetComment

    timesheet = factory.SubFactory(TimesheetFactory)
    entry = None
    author = factory.SubFactory(UserFactory)
    text = factory.LazyAttribute(lambda _: fake.paragraph())
    resolved = False


class OOOPeriodFactory(factory.django.DjangoModelFactory):
    """Factory for creating OOOPeriod instances."""

    class Meta:
        model = OOOPeriod

    user = factory.SubFactory(UserFactory)
    start_date = factory.LazyAttribute(lambda _: date.today())
    end_date = factory.LazyAttribute(lambda _: date.today() + timedelta(days=7))


class AdminOverrideFactory(factory.django.DjangoModelFactory):
    """Factory for creating AdminOverride instances."""

    class Meta:
        model = AdminOverride

    timesheet = factory.SubFactory(TimesheetFactory)
    admin = factory.SubFactory(UserFactory)
    action = AdminOverride.Action.UNLOCK
    reason = factory.LazyAttribute(lambda _: fake.sentence())
    previous_status = Timesheet.Status.SUBMITTED
