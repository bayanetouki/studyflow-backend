"""
Tests unitaires - Collaboration
PFA Génie Logiciel - StudyFlow
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from apps.collaboration.models import Team, TeamMembership, SharedTask

User = get_user_model()


def make_user(email, db_fixture=None):
    return User.objects.create_user(
        username=email, email=email, password='Pass123!', name=email.split('@')[0]
    )


@pytest.fixture
def user(db):
    return make_user('owner@test.ma')


@pytest.fixture
def member_user(db):
    return make_user('member@test.ma')


@pytest.fixture
def auth_client(db, user):
    client = APIClient()
    response = client.post(reverse('auth-login'), {'email': 'owner@test.ma', 'password': 'Pass123!'})
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {response.data["access"]}')
    client.user = user
    return client


@pytest.fixture
def team(db, user):
    t = Team.objects.create(name='Équipe Maths', owner=user)
    TeamMembership.objects.create(team=t, user=user, role='owner')
    return t


@pytest.mark.django_db
class TestTeam:
    def test_create_team(self, auth_client):
        """Un utilisateur peut créer une équipe."""
        url = reverse('team-list')
        response = auth_client.post(url, {'name': 'Groupe Physique', 'description': 'Révisions'})
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'Groupe Physique'
        # Le créateur doit être dans les membres
        team = Team.objects.get(name='Groupe Physique')
        assert TeamMembership.objects.filter(team=team, user=auth_client.user, role='owner').exists()

    def test_list_my_teams(self, auth_client, team):
        """Lister les équipes dont je fais partie."""
        url = reverse('team-list')
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1

    def test_join_team_with_code(self, db, team, member_user):
        """Un utilisateur peut rejoindre une équipe avec le code."""
        client = APIClient()
        response = client.post(reverse('auth-login'), {'email': 'member@test.ma', 'password': 'Pass123!'})
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {response.data["access"]}')

        url = reverse('team-join')
        response = client.post(url, {'invitation_code': team.invitation_code})
        assert response.status_code == status.HTTP_200_OK
        assert TeamMembership.objects.filter(team=team, user=member_user).exists()

    def test_join_team_wrong_code(self, auth_client):
        """Rejoindre avec un mauvais code retourne 404."""
        url = reverse('team-join')
        response = auth_client.post(url, {'invitation_code': 'XXXXXXXX'})
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_join_team_already_member(self, auth_client, team):
        """Rejoindre une équipe dont on est déjà membre retourne 400."""
        url = reverse('team-join')
        response = auth_client.post(url, {'invitation_code': team.invitation_code})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_auto_generates_invitation_code(self, db, user):
        """Un code d'invitation est automatiquement généré à la création."""
        team = Team.objects.create(name='Auto Code', owner=user)
        assert team.invitation_code != ''
        assert len(team.invitation_code) > 0


@pytest.mark.django_db
class TestSharedTask:
    def test_create_shared_task(self, auth_client, team):
        """Créer une tâche partagée dans une équipe."""
        url = reverse('shared-task-list')
        data = {
            'team': team.pk,
            'title': 'Présentation finale',
            'priority': 'high',
            'due_date': '2026-05-01',
        }
        response = auth_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == 'Présentation finale'

    def test_update_shared_task_progress(self, auth_client, team, db):
        """Mettre à jour la progression d'une tâche partagée."""
        task = SharedTask.objects.create(
            team=team,
            created_by=auth_client.user,
            title='Rapport',
            priority='medium'
        )
        url = reverse('shared-task-progress', kwargs={'pk': task.pk})
        response = auth_client.patch(url, {'progress': 75})
        assert response.status_code == status.HTTP_200_OK
        assert response.data['progress'] == 75

    def test_progress_100_marks_completed(self, auth_client, team, db):
        """Mettre à 100% complète automatiquement la tâche."""
        task = SharedTask.objects.create(
            team=team,
            created_by=auth_client.user,
            title='Terminée',
            priority='low'
        )
        url = reverse('shared-task-progress', kwargs={'pk': task.pk})
        auth_client.patch(url, {'progress': 100})
        task.refresh_from_db()
        assert task.completed == True

    def test_progress_invalid_value(self, auth_client, team, db):
        """Une valeur de progression invalide retourne 400."""
        task = SharedTask.objects.create(
            team=team,
            created_by=auth_client.user,
            title='Test',
            priority='low'
        )
        url = reverse('shared-task-progress', kwargs={'pk': task.pk})
        response = auth_client.patch(url, {'progress': 150})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
