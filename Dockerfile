# ─────────────────────────────────────────────
# Dockerfile - StudyFlow Backend
# ─────────────────────────────────────────────
FROM python:3.12-slim

# Variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Répertoire de travail
WORKDIR /app

# Dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Dépendances Python
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copier le code source
COPY . .

# Collecter les fichiers statiques
RUN python manage.py collectstatic --noinput

# Port exposé
EXPOSE 8000

# Commande de démarrage (production avec Gunicorn)
CMD ["gunicorn", "studyflow.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
