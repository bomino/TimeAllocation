"""Factory Boy factories for TimeEntries app."""
import factory
from datetime import date
from decimal import Decimal
from faker import Faker

from apps.projects.factories import ProjectFactory
from apps.timeentries.models import TimeEntry
from apps.users.factories import UserFactory

fake = Faker()


class TimeEntryFactory(factory.django.DjangoModelFactory):
    """Factory for creating TimeEntry instances."""

    class Meta:
        model = TimeEntry

    user = factory.SubFactory(UserFactory)
    project = factory.SubFactory(ProjectFactory)
    timesheet = None
    date = factory.LazyAttribute(lambda _: date.today())
    hours = factory.LazyAttribute(
        lambda _: Decimal(str(fake.pydecimal(left_digits=1, right_digits=2, positive=True, min_value=0.25, max_value=8)))
    )
    description = factory.LazyAttribute(lambda _: fake.sentence())
    billing_rate = factory.LazyAttribute(
        lambda _: fake.pydecimal(left_digits=3, right_digits=2, positive=True)
    )
    rate_source = TimeEntry.RateSource.COMPANY
    is_timer_entry = False
