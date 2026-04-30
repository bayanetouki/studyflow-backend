"""
Serializers pour les tâches
"""
from rest_framework import serializers
from .models import Task, PomodoroSession, CalendarEvent


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'priority',
            'completed', 'due_date', 'estimated_time',
            'view_mode', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class TaskToggleSerializer(serializers.ModelSerializer):
    """Serializer léger pour juste cocher/décocher une tâche."""
    class Meta:
        model = Task
        fields = ['id', 'completed']


class PomodoroSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PomodoroSession
        fields = [
            'id', 'task', 'duration_minutes', 'break_duration',
            'completed', 'started_at', 'ended_at'
        ]
        read_only_fields = ['id', 'started_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class CalendarEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalendarEvent
        fields = [
            'id', 'task', 'title', 'description',
            'start_datetime', 'end_datetime', 'color', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
