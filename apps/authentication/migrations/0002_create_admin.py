# Fichier : apps/authentication/migrations/0002_create_admin.py
from django.db import migrations
from django.contrib.auth.hashers import make_password
import os

def create_admin(apps, schema_editor):
    User = apps.get_model('authentication', 'User')
    
    email = os.environ.get('ADMIN_EMAIL', 'admin@studyflow.com')
    password = os.environ.get('ADMIN_PASSWORD', 'Admin123!')
    username = os.environ.get('ADMIN_USERNAME', 'admin')
    
    if not User.objects.filter(email=email).exists():
        User.objects.create(
            username=username,
            email=email,
            password=make_password(password),
            is_staff=True,
            is_superuser=True,
            is_active=True,
        )

def reverse_func(apps, schema_editor):
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('authentication', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(create_admin, reverse_func),
    ]
