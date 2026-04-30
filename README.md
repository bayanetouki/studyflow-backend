# 📚 StudyFlow Backend — Guide Complet PFA

> Backend Django REST API pour l'application StudyFlow  
> **PFA — Module Génie Logiciel** | CI/CD · GitHub Actions · Tests Unitaires · Déploiement

---

## 🏗️ Architecture du Projet

```
studyflow_backend/
├── studyflow/               # Configuration Django principale
│   ├── settings.py          # Paramètres (JWT, CORS, DB...)
│   ├── urls.py              # URLs racine
│   └── wsgi.py
├── apps/
│   ├── authentication/      # Inscription, Login, Profil (JWT)
│   │   ├── models.py        # Modèle User personnalisé
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   ├── tasks/               # Tâches, Pomodoro, Calendrier
│   │   ├── models.py        # Task, PomodoroSession, CalendarEvent
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   ├── collaboration/       # Équipes, Tâches partagées, Messages
│   │   ├── models.py        # Team, SharedTask, Message
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   └── progress/            # Statistiques et suivi
│       ├── models.py        # DailyProgress
│       ├── serializers.py
│       ├── views.py
│       └── urls.py
├── tests/
│   ├── test_authentication.py   # 12+ tests
│   ├── test_tasks.py            # 12+ tests
│   └── test_collaboration.py   # 10+ tests
├── .github/
│   └── workflows/
│       └── ci-cd.yml        # Pipeline CI/CD GitHub Actions
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pytest.ini
└── manage.py
```

---

## 📋 Endpoints API

### 🔐 Authentification `/api/v1/auth/`

| Méthode   | URL                 | Description                   |
| --------- | ------------------- | ----------------------------- |
| POST      | `/register/`        | Créer un compte               |
| POST      | `/login/`           | Connexion → tokens JWT        |
| POST      | `/logout/`          | Déconnexion (blacklist token) |
| POST      | `/token/refresh/`   | Renouveler le token           |
| GET/PATCH | `/profile/`         | Voir/modifier son profil      |
| POST      | `/change-password/` | Changer le mot de passe       |

### ✅ Tâches `/api/v1/tasks/`

| Méthode        | URL                        | Description                                                 |
| -------------- | -------------------------- | ----------------------------------------------------------- |
| GET            | `/`                        | Lister mes tâches (filtres: priority, completed, view_mode) |
| POST           | `/`                        | Créer une tâche                                             |
| GET/PUT/DELETE | `/<id>/`                   | Détail / modifier / supprimer                               |
| PATCH          | `/<id>/toggle/`            | Cocher / décocher                                           |
| GET            | `/stats/`                  | Statistiques de productivité                                |
| GET/POST       | `/pomodoro/`               | Sessions Pomodoro                                           |
| PATCH          | `/pomodoro/<id>/complete/` | Terminer une session                                        |
| GET/POST       | `/calendar/`               | Événements calendrier                                       |
| GET/PUT/DELETE | `/calendar/<id>/`          | Détail événement                                            |

### 👥 Collaboration `/api/v1/collaboration/`

| Méthode        | URL                     | Description                  |
| -------------- | ----------------------- | ---------------------------- |
| GET/POST       | `/teams/`               | Mes équipes / Créer          |
| GET/PUT/DELETE | `/teams/<id>/`          | Détail équipe                |
| POST           | `/teams/join/`          | Rejoindre avec un code       |
| GET/POST       | `/tasks/`               | Tâches partagées             |
| GET/PUT/DELETE | `/tasks/<id>/`          | Détail tâche partagée        |
| PATCH          | `/tasks/<id>/progress/` | Mettre à jour la progression |
| GET/POST       | `/messages/`            | Messages d'équipe            |

### 📊 Progression `/api/v1/progress/`

| Méthode | URL         | Description                            |
| ------- | ----------- | -------------------------------------- |
| GET     | `/summary/` | Résumé global (dashboard Progress.tsx) |
| GET     | `/daily/`   | Historique 30 jours                    |

📖 **Documentation Swagger** : `http://localhost:8000/api/docs/`

---

## 🚀 ÉTAPE 1 — Installation Locale

### 1.1 Prérequis

```bash
python --version   # Python 3.11+ requis
git --version
```

### 1.2 Cloner et configurer

```bash
# Cloner le repository
git clone https://github.com/TON_USERNAME/studyflow-backend.git
cd studyflow-backend

# Créer et activer le virtualenv
python -m venv venv
source venv/bin/activate          # Linux/Mac
# venv\Scripts\activate           # Windows

# Installer les dépendances
pip install -r requirements.txt
```

### 1.3 Variables d'environnement

```bash
# Copier le template
cp .env.example .env

# Éditer .env avec tes valeurs
# (laisser les valeurs par défaut pour le développement)
```

### 1.4 Base de données et démarrage

```bash
# Appliquer les migrations
python manage.py migrate

# Créer un superutilisateur (pour l'admin)
python manage.py createsuperuser

# Lancer le serveur de développement
python manage.py runserver
```

✅ **Backend disponible sur** : `http://localhost:8000`  
📖 **Swagger** : `http://localhost:8000/api/docs/`  
🔧 **Admin** : `http://localhost:8000/admin/`

---

## 🧪 ÉTAPE 2 — Tests Unitaires

```bash
# Lancer tous les tests
pytest tests/ -v

# Avec rapport de couverture
coverage run -m pytest tests/ -v
coverage report

# Rapport HTML (ouvrir htmlcov/index.html)
coverage html

# Lancer un seul fichier de tests
pytest tests/test_authentication.py -v

# Lancer un test spécifique
pytest tests/test_tasks.py::TestTaskCRUD::test_create_task -v
```

### Résultat attendu

```
tests/test_authentication.py::TestRegister::test_register_success PASSED
tests/test_authentication.py::TestLogin::test_login_success PASSED
tests/test_tasks.py::TestTaskCRUD::test_create_task PASSED
tests/test_tasks.py::TestTaskToggleAndFilters::test_toggle_task_complete PASSED
tests/test_collaboration.py::TestTeam::test_create_team PASSED
...
34 passed in 3.2s
```

---

## 🐳 ÉTAPE 3 — Docker

### 3.1 Build et lancement avec Docker Compose

```bash
# Build + démarrage (PostgreSQL + Django)
docker-compose up --build

# En arrière-plan
docker-compose up -d --build

# Voir les logs
docker-compose logs -f backend

# Arrêter
docker-compose down
```

### 3.2 Build de l'image seule

```bash
docker build -t studyflow-backend .
docker run -p 8000:8000 studyflow-backend
```

---

## ⚙️ ÉTAPE 4 — Configuration GitHub Actions (CI/CD)

### 4.1 Créer le repository GitHub

```bash
git init
git add .
git commit -m "feat: initial backend StudyFlow"
git branch -M main
git remote add origin https://github.com/TON_USERNAME/studyflow-backend.git
git push -u origin main
```

### 4.2 Configurer les Secrets GitHub

Aller dans **Settings → Secrets and variables → Actions** et ajouter :

| Secret            | Valeur                                    |
| ----------------- | ----------------------------------------- |
| `DOCKER_USERNAME` | Ton username Docker Hub                   |
| `DOCKER_PASSWORD` | Ton mot de passe / token Docker Hub       |
| `RAILWAY_TOKEN`   | Token Railway (obtenu depuis railway.app) |

### 4.3 Pipeline CI/CD (automatique)

Le fichier `.github/workflows/ci-cd.yml` déclenche automatiquement :

```
Push sur main/develop
        │
        ▼
┌───────────────┐    ┌───────────────┐
│  JOB 1        │    │  JOB 2        │
│  🧪 Tests     │    │  🔍 Lint      │
│  + Coverage   │    │  (flake8)     │
└───────┬───────┘    └───────┬───────┘
        └─────────┬──────────┘
                  ▼
        ┌─────────────────┐
        │   JOB 3         │
        │  🐳 Docker Build│
        │  + Push Hub     │
        └────────┬────────┘
                 │ (seulement sur main)
                 ▼
        ┌─────────────────┐
        │   JOB 4         │
        │  🚀 Deploy      │
        │  Railway/VPS    │
        └─────────────────┘
```

---

## 🌐 ÉTAPE 5 — Déploiement (Web Service)

### Option A : Railway (Recommandé - Gratuit)

1. Créer un compte sur [railway.app](https://railway.app)
2. Créer un nouveau projet → **Deploy from GitHub repo**
3. Sélectionner ton repository
4. Ajouter un service **PostgreSQL**
5. Configurer les variables d'environnement :
   ```
   SECRET_KEY=une-vraie-cle-secrete-longue-et-complexe
   DEBUG=False
   DATABASE_URL=(Railway le remplit automatiquement)
   ALLOWED_HOSTS=*.railway.app,ton-domaine.com
   CORS_ALLOWED_ORIGINS=https://ton-frontend.vercel.app
   ```
6. Railway génère automatiquement l'URL de déploiement

### Option B : Render (Gratuit)

1. Créer un compte sur [render.com](https://render.com)
2. New → **Web Service** → connecter GitHub
3. Configurer :
   - **Build Command** : `pip install -r requirements.txt && python manage.py migrate`
   - **Start Command** : `gunicorn studyflow.wsgi:application --bind 0.0.0.0:$PORT`
4. Ajouter les variables d'environnement (mêmes que Railway)
5. Créer une base PostgreSQL sur Render et copier l'URL

### Option C : VPS (Herbergement propre)

```bash
# Sur le serveur (Ubuntu)
git clone https://github.com/TON_USERNAME/studyflow-backend.git
cd studyflow-backend
cp .env.example .env
# Éditer .env avec les vraies valeurs
docker-compose up -d --build
```

---

## 🔗 ÉTAPE 6 — Connexion Frontend ↔ Backend

Dans ton projet React (StudyFlow frontend), créer un fichier `src/api/client.ts` :

```typescript
// src/api/client.ts
const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

export const apiClient = {
  async register(email: string, name: string, password: string) {
    const res = await fetch(`${API_BASE}/auth/register/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, name, password, password2: password }),
    });
    return res.json();
  },

  async login(email: string, password: string) {
    const res = await fetch(`${API_BASE}/auth/login/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    const data = await res.json();
    if (data.access) {
      localStorage.setItem("access_token", data.access);
      localStorage.setItem("refresh_token", data.refresh);
      localStorage.setItem("userName", data.user.name || data.user.email);
    }
    return data;
  },

  async getTasks(filters = "") {
    const token = localStorage.getItem("access_token");
    const res = await fetch(`${API_BASE}/tasks/${filters}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return res.json();
  },

  async createTask(task: object) {
    const token = localStorage.getItem("access_token");
    const res = await fetch(`${API_BASE}/tasks/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(task),
    });
    return res.json();
  },

  async toggleTask(id: string) {
    const token = localStorage.getItem("access_token");
    const res = await fetch(`${API_BASE}/tasks/${id}/toggle/`, {
      method: "PATCH",
      headers: { Authorization: `Bearer ${token}` },
    });
    return res.json();
  },
};
```

Modifier `Login.tsx` pour utiliser la vraie API :

```typescript
const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();
  if (isSignUp) {
    const data = await apiClient.register(email, name, password);
    if (data.access) navigate("/dashboard");
  } else {
    const data = await apiClient.login(email, password);
    if (data.access) navigate("/dashboard");
  }
};
```

---

## 📊 Résumé des Technologies

| Composant          | Technologie                      |
| ------------------ | -------------------------------- |
| Framework          | Django 5.0 + DRF                 |
| Auth               | JWT (SimpleJWT)                  |
| Base de données    | SQLite (dev) / PostgreSQL (prod) |
| Tests              | pytest + pytest-django           |
| CI/CD              | GitHub Actions                   |
| Containerisation   | Docker + Docker Compose          |
| Déploiement        | Railway / Render / VPS           |
| Documentation API  | drf-spectacular (Swagger)        |
| Serveur WSGI       | Gunicorn                         |
| Fichiers statiques | WhiteNoise                       |
