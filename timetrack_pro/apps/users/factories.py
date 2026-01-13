"""
Test factories for User model.
"""
import factory
from faker import Faker

from apps.users.models import User

fake = Faker()


class UserFactory(factory.django.DjangoModelFactory):
    """Factory for creating User instances in tests."""

    class Meta:
        model = User

    email = factory.LazyAttribute(lambda _: fake.unique.email())
    username = factory.LazyAttribute(lambda o: o.email)
    first_name = factory.LazyAttribute(lambda _: fake.first_name())
    last_name = factory.LazyAttribute(lambda _: fake.last_name())
    password = factory.PostGenerationMethodCall('set_password', 'ValidPass1!')
    role = User.Role.EMPLOYEE
    timezone = 'UTC'
    workflow_notifications_enabled = True
    security_notifications_enabled = True
    is_active = True

    @factory.lazy_attribute
    def company(self):
        from apps.companies.factories import CompanyFactory
        return CompanyFactory()
