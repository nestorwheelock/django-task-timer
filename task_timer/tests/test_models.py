"""
Tests for task_timer models
Following TDD: Write tests first, then implement models
"""
import pytest
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from task_timer.models import TimerSession, TimerSettings


@pytest.mark.django_db
class TestTimerSession:
    """Tests for TimerSession model"""

    def test_create_timer_session(self):
        """Test creating a new timer session"""
        user = User.objects.create_user(username='testuser', password='testpass')
        session = TimerSession.objects.create(
            task='Write tests for timer',
            notes='Starting with model tests',
            created_by=user,
            status='running'
        )

        assert session.task == 'Write tests for timer'
        assert session.notes == 'Starting with model tests'
        assert session.created_by == user
        assert session.status == 'running'
        assert session.start_time is not None
        assert session.end_time is None
        assert session.duration == 0
        assert session.pause_duration == 0

    def test_timer_session_status_choices(self):
        """Test that status field accepts valid choices"""
        user = User.objects.create_user(username='testuser', password='testpass')

        valid_statuses = ['running', 'paused', 'completed', 'stopped']
        for status in valid_statuses:
            session = TimerSession.objects.create(
                task='Test task',
                created_by=user,
                status=status
            )
            assert session.status == status

    def test_complete_session(self):
        """Test completing a timer session"""
        user = User.objects.create_user(username='testuser', password='testpass')
        session = TimerSession.objects.create(
            task='Test task',
            created_by=user,
            status='running'
        )

        # Simulate 25 minutes of work
        session.duration = 1500  # 25 minutes in seconds
        session.status = 'completed'
        session.end_time = timezone.now()
        session.save()

        assert session.status == 'completed'
        assert session.duration == 1500
        assert session.end_time is not None

    def test_pause_session(self):
        """Test pausing a timer session"""
        user = User.objects.create_user(username='testuser', password='testpass')
        session = TimerSession.objects.create(
            task='Test task',
            created_by=user,
            status='running',
            duration=300  # 5 minutes worked
        )

        session.status = 'paused'
        session.pause_duration = 120  # 2 minutes paused
        session.save()

        assert session.status == 'paused'
        assert session.duration == 300
        assert session.pause_duration == 120

    def test_str_representation(self):
        """Test string representation of timer session"""
        user = User.objects.create_user(username='testuser', password='testpass')
        session = TimerSession.objects.create(
            task='Test task',
            created_by=user,
            status='running'
        )

        expected = f"Test task - running"
        assert str(session) == expected

    def test_session_ordering(self):
        """Test that sessions are ordered by start_time descending"""
        user = User.objects.create_user(username='testuser', password='testpass')

        # Create sessions with different times
        session1 = TimerSession.objects.create(
            task='First task',
            created_by=user,
            status='completed'
        )
        session2 = TimerSession.objects.create(
            task='Second task',
            created_by=user,
            status='running'
        )

        sessions = list(TimerSession.objects.all())
        assert sessions[0] == session2  # Most recent first
        assert sessions[1] == session1

    def test_get_duration_minutes(self):
        """Test getting duration in minutes"""
        user = User.objects.create_user(username='testuser', password='testpass')
        session = TimerSession.objects.create(
            task='Test task',
            created_by=user,
            status='completed',
            duration=1500  # 25 minutes
        )

        assert session.get_duration_minutes() == 25.0

    def test_get_duration_formatted(self):
        """Test getting formatted duration string"""
        user = User.objects.create_user(username='testuser', password='testpass')
        session = TimerSession.objects.create(
            task='Test task',
            created_by=user,
            status='completed',
            duration=3665  # 1 hour, 1 minute, 5 seconds
        )

        assert session.get_duration_formatted() == "1h 1m"


@pytest.mark.django_db
class TestTimerSettings:
    """Tests for TimerSettings model"""

    def test_create_timer_settings(self):
        """Test creating timer settings (auto-created by signal)"""
        user = User.objects.create_user(username='testuser', password='testpass')

        # Settings should be auto-created by signal
        settings = TimerSettings.objects.get(user=user)

        assert settings.user == user
        assert settings.work_duration == 25
        assert settings.short_break_duration == 5
        assert settings.long_break_duration == 15
        assert settings.auto_start_breaks is False

    def test_default_settings(self):
        """Test that default settings are applied"""
        user = User.objects.create_user(username='testuser', password='testpass')

        # Settings auto-created by signal
        settings = TimerSettings.objects.get(user=user)

        assert settings.work_duration == 25
        assert settings.short_break_duration == 5
        assert settings.long_break_duration == 15
        assert settings.auto_start_breaks is False

    def test_one_settings_per_user(self):
        """Test that each user has only one settings object"""
        user = User.objects.create_user(username='testuser', password='testpass')

        # Settings auto-created by signal
        settings1 = TimerSettings.objects.get(user=user)

        # Trying to create another should fail with unique constraint
        with pytest.raises(Exception):  # IntegrityError
            TimerSettings.objects.create(user=user)

    def test_str_representation(self):
        """Test string representation of settings"""
        user = User.objects.create_user(username='testuser', password='testpass')

        # Settings auto-created by signal
        settings = TimerSettings.objects.get(user=user)

        expected = f"Settings for testuser"
        assert str(settings) == expected

    def test_get_work_duration_seconds(self):
        """Test getting work duration in seconds"""
        user = User.objects.create_user(username='testuser', password='testpass')

        # Settings auto-created by signal, modify them
        settings = TimerSettings.objects.get(user=user)
        settings.work_duration = 25
        settings.save()

        assert settings.get_work_duration_seconds() == 1500
