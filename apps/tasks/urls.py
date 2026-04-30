from django.urls import path
from .views import (
    TaskListCreateView, TaskDetailView, TaskToggleView, TaskStatsView,
    PomodoroListCreateView, PomodoroCompleteView,
    CalendarEventListCreateView, CalendarEventDetailView,
)

urlpatterns = [
    # Tâches
    path('', TaskListCreateView.as_view(), name='task-list'),
    path('<int:pk>/', TaskDetailView.as_view(), name='task-detail'),
    path('<int:pk>/toggle/', TaskToggleView.as_view(), name='task-toggle'),
    path('stats/', TaskStatsView.as_view(), name='task-stats'),

    # Pomodoro
    path('pomodoro/', PomodoroListCreateView.as_view(), name='pomodoro-list'),
    path('pomodoro/<int:pk>/complete/', PomodoroCompleteView.as_view(), name='pomodoro-complete'),

    # Calendrier
    path('calendar/', CalendarEventListCreateView.as_view(), name='calendar-list'),
    path('calendar/<int:pk>/', CalendarEventDetailView.as_view(), name='calendar-detail'),
]
