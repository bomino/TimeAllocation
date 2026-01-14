"""
Views for TimeEntry API.
"""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.timeentries.models import TimeEntry
from apps.timeentries.serializers import (
    TimeEntrySerializer,
    TimeEntryUpdateSerializer,
)
from core.pagination import StandardPagination


class TimeEntryViewSet(viewsets.ModelViewSet):
    """ViewSet for TimeEntry CRUD operations."""

    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return TimeEntryUpdateSerializer
        return TimeEntrySerializer

    def get_queryset(self):
        queryset = TimeEntry.objects.filter(user=self.request.user)

        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        project_id = self.request.query_params.get('project')

        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        if project_id:
            queryset = queryset.filter(project_id=project_id)

        return queryset
