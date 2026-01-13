"""
Serializers for Timesheet API.
"""
from decimal import Decimal

from django.db.models import Sum
from django.utils import timezone
from rest_framework import serializers

from apps.timeentries.models import TimeEntry
from apps.timeentries.serializers import TimeEntrySerializer
from apps.timesheets.models import (
    AdminOverride,
    ApprovalDelegation,
    OOOPeriod,
    Timesheet,
    TimesheetComment,
)


class NestedUserSerializer(serializers.Serializer):
    """Minimal user info for nested serialization."""
    id = serializers.IntegerField()
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()


class TimesheetCommentSerializer(serializers.ModelSerializer):
    """Serializer for TimesheetComment model."""

    author = NestedUserSerializer(read_only=True)

    class Meta:
        model = TimesheetComment
        fields = [
            'id',
            'timesheet',
            'entry',
            'author',
            'text',
            'resolved',
            'resolved_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'author',
            'resolved_at',
            'created_at',
            'updated_at',
        ]


class TimesheetCommentCreateSerializer(serializers.Serializer):
    """Serializer for creating a comment on a timesheet."""

    text = serializers.CharField()
    entry_id = serializers.IntegerField(required=False, allow_null=True)

    def validate_text(self, value):
        if not value.strip():
            raise serializers.ValidationError('Comment text cannot be empty.')
        return value

    def validate_entry_id(self, value):
        if value is not None:
            timesheet = self.context.get('timesheet')
            if timesheet:
                try:
                    TimeEntry.objects.get(pk=value, timesheet=timesheet)
                except TimeEntry.DoesNotExist:
                    raise serializers.ValidationError(
                        'Entry not found in this timesheet.'
                    )
        return value

    def create(self, validated_data):
        timesheet = self.context['timesheet']
        author = self.context['request'].user
        entry_id = validated_data.get('entry_id')

        entry = None
        if entry_id:
            entry = TimeEntry.objects.get(pk=entry_id)

        return TimesheetComment.objects.create(
            timesheet=timesheet,
            entry=entry,
            author=author,
            text=validated_data['text'],
        )


class TimesheetListSerializer(serializers.ModelSerializer):
    """Serializer for listing timesheets."""

    user = NestedUserSerializer(read_only=True)
    approved_by = NestedUserSerializer(read_only=True)
    total_hours = serializers.SerializerMethodField()

    class Meta:
        model = Timesheet
        fields = [
            'id',
            'user',
            'week_start',
            'status',
            'submitted_at',
            'approved_at',
            'approved_by',
            'locked_at',
            'total_hours',
            'created_at',
            'updated_at',
        ]

    def get_total_hours(self, obj):
        total = obj.entries.aggregate(total=Sum('hours'))['total']
        return str(total) if total else '0.00'


class TimesheetDetailSerializer(serializers.ModelSerializer):
    """Serializer for timesheet detail with entries."""

    user = NestedUserSerializer(read_only=True)
    approved_by = NestedUserSerializer(read_only=True)
    entries = TimeEntrySerializer(many=True, read_only=True)
    total_hours = serializers.SerializerMethodField()
    comments = TimesheetCommentSerializer(many=True, read_only=True)

    class Meta:
        model = Timesheet
        fields = [
            'id',
            'user',
            'week_start',
            'status',
            'submitted_at',
            'approved_at',
            'approved_by',
            'locked_at',
            'entries',
            'total_hours',
            'comments',
            'created_at',
            'updated_at',
        ]

    def get_total_hours(self, obj):
        total = obj.entries.aggregate(total=Sum('hours'))['total']
        return str(total) if total else '0.00'


class TimesheetSubmitSerializer(serializers.Serializer):
    """Serializer for submitting a timesheet."""

    def validate(self, attrs):
        timesheet = self.context.get('timesheet')

        if timesheet.status != Timesheet.Status.DRAFT:
            raise serializers.ValidationError(
                'Only draft timesheets can be submitted.'
            )

        if not timesheet.entries.exists():
            raise serializers.ValidationError(
                'Cannot submit an empty timesheet. Add time entries first.'
            )

        return attrs

    def save(self):
        timesheet = self.context['timesheet']
        timesheet.status = Timesheet.Status.SUBMITTED
        timesheet.submitted_at = timezone.now()
        timesheet.save()
        return timesheet


class TimesheetApproveSerializer(serializers.Serializer):
    """Serializer for approving a timesheet."""

    def validate(self, attrs):
        timesheet = self.context.get('timesheet')

        if timesheet.status != Timesheet.Status.SUBMITTED:
            raise serializers.ValidationError(
                'Only submitted timesheets can be approved.'
            )

        return attrs

    def save(self):
        timesheet = self.context['timesheet']
        manager = self.context['request'].user

        timesheet.status = Timesheet.Status.APPROVED
        timesheet.approved_at = timezone.now()
        timesheet.approved_by = manager
        timesheet.locked_at = timezone.now()
        timesheet.save()
        return timesheet


class TimesheetRejectSerializer(serializers.Serializer):
    """Serializer for rejecting a timesheet."""

    comment = serializers.CharField()
    entry_id = serializers.IntegerField(required=False, allow_null=True)

    def validate_comment(self, value):
        if not value.strip():
            raise serializers.ValidationError('Rejection comment is required.')
        return value

    def validate_entry_id(self, value):
        if value is not None:
            timesheet = self.context.get('timesheet')
            if timesheet:
                try:
                    TimeEntry.objects.get(pk=value, timesheet=timesheet)
                except TimeEntry.DoesNotExist:
                    raise serializers.ValidationError(
                        'Entry not found in this timesheet.'
                    )
        return value

    def validate(self, attrs):
        timesheet = self.context.get('timesheet')

        if timesheet.status != Timesheet.Status.SUBMITTED:
            raise serializers.ValidationError(
                'Only submitted timesheets can be rejected.'
            )

        return attrs

    def save(self):
        timesheet = self.context['timesheet']
        manager = self.context['request'].user
        entry_id = self.validated_data.get('entry_id')

        entry = None
        if entry_id:
            entry = TimeEntry.objects.get(pk=entry_id)

        TimesheetComment.objects.create(
            timesheet=timesheet,
            entry=entry,
            author=manager,
            text=self.validated_data['comment'],
        )

        timesheet.status = Timesheet.Status.REJECTED
        timesheet.save()
        return timesheet


class TimesheetUnlockSerializer(serializers.Serializer):
    """Serializer for admin unlock of a timesheet."""

    reason = serializers.CharField()

    def validate_reason(self, value):
        if not value.strip():
            raise serializers.ValidationError('Unlock reason is required.')
        return value

    def validate(self, attrs):
        timesheet = self.context.get('timesheet')

        if timesheet.status not in [Timesheet.Status.APPROVED, Timesheet.Status.REJECTED]:
            raise serializers.ValidationError(
                'Only approved or rejected timesheets can be unlocked.'
            )

        if timesheet.approved_at:
            user = timesheet.user
            unlock_window_days = user.company.settings.unlock_window_days
            days_since_approval = (timezone.now() - timesheet.approved_at).days

            if days_since_approval > unlock_window_days:
                raise serializers.ValidationError(
                    f'Timesheet is outside the {unlock_window_days}-day unlock window. '
                    f'Approved {days_since_approval} days ago.'
                )

        return attrs

    def save(self):
        timesheet = self.context['timesheet']
        admin = self.context['request'].user
        previous_status = timesheet.status

        AdminOverride.objects.create(
            timesheet=timesheet,
            admin=admin,
            action=AdminOverride.Action.UNLOCK,
            reason=self.validated_data['reason'],
            previous_status=previous_status,
        )

        timesheet.status = Timesheet.Status.DRAFT
        timesheet.locked_at = None
        timesheet.save()
        return timesheet


class OOOPeriodSerializer(serializers.ModelSerializer):
    """Serializer for OOOPeriod model."""

    class Meta:
        model = OOOPeriod
        fields = [
            'id',
            'user',
            'start_date',
            'end_date',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def validate(self, attrs):
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')

        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError({
                'end_date': 'End date must be on or after start date.'
            })

        return attrs


class AdminOverrideSerializer(serializers.ModelSerializer):
    """Serializer for AdminOverride model."""

    admin_id = serializers.IntegerField(source='admin.id', read_only=True)
    admin_email = serializers.EmailField(source='admin.email', read_only=True)
    timesheet_id = serializers.IntegerField(source='timesheet.id', read_only=True)
    timesheet_user_id = serializers.IntegerField(source='timesheet.user.id', read_only=True)
    timesheet_week_start = serializers.DateField(source='timesheet.week_start', read_only=True)

    class Meta:
        model = AdminOverride
        fields = [
            'id',
            'timesheet',
            'timesheet_id',
            'timesheet_user_id',
            'timesheet_week_start',
            'admin',
            'admin_id',
            'admin_email',
            'action',
            'reason',
            'previous_status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ApprovalDelegationSerializer(serializers.ModelSerializer):
    """Serializer for ApprovalDelegation model."""

    class Meta:
        model = ApprovalDelegation
        fields = [
            'id',
            'delegator',
            'delegate',
            'start_date',
            'end_date',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'delegator', 'created_at', 'updated_at']


class ApprovalDelegationCreateSerializer(serializers.Serializer):
    """Serializer for creating a delegation."""

    delegate_id = serializers.IntegerField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()

    def validate_delegate_id(self, value):
        from apps.users.models import User

        try:
            delegate = User.objects.get(pk=value)
        except User.DoesNotExist:
            raise serializers.ValidationError('User not found.')

        if not delegate.is_manager:
            raise serializers.ValidationError('Delegate must be a manager or admin.')

        return value

    def validate(self, attrs):
        delegator = self.context['request'].user

        if attrs['delegate_id'] == delegator.id:
            raise serializers.ValidationError('Cannot delegate to yourself.')

        if attrs['end_date'] < attrs['start_date']:
            raise serializers.ValidationError({
                'end_date': 'End date must be on or after start date.'
            })

        return attrs

    def create(self, validated_data):
        from apps.users.models import User

        delegator = self.context['request'].user
        delegate = User.objects.get(pk=validated_data['delegate_id'])

        return ApprovalDelegation.objects.create(
            delegator=delegator,
            delegate=delegate,
            start_date=validated_data['start_date'],
            end_date=validated_data['end_date'],
        )
