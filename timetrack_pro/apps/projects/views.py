"""
Views for Project API.
"""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.projects.models import Project
from apps.projects.serializers import ProjectSerializer
from core.pagination import StandardPagination


class ProjectViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for listing projects (read-only for now)."""

    permission_classes = [IsAuthenticated]
    serializer_class = ProjectSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        return Project.objects.filter(
            company=self.request.user.company,
            status=Project.Status.ACTIVE,
        ).order_by('name')
