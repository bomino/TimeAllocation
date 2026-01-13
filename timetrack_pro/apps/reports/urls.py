"""
URL configuration for Reports app.
"""
from django.urls import path

from apps.reports.views import (
    ApprovalMetricsView,
    HoursSummaryView,
    UtilizationReportView,
)

urlpatterns = [
    path('hours/summary/', HoursSummaryView.as_view(), name='hours_summary'),
    path('approval/metrics/', ApprovalMetricsView.as_view(), name='approval_metrics'),
    path('utilization/', UtilizationReportView.as_view(), name='utilization'),
]
