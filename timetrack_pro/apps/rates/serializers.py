"""
Serializers for Rate API.
"""
from rest_framework import serializers

from apps.projects.models import Project
from apps.rates.models import Rate
from apps.users.models import User


class RateSerializer(serializers.ModelSerializer):
    """Serializer for Rate model."""

    employee_id = serializers.IntegerField(required=False, allow_null=True, write_only=True)
    project_id = serializers.IntegerField(required=False, allow_null=True, write_only=True)

    class Meta:
        model = Rate
        fields = [
            'id',
            'company',
            'employee',
            'employee_id',
            'project',
            'project_id',
            'rate_type',
            'hourly_rate',
            'effective_from',
            'effective_to',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'company', 'employee', 'project', 'created_at', 'updated_at']

    def validate(self, attrs):
        effective_from = attrs.get('effective_from')
        effective_to = attrs.get('effective_to')

        if effective_from and effective_to and effective_to < effective_from:
            raise serializers.ValidationError({
                'effective_to': 'End date must be on or after start date.'
            })

        rate_type = attrs.get('rate_type')
        employee_id = attrs.get('employee_id')
        project_id = attrs.get('project_id')

        if rate_type == Rate.RateType.EMPLOYEE and not employee_id:
            raise serializers.ValidationError({
                'employee_id': 'Employee is required for EMPLOYEE rate type.'
            })

        if rate_type == Rate.RateType.PROJECT and not project_id:
            raise serializers.ValidationError({
                'project_id': 'Project is required for PROJECT rate type.'
            })

        if rate_type == Rate.RateType.EMPLOYEE_PROJECT:
            if not employee_id:
                raise serializers.ValidationError({
                    'employee_id': 'Employee is required for EMPLOYEE_PROJECT rate type.'
                })
            if not project_id:
                raise serializers.ValidationError({
                    'project_id': 'Project is required for EMPLOYEE_PROJECT rate type.'
                })

        return attrs


class RateCreateSerializer(serializers.Serializer):
    """Serializer for creating a new rate."""

    employee_id = serializers.IntegerField(required=False, allow_null=True)
    project_id = serializers.IntegerField(required=False, allow_null=True)
    rate_type = serializers.ChoiceField(choices=Rate.RateType.choices)
    hourly_rate = serializers.DecimalField(max_digits=10, decimal_places=2)
    effective_from = serializers.DateField()
    effective_to = serializers.DateField(required=False, allow_null=True)

    def validate(self, attrs):
        effective_from = attrs.get('effective_from')
        effective_to = attrs.get('effective_to')

        if effective_from and effective_to and effective_to < effective_from:
            raise serializers.ValidationError({
                'effective_to': 'End date must be on or after start date.'
            })

        rate_type = attrs.get('rate_type')
        employee_id = attrs.get('employee_id')
        project_id = attrs.get('project_id')

        if rate_type == Rate.RateType.EMPLOYEE and not employee_id:
            raise serializers.ValidationError({
                'employee_id': 'Employee is required for EMPLOYEE rate type.'
            })

        if rate_type == Rate.RateType.PROJECT and not project_id:
            raise serializers.ValidationError({
                'project_id': 'Project is required for PROJECT rate type.'
            })

        if rate_type == Rate.RateType.EMPLOYEE_PROJECT:
            if not employee_id:
                raise serializers.ValidationError({
                    'employee_id': 'Employee is required for EMPLOYEE_PROJECT rate type.'
                })
            if not project_id:
                raise serializers.ValidationError({
                    'project_id': 'Project is required for EMPLOYEE_PROJECT rate type.'
                })

        return attrs

    def create(self, validated_data):
        company = self.context['company']
        employee_id = validated_data.pop('employee_id', None)
        project_id = validated_data.pop('project_id', None)

        employee = None
        project = None

        if employee_id:
            employee = User.objects.get(pk=employee_id)
        if project_id:
            project = Project.objects.get(pk=project_id)

        return Rate.objects.create(
            company=company,
            employee=employee,
            project=project,
            **validated_data
        )


class EffectiveRateSerializer(serializers.Serializer):
    """Serializer for effective rate response."""

    rate = serializers.DecimalField(max_digits=10, decimal_places=2)
    source = serializers.CharField()
    user_id = serializers.IntegerField()
    project_id = serializers.IntegerField()
    as_of_date = serializers.DateField()
