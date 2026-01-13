from django.contrib import admin

from .models import TimeEntry


@admin.register(TimeEntry)
class TimeEntryAdmin(admin.ModelAdmin):
    list_display = ('user', 'project', 'date', 'hours', 'billing_rate', 'rate_source', 'is_timer_entry')
    list_filter = ('rate_source', 'is_timer_entry', 'date', 'project')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'project__name', 'description')
    date_hierarchy = 'date'
    ordering = ('-date', '-created_at')
    readonly_fields = ('billing_rate', 'rate_source', 'timer_started_at', 'timer_stopped_at')

    fieldsets = (
        (None, {'fields': ('user', 'project', 'timesheet', 'date', 'hours', 'description')}),
        ('Billing', {'fields': ('billing_rate', 'rate_source')}),
        ('Timer', {'fields': ('is_timer_entry', 'timer_started_at', 'timer_stopped_at')}),
    )
