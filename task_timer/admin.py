"""
Django admin configuration for task_timer
"""
from django.contrib import admin
from django.utils.html import format_html
from task_timer.models import TimerSession, TimerSettings


@admin.register(TimerSession)
class TimerSessionAdmin(admin.ModelAdmin):
    """Admin interface for TimerSession"""

    list_display = [
        'task_short',
        'status_badge',
        'duration_display',
        'created_by',
        'start_time',
        'end_time'
    ]

    list_filter = [
        'status',
        'created_by',
        'start_time'
    ]

    search_fields = [
        'task',
        'notes',
        'created_by__username'
    ]

    readonly_fields = [
        'start_time',
        'duration_display',
        'pause_duration_display'
    ]

    fieldsets = (
        ('Task Information', {
            'fields': ('task', 'notes', 'created_by')
        }),
        ('Session Status', {
            'fields': ('status', 'start_time', 'end_time')
        }),
        ('Duration', {
            'fields': ('duration_display', 'pause_duration_display')
        }),
    )

    date_hierarchy = 'start_time'

    def task_short(self, obj):
        """Display shortened task description"""
        if len(obj.task) > 50:
            return obj.task[:50] + '...'
        return obj.task
    task_short.short_description = 'Task'

    def status_badge(self, obj):
        """Display status as colored badge"""
        colors = {
            'running': '#28a745',  # green
            'paused': '#ffc107',   # yellow
            'completed': '#007bff', # blue
            'stopped': '#6c757d'   # gray
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.status.upper()
        )
    status_badge.short_description = 'Status'

    def duration_display(self, obj):
        """Display formatted duration"""
        return obj.get_duration_formatted()
    duration_display.short_description = 'Duration'

    def pause_duration_display(self, obj):
        """Display formatted pause duration"""
        if obj.pause_duration > 0:
            minutes = obj.pause_duration // 60
            return f"{minutes}m"
        return "-"
    pause_duration_display.short_description = 'Pause Duration'

    actions = ['mark_as_completed', 'mark_as_stopped']

    def mark_as_completed(self, request, queryset):
        """Mark selected sessions as completed"""
        count = queryset.update(status='completed')
        self.message_user(request, f'{count} sessions marked as completed')
    mark_as_completed.short_description = 'Mark selected as completed'

    def mark_as_stopped(self, request, queryset):
        """Mark selected sessions as stopped"""
        count = queryset.update(status='stopped')
        self.message_user(request, f'{count} sessions marked as stopped')
    mark_as_stopped.short_description = 'Mark selected as stopped'


@admin.register(TimerSettings)
class TimerSettingsAdmin(admin.ModelAdmin):
    """Admin interface for TimerSettings"""

    list_display = [
        'user',
        'work_duration',
        'short_break_duration',
        'long_break_duration',
        'auto_start_breaks'
    ]

    list_filter = [
        'auto_start_breaks'
    ]

    search_fields = [
        'user__username'
    ]

    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Work Durations (minutes)', {
            'fields': ('work_duration', 'short_break_duration', 'long_break_duration')
        }),
        ('Preferences', {
            'fields': ('auto_start_breaks',)
        }),
    )

    def has_add_permission(self, request):
        """Prevent manual creation (created automatically)"""
        return True

    def has_delete_permission(self, request, obj=None):
        """Allow deletion"""
        return True
