"""
Tests for Django signals
Following TDD: Write tests first, then implement signals
"""
import pytest
from django.contrib.auth.models import User
from task_timer.models import TimerSettings


@pytest.mark.django_db
class TestUserSignals:
    """Tests for user-related signals"""

    def test_user_creation_auto_creates_timer_settings(self):
        """
        When a new user is created, TimerSettings should be automatically
        created with default values
        """
        # Create a new user
        user = User.objects.create_user(
            username='testuser',
            password='testpass',
            email='test@example.com'
        )

        # TimerSettings should automatically exist for this user
        assert TimerSettings.objects.filter(user=user).exists()

        # Verify default settings values
        settings = TimerSettings.objects.get(user=user)
        assert settings.work_duration == 25
        assert settings.short_break_duration == 5
        assert settings.long_break_duration == 15
        assert settings.auto_start_breaks is False

    def test_existing_settings_not_overwritten(self):
        """
        If settings already exist for a user, they should not be overwritten
        """
        # Create user with custom settings
        user = User.objects.create_user(username='testuser', password='testpass')
        settings = TimerSettings.objects.get(user=user)

        # Modify settings
        settings.work_duration = 50
        settings.short_break_duration = 10
        settings.save()

        # Re-save the user (simulating an update)
        user.email = 'newemail@example.com'
        user.save()

        # Settings should not be reset to defaults
        settings.refresh_from_db()
        assert settings.work_duration == 50
        assert settings.short_break_duration == 10

    def test_multiple_users_get_separate_settings(self):
        """Each user should get their own TimerSettings instance"""
        user1 = User.objects.create_user(username='user1', password='pass1')
        user2 = User.objects.create_user(username='user2', password='pass2')

        settings1 = TimerSettings.objects.get(user=user1)
        settings2 = TimerSettings.objects.get(user=user2)

        assert settings1.id != settings2.id
        assert settings1.user == user1
        assert settings2.user == user2
