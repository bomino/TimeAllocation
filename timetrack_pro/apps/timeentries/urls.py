"""
URL configuration for TimeEntries app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.timeentries.views import TimeEntryViewSet

router = DefaultRouter()
router.register(r'', TimeEntryViewSet, basename='time-entry')

urlpatterns = [
    path('', include(router.urls)),
]
