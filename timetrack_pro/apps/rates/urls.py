"""
URL configuration for Rates app.
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.rates.views import EffectiveRateView, RateViewSet

router = DefaultRouter()
router.register(r'', RateViewSet, basename='rate')

urlpatterns = [
    path('effective/', EffectiveRateView.as_view(), name='effective_rate'),
    path('', include(router.urls)),
]
