"""
Modèles pour la collaboration - StudyFlow
Correspond à Collaboration.tsx du frontend
"""
from django.db import models
from django.conf import settings


class Team(models.Model):
    """Groupe de travail/étude."""
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_teams'
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='TeamMembership',
        related_name='teams'
    )
    invitation_code = models.CharField(max_length=20, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Équipe'
        verbose_name_plural = 'Équipes'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.invitation_code:
            import uuid
            self.invitation_code = str(uuid.uuid4())[:8].upper()
        super().save(*args, **kwargs)


class TeamMembership(models.Model):
    """Appartenance à une équipe avec rôle."""
    ROLE_CHOICES = [
        ('owner', 'Propriétaire'),
        ('member', 'Membre'),
    ]
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['team', 'user']

    def __str__(self):
        return f"{self.user.email} → {self.team.name} ({self.role})"


class SharedTask(models.Model):
    """
    Tâche partagée entre membres d'une équipe.
    Correspond à SharedTask interface dans Collaboration.tsx.
    """
    PRIORITY_CHOICES = [
        ('high', 'Haute'),
        ('medium', 'Moyenne'),
        ('low', 'Faible'),
    ]
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='shared_tasks')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_shared_tasks'
    )
    assigned_to = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='assigned_tasks',
        blank=True
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    progress = models.PositiveIntegerField(default=0, help_text="Pourcentage 0-100")
    due_date = models.DateField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Tâche Partagée'
        verbose_name_plural = 'Tâches Partagées'

    def __str__(self):
        return f"{self.team.name} - {self.title}"


class Message(models.Model):
    """Message dans le chat d'équipe."""
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'

    def __str__(self):
        return f"{self.sender.email}: {self.content[:50]}"
