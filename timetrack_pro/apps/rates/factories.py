"""Factory Boy factories for Rates app."""
import factory
from datetime import date
from faker import Faker

from apps.companies.factories import CompanyFactory
from apps.rates.models import Rate

fake = Faker()


class RateFactory(factory.django.DjangoModelFactory):
    """Factory for creating Rate instances."""

    class Meta:
        model = Rate

    company = factory.SubFactory(CompanyFactory)
    employee = None
    project = None
    rate_type = Rate.RateType.PROJECT
    hourly_rate = factory.LazyAttribute(
        lambda _: fake.pydecimal(left_digits=3, right_digits=2, positive=True)
    )
    effective_from = factory.LazyAttribute(lambda _: date.today())
    effective_to = None
