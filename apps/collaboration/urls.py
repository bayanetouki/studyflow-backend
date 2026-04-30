from django.urls import path
from .views import (
    TeamListCreateView, TeamDetailView, JoinTeamView,
    SharedTaskListCreateView, SharedTaskDetailView, SharedTaskProgressView,
    MessageListCreateView,
)

urlpatterns = [
    path('teams/', TeamListCreateView.as_view(), name='team-list'),
    path('teams/<int:pk>/', TeamDetailView.as_view(), name='team-detail'),
    path('teams/join/', JoinTeamView.as_view(), name='team-join'),
    path('tasks/', SharedTaskListCreateView.as_view(), name='shared-task-list'),
    path('tasks/<int:pk>/', SharedTaskDetailView.as_view(), name='shared-task-detail'),
    path('tasks/<int:pk>/progress/', SharedTaskProgressView.as_view(), name='shared-task-progress'),
    path('messages/', MessageListCreateView.as_view(), name='message-list'),
]
