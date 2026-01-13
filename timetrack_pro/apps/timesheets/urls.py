"""
URL configuration for Timesheets app.
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.timesheets.views import (
    AdminAuditLogView,
    ApprovalDelegationViewSet,
    OOOPeriodViewSet,
    TimesheetViewSet,
)

timesheet_router = DefaultRouter()
timesheet_router.register(r'', TimesheetViewSet, basename='timesheet')

ooo_router = DefaultRouter()
ooo_router.register(r'', OOOPeriodViewSet, basename='ooo-period')

delegation_router = DefaultRouter()
delegation_router.register(r'', ApprovalDelegationViewSet, basename='delegation')

urlpatterns = [
    path('timesheets/audit-log/', AdminAuditLogView.as_view(), name='audit_log'),
    path('timesheets/', include(timesheet_router.urls)),
    path('ooo-periods/', include(ooo_router.urls)),
    path('delegations/', include(delegation_router.urls)),
]
