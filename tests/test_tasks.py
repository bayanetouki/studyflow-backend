"""
Tests unitaires - Tâches
PFA Génie Logiciel - StudyFlow
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from apps.tasks.models import Task

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username='user@test.ma',
        email='user@test.ma',
        password='Pass123!',
        name='Test User'
    )


@pytest.fixture
def other_user(db):
    return User.objects.create_user(
        username='other@test.ma',
        email='other@test.ma',
        password='Pass123!',
        name='Other User'
    )


@pytest.fixture
def auth_client(api_client, user):
    response = api_client.post(reverse('auth-login'), {
        'email': 'user@test.ma',
        'password': 'Pass123!',
    })
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {response.data["access"]}')
    api_client.user = user
    return api_client


@pytest.fixture
def sample_task(db, user):
    return Task.objects.create(
        user=user,
        title='Réviser les maths',
        description='Chapitres 5 et 6',
        priority='high',
        estimated_time=60,
    )


# ─────────────────────────────────────────────
# CRUD TÂCHES
# ─────────────────────────────────────────────

@pytest.mark.django_db
class TestTaskCRUD:
    def test_create_task(self, auth_client):
        """Un utilisateur peut créer une tâche."""
        url = reverse('task-list')
        data = {
            'title': 'Nouvelle tâche',
            'description': 'Description',
            'priority': 'medium',
            'estimated_time': 45,
        }
        response = auth_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == 'Nouvelle tâche'
        assert Task.objects.filter(user=auth_client.user, title='Nouvelle tâche').exists()

    def test_list_tasks(self, auth_client, sample_task):
        """Un utilisateur voit uniquement ses tâches."""
        url = reverse('task-list')
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1

    def test_list_tasks_isolates_users(self, auth_client, other_user, db):
        """Les tâches d'un autre utilisateur ne sont pas visibles."""
        Task.objects.create(
            user=other_user,
            title='Tâche privée de l\'autre',
            priority='low'
        )
        url = reverse('task-list')
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 0

    def test_get_task_detail(self, auth_client, sample_task):
        """Un utilisateur peut voir le détail de sa tâche."""
        url = reverse('task-detail', kwargs={'pk': sample_task.pk})
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'Réviser les maths'

    def test_update_task(self, auth_client, sample_task):
        """Un utilisateur peut modifier sa tâche."""
        url = reverse('task-detail', kwargs={'pk': sample_task.pk})
        response = auth_client.patch(url, {'title': 'Titre modifié'})
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'Titre modifié'

    def test_delete_task(self, auth_client, sample_task):
        """Un utilisateur peut supprimer sa tâche."""
        url = reverse('task-detail', kwargs={'pk': sample_task.pk})
        response = auth_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Task.objects.filter(pk=sample_task.pk).exists()

    def test_cannot_access_other_user_task(self, auth_client, other_user, db):
        """Un utilisateur ne peut pas accéder à la tâche d'un autre."""
        other_task = Task.objects.create(
            user=other_user,
            title='Confidentiel',
            priority='high'
        )
        url = reverse('task-detail', kwargs={'pk': other_task.pk})
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


# ─────────────────────────────────────────────
# TOGGLE & FILTRES
# ─────────────────────────────────────────────

@pytest.mark.django_db
class TestTaskToggleAndFilters:
    def test_toggle_task_complete(self, auth_client, sample_task):
        """Basculer l'état d'une tâche (compléter)."""
        assert sample_task.completed == False
        url = reverse('task-toggle', kwargs={'pk': sample_task.pk})
        response = auth_client.patch(url)
        assert response.status_code == status.HTTP_200_OK
        sample_task.refresh_from_db()
        assert sample_task.completed == True

    def test_toggle_task_twice(self, auth_client, sample_task):
        """Basculer deux fois remet à False."""
        url = reverse('task-toggle', kwargs={'pk': sample_task.pk})
        auth_client.patch(url)
        auth_client.patch(url)
        sample_task.refresh_from_db()
        assert sample_task.completed == False

    def test_filter_by_priority(self, auth_client, user, db):
        """Filtrer les tâches par priorité."""
        Task.objects.create(user=user, title='High task', priority='high')
        Task.objects.create(user=user, title='Low task', priority='low')
        url = reverse('task-list') + '?priority=high'
        response = auth_client.get(url)
        assert response.data['count'] == 1
        assert response.data['results'][0]['priority'] == 'high'

    def test_filter_completed(self, auth_client, user, db):
        """Filtrer les tâches complétées."""
        Task.objects.create(user=user, title='Faite', priority='medium', completed=True)
        Task.objects.create(user=user, title='En cours', priority='medium', completed=False)
        url = reverse('task-list') + '?completed=true'
        response = auth_client.get(url)
        assert response.data['count'] == 1

    def test_task_stats(self, auth_client, user, db):
        """Les statistiques retournent les bons totaux."""
        Task.objects.create(user=user, title='T1', priority='high', completed=True, estimated_time=30)
        Task.objects.create(user=user, title='T2', priority='low', completed=False)
        url = reverse('task-stats')
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['total'] == 2
        assert response.data['completed'] == 1
        assert response.data['completion_rate'] == 50.0

    def test_unauthenticated_cannot_access_tasks(self, api_client):
        """Sans authentification, les tâches sont inaccessibles."""
        url = reverse('task-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
