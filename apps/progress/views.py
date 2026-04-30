"""
Views pour le suivi de progression - StudyFlow
"""
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from datetime import timedelta

from apps.tasks.models import Task, PomodoroSession
from .models import DailyProgress
from .serializers import DailyProgressSerializer


class ProgressSummaryView(APIView):
    """
    GET /api/v1/progress/summary/
    Résumé complet de la progression (utilisé par Progress.tsx).
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)

        tasks = Task.objects.filter(user=user)
        sessions = PomodoroSession.objects.filter(user=user)

        # Stats globales
        total_tasks = tasks.count()
        completed_tasks = tasks.filter(completed=True).count()

        # Stats semaine
        weekly_tasks = tasks.filter(updated_at__date__gte=week_ago)
        weekly_completed = weekly_tasks.filter(completed=True).count()
        weekly_sessions = sessions.filter(started_at__date__gte=week_ago, completed=True).count()
        weekly_time = sum(s.duration_minutes for s in sessions.filter(
            started_at__date__gte=week_ago, completed=True
        ))

        # Stats mois
        monthly_tasks = tasks.filter(updated_at__date__gte=month_ago)
        monthly_completed = monthly_tasks.filter(completed=True).count()

        # Données pour le graphique (7 derniers jours)
        daily_data = []
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            day_tasks = tasks.filter(updated_at__date=day)
            day_completed = day_tasks.filter(completed=True).count()
            daily_data.append({
                'date': day.strftime('%Y-%m-%d'),
                'day_label': day.strftime('%a'),
                'tasks_completed': day_completed,
                'tasks_total': day_tasks.count(),
            })

        return Response({
            'global': {
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'completion_rate': round((completed_tasks / total_tasks * 100), 1) if total_tasks > 0 else 0,
            },
            'weekly': {
                'tasks_completed': weekly_completed,
                'pomodoro_sessions': weekly_sessions,
                'study_time_minutes': weekly_time,
            },
            'monthly': {
                'tasks_completed': monthly_completed,
            },
            'daily_chart': daily_data,
        })


class DailyProgressListView(generics.ListAPIView):
    """
    GET /api/v1/progress/daily/
    Historique de progression quotidienne.
    """
    serializer_class = DailyProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return DailyProgress.objects.filter(user=self.request.user)[:30]
