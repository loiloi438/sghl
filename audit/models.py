from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    """Piste d'audit immuable (User, Timestamp, IP, Old/New Value)."""

    ACTION_CREATE = 'CREATE'
    ACTION_UPDATE = 'UPDATE'
    ACTION_DELETE = 'DELETE'
    ACTION_CHOICES = [
        (ACTION_CREATE, 'Création'),
        (ACTION_UPDATE, 'Modification'),
        (ACTION_DELETE, 'Suppression'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
    )
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=64)
    old_value = models.JSONField(null=True, blank=True)
    new_value = models.JSONField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['model_name', 'object_id']),
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        return f'{self.action} {self.model_name}#{self.object_id}'
