"""Factory Boy factories for Projects app."""
import factory
from faker import Faker

from apps.companies.factories import CompanyFactory
from apps.projects.models import Project

fake = Faker()


class ProjectFactory(factory.django.DjangoModelFactory):
    """Factory for creating Project instances."""

    class Meta:
        model = Project

    name = factory.LazyAttribute(lambda _: fake.unique.bs())
    company = factory.SubFactory(CompanyFactory)
    status = Project.Status.ACTIVE
    description = factory.LazyAttribute(lambda _: fake.paragraph())
