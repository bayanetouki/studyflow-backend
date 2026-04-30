"""
Tests unitaires - Authentification
PFA Génie Logiciel - StudyFlow
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_user(db):
    def _create(email='test@studyflow.ma', password='StrongPass123!', name='Test User'):
        return User.objects.create_user(
            username=email,
            email=email,
            password=password,
            name=name,
        )
    return _create


@pytest.fixture
def authenticated_client(api_client, create_user):
    user = create_user()
    response = api_client.post(reverse('auth-login'), {
        'email': 'test@studyflow.ma',
        'password': 'StrongPass123!',
    })
    token = response.data['access']
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    api_client.user = user
    return api_client


# ─────────────────────────────────────────────
# INSCRIPTION
# ─────────────────────────────────────────────

@pytest.mark.django_db
class TestRegister:
    def test_register_success(self, api_client):
        """Un utilisateur peut s'inscrire avec des données valides."""
        url = reverse('auth-register')
        data = {
            'email': 'nouveau@studyflow.ma',
            'name': 'Nouveau User',
            'password': 'StrongPass123!',
            'password2': 'StrongPass123!',
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert response.data['user']['email'] == 'nouveau@studyflow.ma'

    def test_register_password_mismatch(self, api_client):
        """L'inscription échoue si les mots de passe ne correspondent pas."""
        url = reverse('auth-register')
        data = {
            'email': 'test@studyflow.ma',
            'name': 'Test',
            'password': 'StrongPass123!',
            'password2': 'AutrePass456!',
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_duplicate_email(self, api_client, create_user):
        """L'inscription échoue si l'email est déjà utilisé."""
        create_user(email='existe@studyflow.ma')
        url = reverse('auth-register')
        data = {
            'email': 'existe@studyflow.ma',
            'name': 'Doublon',
            'password': 'StrongPass123!',
            'password2': 'StrongPass123!',
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_weak_password(self, api_client):
        """L'inscription échoue avec un mot de passe trop simple."""
        url = reverse('auth-register')
        data = {
            'email': 'faible@studyflow.ma',
            'name': 'Test',
            'password': '123',
            'password2': '123',
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ─────────────────────────────────────────────
# CONNEXION
# ─────────────────────────────────────────────

@pytest.mark.django_db
class TestLogin:
    def test_login_success(self, api_client, create_user):
        """Un utilisateur peut se connecter avec des identifiants valides."""
        create_user()
        url = reverse('auth-login')
        response = api_client.post(url, {
            'email': 'test@studyflow.ma',
            'password': 'StrongPass123!',
        })
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert 'user' in response.data

    def test_login_wrong_password(self, api_client, create_user):
        """La connexion échoue avec un mauvais mot de passe."""
        create_user()
        url = reverse('auth-login')
        response = api_client.post(url, {
            'email': 'test@studyflow.ma',
            'password': 'MauvaisMotDePasse',
        })
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_unknown_email(self, api_client):
        """La connexion échoue avec un email inconnu."""
        url = reverse('auth-login')
        response = api_client.post(url, {
            'email': 'inconnu@studyflow.ma',
            'password': 'StrongPass123!',
        })
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ─────────────────────────────────────────────
# PROFIL
# ─────────────────────────────────────────────

@pytest.mark.django_db
class TestProfile:
    def test_get_profile(self, authenticated_client):
        """Un utilisateur authentifié peut voir son profil."""
        url = reverse('auth-profile')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == 'test@studyflow.ma'

    def test_update_profile(self, authenticated_client):
        """Un utilisateur peut mettre à jour son profil."""
        url = reverse('auth-profile')
        response = authenticated_client.patch(url, {'name': 'Nouveau Nom', 'bio': 'Ma bio'})
        assert response.status_code == status.HTTP_200_OK

    def test_profile_requires_auth(self, api_client):
        """Le profil est inaccessible sans authentification."""
        url = reverse('auth-profile')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
