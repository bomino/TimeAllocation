"""
Views for Rate API.
"""
from datetime import date

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.projects.models import Project
from apps.rates.models import Rate
from apps.rates.serializers import (
    EffectiveRateSerializer,
    RateCreateSerializer,
    RateSerializer,
)
from apps.rates.services import RateResolutionService
from apps.users.models import User
from core.pagination import StandardPagination


class RateViewSet(viewsets.ModelViewSet):
    """ViewSet for Rate CRUD operations."""

    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination
    serializer_class = RateSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Rate.objects.filter(company=user.company)

        rate_type = self.request.query_params.get('rate_type')
        if rate_type:
            queryset = queryset.filter(rate_type=rate_type)

        employee_id = self.request.query_params.get('employee_id')
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)

        project_id = self.request.query_params.get('project_id')
        if project_id:
            queryset = queryset.filter(project_id=project_id)

        return queryset.select_related('employee', 'project')

    def list(self, request, *args, **kwargs):
        if not request.user.is_manager:
            return Response(
                {'detail': 'Only managers and admins can view rates.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        if not request.user.is_admin:
            return Response(
                {'detail': 'Only admins can create rates.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = RateCreateSerializer(
            data=request.data,
            context={'company': request.user.company}
        )

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        rate = serializer.save()
        return Response(RateSerializer(rate).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        if not request.user.is_admin:
            return Response(
                {'detail': 'Only admins can update rates.'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            rate = Rate.objects.get(pk=kwargs['pk'], company=request.user.company)
        except Rate.DoesNotExist:
            return Response(
                {'detail': 'Not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        hourly_rate = request.data.get('hourly_rate')
        effective_from = request.data.get('effective_from')
        effective_to = request.data.get('effective_to')

        if hourly_rate:
            rate.hourly_rate = hourly_rate
        if effective_from:
            rate.effective_from = effective_from
        if effective_to is not None:
            rate.effective_to = effective_to if effective_to else None

        rate.save()
        return Response(RateSerializer(rate).data)

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_admin:
            return Response(
                {'detail': 'Only admins can delete rates.'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            rate = Rate.objects.get(pk=kwargs['pk'], company=request.user.company)
        except Rate.DoesNotExist:
            return Response(
                {'detail': 'Not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        rate.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class EffectiveRateView(APIView):
    """
    GET /api/v1/rates/effective/

    Resolve effective rate for a user/project combination.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_manager:
            return Response(
                {'detail': 'Only managers and admins can view effective rates.'},
                status=status.HTTP_403_FORBIDDEN
            )

        user_id = request.query_params.get('user_id')
        project_id = request.query_params.get('project_id')
        as_of_date_str = request.query_params.get('date')

        if not user_id or not project_id:
            return Response(
                {'detail': 'user_id and project_id are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            target_user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response(
                {'detail': 'User not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            project = Project.objects.get(pk=project_id)
        except Project.DoesNotExist:
            return Response(
                {'detail': 'Project not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if as_of_date_str:
            try:
                as_of_date = date.fromisoformat(as_of_date_str)
            except ValueError:
                return Response(
                    {'detail': 'Invalid date format. Use YYYY-MM-DD.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            as_of_date = date.today()

        result = RateResolutionService.resolve(target_user, project, as_of_date)

        return Response({
            'rate': str(result.rate),
            'source': result.source,
            'user_id': target_user.id,
            'project_id': project.id,
            'as_of_date': str(as_of_date),
        })
