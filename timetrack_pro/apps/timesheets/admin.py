from django.contrib import admin

from .models import Timesheet, TimesheetComment, OOOPeriod, AdminOverride, ApprovalDelegation


class TimesheetCommentInline(admin.TabularInline):
    model = TimesheetComment
    extra = 0
    readonly_fields = ('author', 'text', 'entry', 'resolved', 'resolved_at', 'created_at')


class AdminOverrideInline(admin.TabularInline):
    model = AdminOverride
    extra = 0
    readonly_fields = ('admin', 'action', 'reason', 'previous_status', 'created_at')


@admin.register(Timesheet)
class TimesheetAdmin(admin.ModelAdmin):
    list_display = ('user', 'week_start', 'status', 'submitted_at', 'approved_by', 'approved_at')
    list_filter = ('status', 'week_start')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    date_hierarchy = 'week_start'
    ordering = ('-week_start',)
    inlines = [TimesheetCommentInline, AdminOverrideInline]

    fieldsets = (
        (None, {'fields': ('user', 'week_start', 'status')}),
        ('Workflow', {'fields': ('submitted_at', 'approved_at', 'approved_by', 'locked_at')}),
    )


@admin.register(TimesheetComment)
class TimesheetCommentAdmin(admin.ModelAdmin):
    list_display = ('timesheet', 'author', 'entry', 'resolved', 'created_at')
    list_filter = ('resolved', 'created_at')
    search_fields = ('author__email', 'text')


@admin.register(OOOPeriod)
class OOOPeriodAdmin(admin.ModelAdmin):
    list_display = ('user', 'start_date', 'end_date')
    list_filter = ('start_date', 'end_date')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    date_hierarchy = 'start_date'


@admin.register(AdminOverride)
class AdminOverrideAdmin(admin.ModelAdmin):
    list_display = ('timesheet', 'admin', 'action', 'previous_status', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = ('admin__email', 'reason')
    readonly_fields = ('timesheet', 'admin', 'action', 'reason', 'previous_status', 'created_at')


@admin.register(ApprovalDelegation)
class ApprovalDelegationAdmin(admin.ModelAdmin):
    list_display = ('delegator', 'delegate', 'start_date', 'end_date')
    list_filter = ('start_date', 'end_date')
    search_fields = ('delegator__email', 'delegate__email')
    date_hierarchy = 'start_date'
