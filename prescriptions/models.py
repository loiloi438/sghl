import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone

from core.models import OptimisticLockModel, TimeStampedModel
from hospitalisation.models import Hospitalisation


class StatutPrescription(models.TextChoices):
    BROUILLON = 'brouillon', 'Brouillon'
    VALIDEE = 'validee', 'Validée'
    ANNULEE = 'annulee', 'Annulée'


class DiagnosticCIM10(models.Model):
    code = models.CharField('Code CIM-10', max_length=10, unique=True)
    libelle = models.CharField(max_length=255)
    actif = models.BooleanField(default=True)

    class Meta:
        ordering = ['code']
        verbose_name = 'diagnostic CIM-10'
        verbose_name_plural = 'diagnostics CIM-10'

    def __str__(self):
        return f'{self.code} — {self.libelle}'


class Prescription(TimeStampedModel, OptimisticLockModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hospitalisation = models.ForeignKey(
        Hospitalisation,
        on_delete=models.PROTECT,
        related_name='prescriptions',
    )
    medecin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='prescriptions_redigees',
    )
    statut = models.CharField(
        max_length=20,
        choices=StatutPrescription.choices,
        default=StatutPrescription.BROUILLON,
    )
    observations = models.TextField(blank=True)
    validee_le = models.DateTimeField(null=True, blank=True)
    validee_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='prescriptions_validees',
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['statut']),
            models.Index(fields=['created_at']),
        ]
        verbose_name = 'prescription'
        verbose_name_plural = 'prescriptions'

    def __str__(self):
        return f'Prescription {self.id} ({self.get_statut_display()})'

    @property
    def est_modifiable(self) -> bool:
        return self.statut == StatutPrescription.BROUILLON

    @property
    def est_verrouillee(self) -> bool:
        return self.statut == StatutPrescription.VALIDEE


class PrescriptionDiagnostic(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    prescription = models.ForeignKey(
        Prescription,
        on_delete=models.CASCADE,
        related_name='diagnostics',
    )
    code_cim10 = models.CharField(max_length=10)
    libelle = models.CharField(max_length=255)

    class Meta:
        unique_together = [('prescription', 'code_cim10')]
        verbose_name = 'diagnostic de prescription'
        verbose_name_plural = 'diagnostics de prescription'

    def __str__(self):
        return f'{self.code_cim10} — {self.libelle}'


class LignePrescription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    prescription = models.ForeignKey(
        Prescription,
        on_delete=models.CASCADE,
        related_name='lignes',
    )
    medicament = models.CharField(max_length=200)
    posologie = models.CharField(max_length=150)
    duree_traitement = models.CharField(max_length=100, blank=True)
    voie_administration = models.CharField(max_length=50, default='orale')
    instructions = models.TextField(blank=True)
    ordre = models.PositiveSmallIntegerField(default=1)

    class Meta:
        ordering = ['ordre', 'medicament']
        verbose_name = 'ligne de prescription'
        verbose_name_plural = 'lignes de prescription'

    def __str__(self):
        return f'{self.medicament} — {self.posologie}'
