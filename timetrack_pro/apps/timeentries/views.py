"""
Views for TimeEntry API.
"""
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.timeentries.models import TimeEntry
from apps.timeentries.serializers import (
    ActiveTimerSerializer,
    TimeEntrySerializer,
    TimeEntryUpdateSerializer,
    TimerStartSerializer,
    TimerStopSerializer,
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


class TimerStartView(APIView):
    """Start a new timer."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = TimerStartSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        entry = serializer.save()
        return Response(
            TimeEntrySerializer(entry).data,
            status=status.HTTP_201_CREATED,
        )


class TimerStopView(APIView):
    """Stop the active timer."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = TimerStopSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        entry = serializer.save()
        return Response(TimeEntrySerializer(entry).data)


class ActiveTimerView(APIView):
    """Get the currently active timer."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        active_timer = TimeEntry.objects.filter(
            user=request.user,
            is_timer_entry=True,
            timer_stopped_at__isnull=True,
        ).first()

        if not active_timer:
            return Response(
                {'detail': 'No active timer.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(ActiveTimerSerializer(active_timer).data)
