"""
Modèles pour le suivi de progression - StudyFlow
Correspond à Progress.tsx du frontend
"""
from django.db import models
from django.conf import settings


class DailyProgress(models.Model):
    """Suivi quotidien de la productivité."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='daily_progress'
    )
    date = models.DateField()
    tasks_completed = models.PositiveIntegerField(default=0)
    tasks_total = models.PositiveIntegerField(default=0)
    pomodoro_sessions = models.PositiveIntegerField(default=0)
    study_time_minutes = models.PositiveIntegerField(default=0)
    productivity_score = models.FloatField(default=0.0)

    class Meta:
        unique_together = ['user', 'date']
        ordering = ['-date']
        verbose_name = 'Progression Quotidienne'
        verbose_name_plural = 'Progressions Quotidiennes'

    def __str__(self):
        return f"{self.user.email} - {self.date}"

    def calculate_score(self):
        """Calcule un score de productivité sur 100."""
        if self.tasks_total == 0:
            return 0
        completion_rate = (self.tasks_completed / self.tasks_total) * 100
        time_bonus = min(self.study_time_minutes / 120, 1) * 20  # Max 20 bonus points
        self.productivity_score = min(round(completion_rate + time_bonus, 1), 100)
        return self.productivity_score
