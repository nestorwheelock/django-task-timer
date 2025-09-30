"""
Models for django-task-timer

TimerSession: Stores individual Pomodoro timer sessions
TimerSettings: User preferences for timer durations
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class TimerSession(models.Model):
    """
    Represents a single Pomodoro timer session
    """
    STATUS_CHOICES = [
        ('running', 'Running'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('stopped', 'Stopped'),
    ]

    task = models.TextField(
        help_text="Description of what you're working on"
    )
    notes = models.TextField(
        blank=True,
        default='',
        help_text="Optional notes about the task"
    )
    start_time = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        help_text="When the session started"
    )
    end_time = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the session completed/stopped"
    )
    duration = models.IntegerField(
        default=0,
        help_text="Total seconds worked (excluding pauses)"
    )
    pause_duration = models.IntegerField(
        default=0,
        help_text="Total seconds paused"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='running',
        db_index=True,
        help_text="Current session status"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='timer_sessions',
        help_text="User who owns this session"
    )

    class Meta:
        verbose_name = "Timer Session"
        verbose_name_plural = "Timer Sessions"
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['created_by', 'status']),
            models.Index(fields=['created_by', 'start_time']),
        ]

    def __str__(self):
        return f"{self.task} - {self.status}"

    def get_duration_minutes(self):
        """Return duration in minutes"""
        return self.duration / 60.0

    def get_duration_formatted(self):
        """Return formatted duration as 'Xh Ym'"""
        minutes = self.duration // 60
        hours = minutes // 60
        remaining_minutes = minutes % 60

        if hours > 0:
            return f"{hours}h {remaining_minutes}m"
        return f"{minutes}m"


class TimerSettings(models.Model):
    """
    User preferences for timer durations
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='timer_settings',
        help_text="User these settings belong to"
    )
    work_duration = models.IntegerField(
        default=25,
        help_text="Work session duration in minutes"
    )
    short_break_duration = models.IntegerField(
        default=5,
        help_text="Short break duration in minutes"
    )
    long_break_duration = models.IntegerField(
        default=15,
        help_text="Long break duration in minutes"
    )
    auto_start_breaks = models.BooleanField(
        default=False,
        help_text="Automatically start break timers"
    )

    class Meta:
        verbose_name = "Timer Settings"
        verbose_name_plural = "Timer Settings"

    def __str__(self):
        return f"Settings for {self.user.username}"

    def get_work_duration_seconds(self):
        """Return work duration in seconds"""
        return self.work_duration * 60
