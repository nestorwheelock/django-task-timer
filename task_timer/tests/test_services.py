"""
Tests for timer service layer
Following TDD: Write tests first, then implement service
"""
import pytest
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from task_timer.models import TimerSession, TimerSettings
from task_timer.services import TimerEngine


@pytest.mark.django_db
class TestTimerEngine:
    """Tests for TimerEngine service"""

    def test_start_session(self):
        """Test starting a new timer session"""
        user = User.objects.create_user(username='testuser', password='testpass')
        engine = TimerEngine(user=user)

        session = engine.start_session(
            task='Write tests',
            notes='Testing timer engine'
        )

        assert session.task == 'Write tests'
        assert session.notes == 'Testing timer engine'
        assert session.status == 'running'
        assert session.created_by == user
        assert session.duration == 0

    def test_cannot_start_multiple_sessions(self):
        """Test that user cannot start multiple sessions simultaneously"""
        user = User.objects.create_user(username='testuser', password='testpass')
        engine = TimerEngine(user=user)

        # Start first session
        session1 = engine.start_session(task='First task')

        # Attempt to start second session should fail
        with pytest.raises(ValueError, match="already has an active session"):
            engine.start_session(task='Second task')

    def test_get_active_session(self):
        """Test getting user's active session"""
        user = User.objects.create_user(username='testuser', password='testpass')
        engine = TimerEngine(user=user)

        # No active session initially
        assert engine.get_active_session() is None

        # Start session
        session = engine.start_session(task='Test task')

        # Should return active session
        active = engine.get_active_session()
        assert active == session
        assert active.status == 'running'

    def test_pause_session(self):
        """Test pausing an active session"""
        user = User.objects.create_user(username='testuser', password='testpass')
        engine = TimerEngine(user=user)

        session = engine.start_session(task='Test task')

        # Pause the session
        paused = engine.pause_session()

        assert paused.status == 'paused'
        assert paused == session

    def test_pause_without_active_session(self):
        """Test pausing when no active session"""
        user = User.objects.create_user(username='testuser', password='testpass')
        engine = TimerEngine(user=user)

        with pytest.raises(ValueError, match="No active session"):
            engine.pause_session()

    def test_resume_session(self):
        """Test resuming a paused session"""
        user = User.objects.create_user(username='testuser', password='testpass')
        engine = TimerEngine(user=user)

        session = engine.start_session(task='Test task')
        engine.pause_session()

        # Resume the session
        resumed = engine.resume_session()

        assert resumed.status == 'running'
        assert resumed == session

    def test_resume_without_paused_session(self):
        """Test resuming when no paused session"""
        user = User.objects.create_user(username='testuser', password='testpass')
        engine = TimerEngine(user=user)

        with pytest.raises(ValueError, match="No paused session"):
            engine.resume_session()

    def test_stop_session(self):
        """Test stopping an active session"""
        user = User.objects.create_user(username='testuser', password='testpass')
        engine = TimerEngine(user=user)

        session = engine.start_session(task='Test task')

        # Simulate some work time
        session.duration = 600  # 10 minutes
        session.save()

        # Stop the session
        stopped = engine.stop_session()

        assert stopped.status == 'stopped'
        assert stopped.end_time is not None
        assert stopped.duration == 600

    def test_complete_session(self):
        """Test completing a session (timer reached 0)"""
        user = User.objects.create_user(username='testuser', password='testpass')
        engine = TimerEngine(user=user)

        session = engine.start_session(task='Test task')

        # Simulate completing a full Pomodoro (25 minutes)
        session.duration = 1500
        session.save()

        # Complete the session
        completed = engine.complete_session()

        assert completed.status == 'completed'
        assert completed.end_time is not None
        assert completed.duration == 1500

    def test_get_session_history(self):
        """Test retrieving user's session history"""
        user = User.objects.create_user(username='testuser', password='testpass')
        engine = TimerEngine(user=user)

        # Create some completed sessions
        for i in range(3):
            TimerSession.objects.create(
                task=f'Task {i+1}',
                created_by=user,
                status='completed',
                duration=1500
            )

        history = engine.get_session_history()

        assert history.count() == 3
        # Should be ordered by most recent first
        assert history[0].task == 'Task 3'

    def test_get_session_history_with_filters(self):
        """Test filtering session history by date"""
        user = User.objects.create_user(username='testuser', password='testpass')
        engine = TimerEngine(user=user)

        # Create sessions from yesterday and today
        yesterday = timezone.now() - timedelta(days=1)

        # Yesterday's session
        old_session = TimerSession.objects.create(
            task='Old task',
            created_by=user,
            status='completed',
            duration=1500
        )
        old_session.start_time = yesterday
        old_session.save()

        # Today's session
        TimerSession.objects.create(
            task='Recent task',
            created_by=user,
            status='completed',
            duration=1500
        )

        # Get today's sessions
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_sessions = engine.get_session_history(start_date=today_start)

        assert today_sessions.count() == 1
        assert today_sessions[0].task == 'Recent task'

    def test_get_daily_stats(self):
        """Test getting daily statistics"""
        user = User.objects.create_user(username='testuser', password='testpass')
        engine = TimerEngine(user=user)

        # Create some completed sessions today
        for i in range(3):
            TimerSession.objects.create(
                task=f'Task {i+1}',
                created_by=user,
                status='completed',
                duration=1500  # 25 minutes each
            )

        stats = engine.get_daily_stats()

        assert stats['total_sessions'] == 3
        assert stats['total_minutes'] == 75  # 3 * 25
        assert stats['completed_sessions'] == 3

    def test_get_weekly_stats(self):
        """Test getting weekly statistics"""
        user = User.objects.create_user(username='testuser', password='testpass')
        engine = TimerEngine(user=user)

        # Create sessions from this week
        for i in range(5):
            TimerSession.objects.create(
                task=f'Task {i+1}',
                created_by=user,
                status='completed',
                duration=1500
            )

        stats = engine.get_weekly_stats()

        assert stats['total_sessions'] == 5
        assert stats['total_minutes'] == 125  # 5 * 25
        assert stats['completed_sessions'] == 5

    def test_update_session_duration(self):
        """Test updating session duration"""
        user = User.objects.create_user(username='testuser', password='testpass')
        engine = TimerEngine(user=user)

        session = engine.start_session(task='Test task')

        # Update duration to 10 minutes
        updated = engine.update_session_duration(600)

        assert updated.duration == 600
        assert updated == session

    def test_get_or_create_settings(self):
        """Test getting or creating user settings"""
        user = User.objects.create_user(username='testuser', password='testpass')
        engine = TimerEngine(user=user)

        # Should create settings with defaults
        settings = engine.get_or_create_settings()

        assert settings.user == user
        assert settings.work_duration == 25
        assert settings.short_break_duration == 5
        assert settings.long_break_duration == 15

        # Calling again should return same settings
        settings2 = engine.get_or_create_settings()
        assert settings == settings2
