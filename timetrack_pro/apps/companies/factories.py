"""
Factory Boy factories for Companies app.

Used in tests to create realistic test data with Faker.
"""
import factory
from faker import Faker

from apps.companies.models import Company, CompanySettings, CompanySettingsAudit

fake = Faker()


class CompanyFactory(factory.django.DjangoModelFactory):
    """Factory for creating Company instances."""

    class Meta:
        model = Company

    name = factory.LazyAttribute(lambda _: fake.unique.company())
    week_start_day = Company.WeekDay.MONDAY
    timezone = 'UTC'

    @factory.post_generation
    def settings(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            return
        if not hasattr(self, '_settings_created'):
            CompanySettings.objects.get_or_create(
                company=self,
                defaults={
                    'unlock_window_days': 7,
                    'daily_warning_threshold': 8,
                    'escalation_days': 3,
                    'escalation_logic': CompanySettings.EscalationLogic.OR,
                    'default_hourly_rate': fake.pydecimal(left_digits=3, right_digits=2, positive=True),
                }
            )
            self._settings_created = True


class CompanySettingsFactory(factory.django.DjangoModelFactory):
    """Factory for creating CompanySettings instances."""

    class Meta:
        model = CompanySettings

    company = factory.SubFactory(CompanyFactory)
    unlock_window_days = 7
    daily_warning_threshold = 8
    escalation_days = 3
    escalation_logic = CompanySettings.EscalationLogic.OR
    default_hourly_rate = factory.LazyAttribute(
        lambda _: fake.pydecimal(left_digits=3, right_digits=2, positive=True)
    )


class CompanySettingsAuditFactory(factory.django.DjangoModelFactory):
    """Factory for creating CompanySettingsAudit instances."""

    class Meta:
        model = CompanySettingsAudit

    company_settings = factory.SubFactory(CompanySettingsFactory)
    changed_by = None
    field_name = factory.LazyAttribute(
        lambda _: fake.random_element([
            'unlock_window_days',
            'daily_warning_threshold',
            'escalation_days',
            'escalation_logic',
            'default_hourly_rate',
        ])
    )
    old_value = factory.LazyAttribute(lambda _: str(fake.random_int(min=1, max=10)))
    new_value = factory.LazyAttribute(lambda _: str(fake.random_int(min=1, max=10)))
