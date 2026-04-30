"""
Views pour la gestion des tâches - StudyFlow
"""
from rest_framework import generics, permissions, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import Task, PomodoroSession, CalendarEvent
from .serializers import (
    TaskSerializer,
    PomodoroSessionSerializer,
    CalendarEventSerializer
)


class TaskListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/v1/tasks/          → Lister les tâches de l'utilisateur
    POST /api/v1/tasks/          → Créer une nouvelle tâche

    Filtres disponibles : ?priority=high&completed=false&view_mode=daily
    """
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'due_date', 'priority']
    ordering = ['-created_at']

    def get_queryset(self):
        qs = Task.objects.filter(user=self.request.user)
        # Filtres manuels
        priority = self.request.query_params.get('priority')
        completed = self.request.query_params.get('completed')
        view_mode = self.request.query_params.get('view_mode')

        if priority:
            qs = qs.filter(priority=priority)
        if completed is not None:
            qs = qs.filter(completed=completed.lower() == 'true')
        if view_mode:
            qs = qs.filter(view_mode=view_mode)
        return qs


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/v1/tasks/<id>/  → Détail d'une tâche
    PUT    /api/v1/tasks/<id>/  → Modifier une tâche
    DELETE /api/v1/tasks/<id>/  → Supprimer une tâche
    """
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)


class TaskToggleView(APIView):
    """
    PATCH /api/v1/tasks/<id>/toggle/
    Basculer l'état completed d'une tâche (cocher/décocher).
    """
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        task = get_object_or_404(Task, pk=pk, user=request.user)
        task.completed = not task.completed
        task.save()
        return Response(TaskSerializer(task).data)


class TaskStatsView(APIView):
    """
    GET /api/v1/tasks/stats/
    Statistiques de productivité pour la page Progress.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        tasks = Task.objects.filter(user=request.user)
        total = tasks.count()
        completed = tasks.filter(completed=True).count()
        in_progress = tasks.filter(completed=False).count()

        # Par priorité
        high = tasks.filter(priority='high').count()
        medium = tasks.filter(priority='medium').count()
        low = tasks.filter(priority='low').count()

        # Temps estimé total
        total_time = sum(t.estimated_time or 0 for t in tasks.filter(completed=True))

        return Response({
            'total': total,
            'completed': completed,
            'in_progress': in_progress,
            'completion_rate': round((completed / total * 100), 1) if total > 0 else 0,
            'by_priority': {'high': high, 'medium': medium, 'low': low},
            'total_time_completed_minutes': total_time,
        })


# ─────────────────────────────────────────────
# POMODORO
# ─────────────────────────────────────────────

class PomodoroListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/v1/tasks/pomodoro/
    POST /api/v1/tasks/pomodoro/
    """
    serializer_class = PomodoroSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PomodoroSession.objects.filter(user=self.request.user)


class PomodoroCompleteView(APIView):
    """
    PATCH /api/v1/tasks/pomodoro/<id>/complete/
    Marquer une session Pomodoro comme terminée.
    """
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        session = get_object_or_404(PomodoroSession, pk=pk, user=request.user)
        session.completed = True
        session.ended_at = timezone.now()
        session.save()
        return Response(PomodoroSessionSerializer(session).data)


# ─────────────────────────────────────────────
# CALENDRIER
# ─────────────────────────────────────────────

class CalendarEventListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/v1/tasks/calendar/
    POST /api/v1/tasks/calendar/
    """
    serializer_class = CalendarEventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = CalendarEvent.objects.filter(user=self.request.user)
        # Filtrer par mois: ?year=2026&month=4
        year = self.request.query_params.get('year')
        month = self.request.query_params.get('month')
        if year and month:
            qs = qs.filter(start_datetime__year=year, start_datetime__month=month)
        return qs


class CalendarEventDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET/PUT/DELETE /api/v1/tasks/calendar/<id>/
    """
    serializer_class = CalendarEventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CalendarEvent.objects.filter(user=self.request.user)
