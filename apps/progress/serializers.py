from rest_framework import serializers
from .models import DailyProgress


class DailyProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyProgress
        fields = [
            'id', 'date', 'tasks_completed', 'tasks_total',
            'pomodoro_sessions', 'study_time_minutes', 'productivity_score'
        ]
        read_only_fields = ['id']
