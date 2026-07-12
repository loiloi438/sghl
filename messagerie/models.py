import uuid

from django.conf import settings
from django.db import models

from core.models import TimeStampedModel


class MessageInterne(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    expediteur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='messages_envoyes',
    )
    destinataire = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='messages_recus',
    )
    sujet = models.CharField(max_length=200)
    corps = models.TextField()
    lu = models.BooleanField(default=False)
    lu_le = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['destinataire', 'lu']),
            models.Index(fields=['expediteur']),
        ]
        verbose_name = 'message interne'
        verbose_name_plural = 'messages internes'

    def __str__(self):
        return f'{self.sujet} ({self.expediteur_id} → {self.destinataire_id})'
