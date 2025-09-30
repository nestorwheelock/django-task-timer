"""
TimerEngine: Business logic for timer operations

Handles all timer-related operations:
- Starting/stopping/pausing/resuming sessions
- Session history and statistics
- User settings management
"""
from django.utils import timezone
from datetime import timedelta
from task_timer.models import TimerSession, TimerSettings


class TimerEngine:
    """
    Service layer for timer operations
    """

    def __init__(self, user):
        """
        Initialize timer engine for a specific user

        Args:
            user: Django User instance
        """
        self.user = user

    def start_session(self, task, notes=''):
        """
        Start a new timer session

        Args:
            task: Description of the task
            notes: Optional notes about the task

        Returns:
            TimerSession instance

        Raises:
            ValueError: If user already has an active session
        """
        # Check if user has an active session
        active_session = self.get_active_session()
        if active_session:
            raise ValueError(f"User {self.user.username} already has an active session")

        # Create new session
        session = TimerSession.objects.create(
            task=task,
            notes=notes,
            created_by=self.user,
            status='running'
        )

        return session

    def get_active_session(self):
        """
        Get user's currently active session (running or paused)

        Returns:
            TimerSession instance or None
        """
        return TimerSession.objects.filter(
            created_by=self.user,
            status__in=['running', 'paused']
        ).first()

    def pause_session(self):
        """
        Pause the active session

        Returns:
            TimerSession instance

        Raises:
            ValueError: If no active session
        """
        session = self.get_active_session()
        if not session:
            raise ValueError("No active session to pause")

        if session.status != 'running':
            raise ValueError("Can only pause running sessions")

        session.status = 'paused'
        session.save()

        return session

    def resume_session(self):
        """
        Resume a paused session

        Returns:
            TimerSession instance

        Raises:
            ValueError: If no paused session
        """
        session = TimerSession.objects.filter(
            created_by=self.user,
            status='paused'
        ).first()

        if not session:
            raise ValueError("No paused session to resume")

        session.status = 'running'
        session.save()

        return session

    def stop_session(self):
        """
        Stop the active session (manual stop before completion)

        Returns:
            TimerSession instance

        Raises:
            ValueError: If no active session
        """
        session = self.get_active_session()
        if not session:
            raise ValueError("No active session to stop")

        session.status = 'stopped'
        session.end_time = timezone.now()
        session.save()

        return session

    def complete_session(self):
        """
        Mark session as completed (timer reached 0)

        Returns:
            TimerSession instance

        Raises:
            ValueError: If no active session
        """
        session = self.get_active_session()
        if not session:
            raise ValueError("No active session to complete")

        session.status = 'completed'
        session.end_time = timezone.now()
        session.save()

        return session

    def update_session_duration(self, duration):
        """
        Update the duration of the active session

        Args:
            duration: Duration in seconds

        Returns:
            TimerSession instance

        Raises:
            ValueError: If no active session
        """
        session = self.get_active_session()
        if not session:
            raise ValueError("No active session to update")

        session.duration = duration
        session.save()

        return session

    def get_session_history(self, start_date=None, end_date=None, status=None):
        """
        Get user's session history with optional filtering

        Args:
            start_date: Filter sessions after this date (optional)
            end_date: Filter sessions before this date (optional)
            status: Filter by session status (optional)

        Returns:
            QuerySet of TimerSession instances
        """
        queryset = TimerSession.objects.filter(created_by=self.user)

        if start_date:
            queryset = queryset.filter(start_time__gte=start_date)

        if end_date:
            queryset = queryset.filter(start_time__lte=end_date)

        if status:
            queryset = queryset.filter(status=status)

        return queryset

    def get_daily_stats(self, date=None):
        """
        Get statistics for a specific day

        Args:
            date: Date to get stats for (defaults to today)

        Returns:
            dict with keys: total_sessions, completed_sessions, total_minutes
        """
        if date is None:
            date = timezone.now().date()

        # Get start and end of day
        start = timezone.make_aware(
            timezone.datetime.combine(date, timezone.datetime.min.time())
        )
        end = start + timedelta(days=1)

        sessions = TimerSession.objects.filter(
            created_by=self.user,
            start_time__gte=start,
            start_time__lt=end
        )

        total_sessions = sessions.count()
        completed_sessions = sessions.filter(status='completed').count()
        total_seconds = sum(s.duration for s in sessions)
        total_minutes = total_seconds // 60

        return {
            'total_sessions': total_sessions,
            'completed_sessions': completed_sessions,
            'total_minutes': total_minutes
        }

    def get_weekly_stats(self, date=None):
        """
        Get statistics for a specific week

        Args:
            date: Date in the week to get stats for (defaults to current week)

        Returns:
            dict with keys: total_sessions, completed_sessions, total_minutes
        """
        if date is None:
            date = timezone.now().date()

        # Get start of week (Monday)
        start = timezone.make_aware(
            timezone.datetime.combine(
                date - timedelta(days=date.weekday()),
                timezone.datetime.min.time()
            )
        )
        end = start + timedelta(days=7)

        sessions = TimerSession.objects.filter(
            created_by=self.user,
            start_time__gte=start,
            start_time__lt=end
        )

        total_sessions = sessions.count()
        completed_sessions = sessions.filter(status='completed').count()
        total_seconds = sum(s.duration for s in sessions)
        total_minutes = total_seconds // 60

        return {
            'total_sessions': total_sessions,
            'completed_sessions': completed_sessions,
            'total_minutes': total_minutes
        }

    def get_or_create_settings(self):
        """
        Get or create user settings with defaults

        Returns:
            TimerSettings instance
        """
        settings, created = TimerSettings.objects.get_or_create(
            user=self.user,
            defaults={
                'work_duration': 25,
                'short_break_duration': 5,
                'long_break_duration': 15,
                'auto_start_breaks': False
            }
        )

        return settings
