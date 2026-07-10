import uuid

from django.conf import settings
from django.db import models


class PlateformeAppareil(models.TextChoices):
    ANDROID = 'android', 'Android'
    IOS = 'ios', 'iOS'
    WEB = 'web', 'Web'
    INCONNU = 'inconnu', 'Inconnu'


class DeviceToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='appareils_push',
    )
    token = models.CharField(max_length=512, unique=True)
    plateforme = models.CharField(
        max_length=20,
        choices=PlateformeAppareil.choices,
        default=PlateformeAppareil.INCONNU,
    )
    actif = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'jeton appareil'
        verbose_name_plural = 'jetons appareils'

    def __str__(self):
        return f'{self.utilisateur_id} — {self.plateforme}'


class NotificationInbox(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications_inbox',
    )
    titre = models.CharField(max_length=200)
    corps = models.TextField()
    categorie = models.CharField(max_length=50, blank=True)
    donnees = models.JSONField(default=dict, blank=True)
    lu = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['utilisateur', 'lu'])]
        verbose_name = 'notification'
        verbose_name_plural = 'notifications'

    def __str__(self):
        return f'{self.titre} — {self.utilisateur_id}'
