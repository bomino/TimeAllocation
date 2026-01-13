from django.contrib import admin

from .models import Company, CompanySettings, CompanySettingsAudit


class CompanySettingsInline(admin.StackedInline):
    model = CompanySettings
    can_delete = False


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'week_start_day', 'timezone', 'created_at')
    search_fields = ('name',)
    list_filter = ('week_start_day',)
    inlines = [CompanySettingsInline]


@admin.register(CompanySettings)
class CompanySettingsAdmin(admin.ModelAdmin):
    list_display = ('company', 'unlock_window_days', 'daily_warning_threshold', 'default_hourly_rate')
    search_fields = ('company__name',)


@admin.register(CompanySettingsAudit)
class CompanySettingsAuditAdmin(admin.ModelAdmin):
    list_display = ('company_settings', 'changed_by', 'field_name', 'old_value', 'new_value', 'created_at')
    list_filter = ('field_name', 'created_at')
    search_fields = ('company_settings__company__name', 'changed_by__email')
    readonly_fields = ('company_settings', 'changed_by', 'field_name', 'old_value', 'new_value', 'created_at')
