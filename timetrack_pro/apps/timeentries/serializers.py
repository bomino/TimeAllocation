"""
Serializers for TimeEntry API.
"""
from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Sum
from rest_framework import serializers

from apps.projects.models import Project
from apps.rates.services import RateResolutionService
from apps.timeentries.models import TimeEntry


def get_week_start(target_date: date, week_start_day: int = 0) -> date:
    """Calculate the start of the week containing target_date."""
    days_since_week_start = (target_date.weekday() - week_start_day) % 7
    return target_date - timedelta(days=days_since_week_start)


def get_or_create_timesheet(user, entry_date: date):
    """Get or create a timesheet for the given user and date."""
    from apps.timesheets.models import Timesheet

    week_start_day = user.company.week_start_day if hasattr(user, 'company') and user.company else 0
    week_start = get_week_start(entry_date, week_start_day)

    timesheet, _ = Timesheet.objects.get_or_create(
        user=user,
        week_start=week_start,
        defaults={'status': Timesheet.Status.DRAFT},
    )
    return timesheet


class NestedUserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    email = serializers.EmailField()


class NestedProjectSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class TimeEntrySerializer(serializers.ModelSerializer):
    """Serializer for TimeEntry model."""

    user = NestedUserSerializer(read_only=True)
    project = NestedProjectSerializer(read_only=True)
    project_id = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(),
        source='project',
        write_only=True,
    )

    class Meta:
        model = TimeEntry
        fields = [
            'id',
            'user',
            'project',
            'project_id',
            'timesheet',
            'date',
            'hours',
            'description',
            'billing_rate',
            'rate_source',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'user',
            'project',
            'billing_rate',
            'rate_source',
            'created_at',
            'updated_at',
        ]

    def validate_hours(self, value):
        if value <= Decimal('0'):
            raise serializers.ValidationError('Hours must be greater than zero.')
        return value

    def validate(self, attrs):
        user = self.context['request'].user
        entry_date = attrs.get('date')
        hours = attrs.get('hours')

        if entry_date and hours:
            existing_hours = TimeEntry.objects.filter(
                user=user,
                date=entry_date,
            ).exclude(
                pk=self.instance.pk if self.instance else None
            ).aggregate(
                total=Sum('hours')
            )['total'] or Decimal('0')

            if existing_hours + hours > Decimal('24'):
                raise serializers.ValidationError({
                    'hours': f'Daily limit exceeded. You have {existing_hours} hours logged. '
                             f'Maximum additional hours: {Decimal("24") - existing_hours}.'
                })

        return attrs

    def create(self, validated_data):
        user = self.context['request'].user
        project = validated_data['project']
        entry_date = validated_data.get('date', date.today())

        rate_result = RateResolutionService.resolve(
            user=user,
            project=project,
            as_of_date=entry_date,
        )

        timesheet = get_or_create_timesheet(user, entry_date)

        validated_data['user'] = user
        validated_data['billing_rate'] = rate_result.rate
        validated_data['rate_source'] = rate_result.source
        validated_data['timesheet'] = timesheet

        return super().create(validated_data)


class TimeEntryUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating TimeEntry (doesn't recalculate rate)."""

    class Meta:
        model = TimeEntry
        fields = [
            'id',
            'user',
            'project',
            'timesheet',
            'date',
            'hours',
            'description',
            'billing_rate',
            'rate_source',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'user',
            'billing_rate',
            'rate_source',
            'created_at',
            'updated_at',
        ]

    def validate_hours(self, value):
        if value <= Decimal('0'):
            raise serializers.ValidationError('Hours must be greater than zero.')
        return value

    def validate(self, attrs):
        user = self.context['request'].user
        entry_date = attrs.get('date', self.instance.date if self.instance else None)
        hours = attrs.get('hours', self.instance.hours if self.instance else Decimal('0'))

        if entry_date and hours:
            existing_hours = TimeEntry.objects.filter(
                user=user,
                date=entry_date,
            ).exclude(
                pk=self.instance.pk if self.instance else None
            ).aggregate(
                total=Sum('hours')
            )['total'] or Decimal('0')

            if existing_hours + hours > Decimal('24'):
                raise serializers.ValidationError({
                    'hours': f'Daily limit exceeded. You have {existing_hours} hours logged. '
                             f'Maximum additional hours: {Decimal("24") - existing_hours}.'
                })

        return attrs
