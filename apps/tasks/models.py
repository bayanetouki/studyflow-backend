"""
Modèles pour la gestion des tâches - StudyFlow
"""
from django.db import models
from django.conf import settings


class Task(models.Model):
    """
    Tâche principale. Correspond à l'interface TaskOrganization du frontend.
    """
    PRIORITY_CHOICES = [
        ('high', 'Haute'),
        ('medium', 'Moyenne'),
        ('low', 'Faible'),
    ]
    VIEW_MODE_CHOICES = [
        ('daily', 'Quotidien'),
        ('weekly', 'Hebdomadaire'),
        ('monthly', 'Mensuel'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tasks'
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    completed = models.BooleanField(default=False)
    due_date = models.DateField(null=True, blank=True)
    estimated_time = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Temps estimé en minutes"
    )
    view_mode = models.CharField(max_length=10, choices=VIEW_MODE_CHOICES, default='daily')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Tâche'
        verbose_name_plural = 'Tâches'

    def __str__(self):
        return f"{self.user.email} - {self.title}"


class PomodoroSession(models.Model):
    """
    Session Pomodoro. Correspond à TimeManagement.tsx du frontend.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='pomodoro_sessions'
    )
    task = models.ForeignKey(
        Task,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='pomodoro_sessions'
    )
    duration_minutes = models.PositiveIntegerField(default=25)
    break_duration = models.PositiveIntegerField(default=5)
    completed = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-started_at']
        verbose_name = 'Session Pomodoro'
        verbose_name_plural = 'Sessions Pomodoro'

    def __str__(self):
        return f"{self.user.email} - {self.started_at.date()} ({self.duration_minutes}min)"


class CalendarEvent(models.Model):
    """
    Événement calendrier. Correspond à Calendar.tsx du frontend.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='calendar_events'
    )
    task = models.ForeignKey(
        Task,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='calendar_events'
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField(null=True, blank=True)
    color = models.CharField(max_length=20, default='#A0826D')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['start_datetime']
        verbose_name = 'Événement Calendrier'
        verbose_name_plural = 'Événements Calendrier'

    def __str__(self):
        return f"{self.user.email} - {self.title}"
