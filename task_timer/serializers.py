"""
Serializers for task_timer API
"""
from rest_framework import serializers
from task_timer.models import TimerSession, TimerSettings


class TimerSessionSerializer(serializers.ModelSerializer):
    """Serializer for TimerSession model"""

    duration_minutes = serializers.SerializerMethodField()
    duration_formatted = serializers.SerializerMethodField()

    class Meta:
        model = TimerSession
        fields = [
            'id',
            'task',
            'notes',
            'start_time',
            'end_time',
            'duration',
            'duration_minutes',
            'duration_formatted',
            'pause_duration',
            'status',
            'created_by'
        ]
        read_only_fields = ['id', 'start_time', 'end_time', 'created_by', 'status']

    def get_duration_minutes(self, obj):
        return obj.get_duration_minutes()

    def get_duration_formatted(self, obj):
        return obj.get_duration_formatted()


class TimerSettingsSerializer(serializers.ModelSerializer):
    """Serializer for TimerSettings model"""

    class Meta:
        model = TimerSettings
        fields = [
            'id',
            'work_duration',
            'short_break_duration',
            'long_break_duration',
            'auto_start_breaks'
        ]
        read_only_fields = ['id']
