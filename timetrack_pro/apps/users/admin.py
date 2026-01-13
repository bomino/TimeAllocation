from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, UserDeactivationAudit


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role', 'company', 'is_active')
    list_filter = ('role', 'is_active', 'company')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'username')}),
        ('Organization', {'fields': ('company', 'role', 'manager')}),
        ('Preferences', {'fields': ('timezone', 'workflow_notifications_enabled', 'security_notifications_enabled')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'first_name', 'last_name', 'company', 'password1', 'password2'),
        }),
    )


@admin.register(UserDeactivationAudit)
class UserDeactivationAuditAdmin(admin.ModelAdmin):
    list_display = ('user', 'admin', 'was_forced', 'created_at')
    list_filter = ('was_forced', 'created_at')
    search_fields = ('user__email', 'admin__email', 'reason')
    readonly_fields = ('user', 'admin', 'reason', 'was_forced', 'pending_timesheets_at_deactivation', 'export_data', 'created_at')
