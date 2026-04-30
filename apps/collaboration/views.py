"""
Views pour la collaboration - StudyFlow
"""
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import Team, TeamMembership, SharedTask, Message
from .serializers import (
    TeamSerializer, SharedTaskSerializer, MessageSerializer, JoinTeamSerializer
)


class TeamListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/v1/collaboration/teams/    → Mes équipes
    POST /api/v1/collaboration/teams/    → Créer une équipe
    """
    serializer_class = TeamSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Team.objects.filter(members=self.request.user)


class TeamDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET/PUT/DELETE /api/v1/collaboration/teams/<id>/
    """
    serializer_class = TeamSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Team.objects.filter(members=self.request.user)


class JoinTeamView(APIView):
    """
    POST /api/v1/collaboration/teams/join/
    Rejoindre une équipe avec un code d'invitation.
    Body: { "invitation_code": "ABC12345" }
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = JoinTeamSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data['invitation_code']

        team = get_object_or_404(Team, invitation_code=code.upper())

        # Vérifier si déjà membre
        if TeamMembership.objects.filter(team=team, user=request.user).exists():
            return Response(
                {"error": "Vous êtes déjà membre de cette équipe."},
                status=status.HTTP_400_BAD_REQUEST
            )

        TeamMembership.objects.create(team=team, user=request.user, role='member')
        return Response(TeamSerializer(team, context={'request': request}).data)


class SharedTaskListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/v1/collaboration/tasks/?team=<id>
    POST /api/v1/collaboration/tasks/
    """
    serializer_class = SharedTaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = SharedTask.objects.filter(team__members=self.request.user)
        team_id = self.request.query_params.get('team')
        if team_id:
            qs = qs.filter(team_id=team_id)
        return qs


class SharedTaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET/PUT/DELETE /api/v1/collaboration/tasks/<id>/
    """
    serializer_class = SharedTaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SharedTask.objects.filter(team__members=self.request.user)


class SharedTaskProgressView(APIView):
    """
    PATCH /api/v1/collaboration/tasks/<id>/progress/
    Mettre à jour la progression d'une tâche partagée.
    Body: { "progress": 75 }
    """
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        task = get_object_or_404(SharedTask, pk=pk, team__members=request.user)
        progress = request.data.get('progress', 0)
        if not (0 <= int(progress) <= 100):
            return Response({"error": "La progression doit être entre 0 et 100."}, status=400)
        task.progress = progress
        if int(progress) == 100:
            task.completed = True
        task.save()
        return Response(SharedTaskSerializer(task).data)


class MessageListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/v1/collaboration/messages/?team=<id>
    POST /api/v1/collaboration/messages/
    """
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Message.objects.filter(team__members=self.request.user)
        team_id = self.request.query_params.get('team')
        if team_id:
            qs = qs.filter(team_id=team_id)
        return qs
