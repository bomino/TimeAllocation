"""
Serializers for TimeEntry API.
"""
from datetime import date, datetime
from decimal import Decimal

from django.db.models import Sum
from django.utils import timezone
from rest_framework import serializers

from apps.projects.models import Project
from apps.rates.services import RateResolutionService
from apps.timeentries.models import TimeEntry


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
            'is_timer_entry',
            'timer_started_at',
            'timer_stopped_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'user',
            'project',
            'billing_rate',
            'rate_source',
            'is_timer_entry',
            'timer_started_at',
            'timer_stopped_at',
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

        validated_data['user'] = user
        validated_data['billing_rate'] = rate_result.rate
        validated_data['rate_source'] = rate_result.source

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
            'is_timer_entry',
            'timer_started_at',
            'timer_stopped_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'user',
            'billing_rate',
            'rate_source',
            'is_timer_entry',
            'timer_started_at',
            'timer_stopped_at',
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


class TimerStartSerializer(serializers.Serializer):
    """Serializer for starting a timer."""

    project = serializers.IntegerField()
    description = serializers.CharField(required=False, allow_blank=True, default='')

    def validate_project(self, value):
        from apps.projects.models import Project
        try:
            project = Project.objects.get(pk=value)
            return project
        except Project.DoesNotExist:
            raise serializers.ValidationError('Project not found.')

    def validate(self, attrs):
        user = self.context['request'].user

        active_timer = TimeEntry.objects.filter(
            user=user,
            is_timer_entry=True,
            timer_stopped_at__isnull=True,
        ).first()

        if active_timer:
            raise serializers.ValidationError(
                'You already have an active timer. Stop it before starting a new one.'
            )

        return attrs

    def create(self, validated_data):
        user = self.context['request'].user
        project = validated_data['project']
        now = timezone.now()

        rate_result = RateResolutionService.resolve(
            user=user,
            project=project,
            as_of_date=now.date(),
        )

        entry = TimeEntry.objects.create(
            user=user,
            project=project,
            date=now.date(),
            hours=Decimal('0.00'),
            description=validated_data.get('description', ''),
            billing_rate=rate_result.rate,
            rate_source=rate_result.source,
            is_timer_entry=True,
            timer_started_at=now,
        )

        return entry


class TimerStopSerializer(serializers.Serializer):
    """Serializer for stopping a timer."""

    description = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        user = self.context['request'].user

        active_timer = TimeEntry.objects.filter(
            user=user,
            is_timer_entry=True,
            timer_stopped_at__isnull=True,
        ).first()

        if not active_timer:
            raise serializers.ValidationError('No active timer to stop.')

        attrs['active_timer'] = active_timer
        return attrs

    def save(self):
        active_timer = self.validated_data['active_timer']
        user = self.context['request'].user
        now = timezone.now()

        elapsed = now - active_timer.timer_started_at
        elapsed_hours = Decimal(str(elapsed.total_seconds() / 3600)).quantize(Decimal('0.01'))

        existing_hours = TimeEntry.objects.filter(
            user=user,
            date=active_timer.date,
        ).exclude(
            pk=active_timer.pk
        ).aggregate(
            total=Sum('hours')
        )['total'] or Decimal('0')

        max_allowed = Decimal('24') - existing_hours
        final_hours = min(elapsed_hours, max_allowed)

        active_timer.timer_stopped_at = now
        active_timer.hours = final_hours

        if 'description' in self.validated_data and self.validated_data['description']:
            active_timer.description = self.validated_data['description']

        active_timer.save()
        return active_timer


class ActiveTimerSerializer(serializers.ModelSerializer):
    """Serializer for active timer with elapsed time."""

    user = NestedUserSerializer(read_only=True)
    project = NestedProjectSerializer(read_only=True)
    elapsed_hours = serializers.SerializerMethodField()

    class Meta:
        model = TimeEntry
        fields = [
            'id',
            'user',
            'project',
            'date',
            'hours',
            'description',
            'billing_rate',
            'rate_source',
            'is_timer_entry',
            'timer_started_at',
            'timer_stopped_at',
            'elapsed_hours',
            'created_at',
            'updated_at',
        ]

    def get_elapsed_hours(self, obj):
        if obj.timer_started_at and not obj.timer_stopped_at:
            now = timezone.now()
            elapsed = now - obj.timer_started_at
            return str(Decimal(str(elapsed.total_seconds() / 3600)).quantize(Decimal('0.01')))
        return '0.00'
