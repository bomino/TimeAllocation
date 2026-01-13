"""
URL configuration for TimeTrack Pro.
"""
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),

    # API v1
    path('api/v1/', include('apps.users.urls')),
    path('api/v1/projects/', include('apps.projects.urls')),
    path('api/v1/time-entries/', include('apps.timeentries.urls')),
    path('api/v1/', include('apps.timesheets.urls')),
    path('api/v1/rates/', include('apps.rates.urls')),
    path('api/v1/reports/', include('apps.reports.urls')),

    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
