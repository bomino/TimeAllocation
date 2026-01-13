from django.contrib import admin

from .models import Rate


@admin.register(Rate)
class RateAdmin(admin.ModelAdmin):
    list_display = ('rate_type', 'company', 'employee', 'project', 'hourly_rate', 'effective_from', 'effective_to')
    list_filter = ('rate_type', 'company', 'effective_from')
    search_fields = ('company__name', 'employee__email', 'project__name')
    date_hierarchy = 'effective_from'
    ordering = ('-effective_from',)

    fieldsets = (
        (None, {'fields': ('company', 'rate_type', 'hourly_rate')}),
        ('Scope', {'fields': ('employee', 'project')}),
        ('Validity', {'fields': ('effective_from', 'effective_to')}),
    )
