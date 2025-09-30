"""
Django signals for task_timer

Automatically creates TimerSettings when a new User is created
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from task_timer.models import TimerSettings


@receiver(post_save, sender=User)
def create_timer_settings(sender, instance, created, **kwargs):
    """
    Automatically create TimerSettings with defaults when a new User is created

    Args:
        sender: The model class (User)
        instance: The actual User instance
        created: Boolean; True if a new record was created
        **kwargs: Additional keyword arguments
    """
    if created:
        TimerSettings.objects.create(
            user=instance,
            work_duration=25,
            short_break_duration=5,
            long_break_duration=15,
            auto_start_breaks=False
        )
