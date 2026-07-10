import uuid

from django.conf import settings
from django.db import models
from django.db.models import Q

from core.models import OptimisticLockModel, TimeStampedModel
from logistics.models import Lit
from patients.models import Patient


class StatutHospitalisation(models.TextChoices):
    ACTIVE = 'active', 'Active'
    SORTIE = 'sortie', 'Sortie'
    ANNULEE = 'annulee', 'Annulée'


class Hospitalisation(TimeStampedModel, OptimisticLockModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name='hospitalisations')
    lit = models.ForeignKey(Lit, on_delete=models.PROTECT, related_name='hospitalisations')
    medecin_referent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='hospitalisations_suivies',
    )
    motif_admission = models.TextField()
    date_admission = models.DateTimeField()
    date_sortie_prevue = models.DateField(null=True, blank=True)
    date_sortie_effective = models.DateTimeField(null=True, blank=True)
    statut = models.CharField(
        max_length=20,
        choices=StatutHospitalisation.choices,
        default=StatutHospitalisation.ACTIVE,
    )

    class Meta:
        ordering = ['-date_admission']
        indexes = [
            models.Index(fields=['statut']),
            models.Index(fields=['date_admission']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['patient'],
                condition=Q(statut=StatutHospitalisation.ACTIVE),
                name='unique_hospitalisation_active_par_patient',
            ),
            models.UniqueConstraint(
                fields=['lit'],
                condition=Q(statut=StatutHospitalisation.ACTIVE),
                name='unique_hospitalisation_active_par_lit',
            ),
        ]
        verbose_name = 'hospitalisation'
        verbose_name_plural = 'hospitalisations'

    def __str__(self):
        return f'{self.patient} — {self.get_statut_display()} ({self.date_admission:%d/%m/%Y})'

    @property
    def est_active(self) -> bool:
        return self.statut == StatutHospitalisation.ACTIVE
