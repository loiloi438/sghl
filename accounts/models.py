import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.TextChoices):
    ADMIN = 'admin', 'Administrateur'
    MEDECIN = 'medecin', 'Médecin'
    INFIRMIER = 'infirmier', 'Infirmier(ère)'
    BIOLOGISTE = 'biologiste', 'Biologiste'
    PHARMACIEN = 'pharmacien', 'Pharmacien'
    COMPTABLE = 'comptable', 'Comptable'
    PATIENT = 'patient', 'Patient'


class User(AbstractUser):
    email = models.EmailField('email address', unique=True, blank=True, null=True)
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.INFIRMIER,
    )
    mfa_enabled = models.BooleanField(default=False)
    mfa_secret = models.CharField(max_length=32, blank=True)

    class Meta:
        verbose_name = 'utilisateur'
        verbose_name_plural = 'utilisateurs'

    def save(self, *args, **kwargs):
        if self.email == '':
            self.email = None
        super().save(*args, **kwargs)

    @property
    def is_staff_medical(self) -> bool:
        return self.role in {
            Role.ADMIN,
            Role.MEDECIN,
            Role.INFIRMIER,
            Role.BIOLOGISTE,
            Role.PHARMACIEN,
        }


class RefreshToken(models.Model):
    """Jetons de rafraîchissement pour rotation JWT."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='refresh_tokens')
    token_hash = models.CharField(max_length=128, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    revoked = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']


class AccountValidation(models.Model):
    """Code temporaire pour validation d'un compte utilisateur (inscription)."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='validations')
    code_hash = models.CharField(max_length=256)
    created_at = models.DateTimeField(auto_now_add=True)
    attempts = models.PositiveSmallIntegerField(default=0)
    used = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
