"""
URL configuration for TimeEntries app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.timeentries.views import (
    ActiveTimerView,
    TimeEntryViewSet,
    TimerStartView,
    TimerStopView,
)

router = DefaultRouter()
router.register(r'', TimeEntryViewSet, basename='time-entry')

urlpatterns = [
    path('timer/start/', TimerStartView.as_view(), name='timer_start'),
    path('timer/stop/', TimerStopView.as_view(), name='timer_stop'),
    path('timer/active/', ActiveTimerView.as_view(), name='timer_active'),
    path('', include(router.urls)),
]
