"""
URL configuration for Users app.
"""
from django.urls import path

from apps.users.views import (
    LoginView,
    LogoutView,
    CustomTokenRefreshView,
    UserProfileView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    UserDeactivationView,
    UserDeactivationStatusView,
)

app_name = 'users'

urlpatterns = [
    # Auth endpoints
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('auth/password/reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('auth/password/reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    # User profile
    path('users/me/', UserProfileView.as_view(), name='profile'),

    # User management (admin only)
    path('users/<int:pk>/deactivate/', UserDeactivationView.as_view(), name='user_deactivate'),
    path('users/<int:pk>/deactivation-status/', UserDeactivationStatusView.as_view(), name='user_deactivation_status'),
]
