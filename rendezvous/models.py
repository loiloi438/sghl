import uuid

from django.conf import settings
from django.db import models

from core.models import OptimisticLockModel, TimeStampedModel
from patients.models import Patient


class StatutRendezVous(models.TextChoices):
    EN_ATTENTE = 'en_attente', 'En attente de validation'
    PLANIFIE = 'planifie', 'Planifié'
    CONFIRME = 'confirme', 'Confirmé'
    ANNULE = 'annule', 'Annulé'
    TERMINE = 'termine', 'Terminé'
    ABSENT = 'absent', 'Absent'


class TypeConsultation(models.TextChoices):
    PRESENTIEL = 'presentiel', 'Présentiel'
    TELECONSULTATION = 'teleconsultation', 'Téléconsultation'


class RendezVous(TimeStampedModel, OptimisticLockModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(
        Patient,
        on_delete=models.PROTECT,
        related_name='rendez_vous',
    )
    medecin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='rendez_vous_medecin',
    )
    date_heure = models.DateTimeField()
    duree_minutes = models.PositiveSmallIntegerField(default=30)
    motif = models.CharField(max_length=255)
    statut = models.CharField(
        max_length=20,
        choices=StatutRendezVous.choices,
        default=StatutRendezVous.PLANIFIE,
    )
    notes = models.TextField(blank=True)
    cree_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rendez_vous_crees',
    )
    confirme_le = models.DateTimeField(null=True, blank=True)
    annule_le = models.DateTimeField(null=True, blank=True)
    annule_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rendez_vous_annules',
    )
    motif_annulation = models.CharField(max_length=255, blank=True)
    type_consultation = models.CharField(
        max_length=20,
        choices=TypeConsultation.choices,
        default=TypeConsultation.PRESENTIEL,
    )
    lien_visio = models.URLField(blank=True, default='')
    rappel_j1_envoye_le = models.DateTimeField(
        'Rappel J-1 envoyé le',
        null=True,
        blank=True,
        help_text='Horodatage du dernier e-mail de rappel la veille du RDV.',
    )

    class Meta:
        ordering = ['date_heure']
        indexes = [
            models.Index(fields=['date_heure']),
            models.Index(fields=['statut']),
            models.Index(fields=['medecin', 'date_heure']),
        ]
        verbose_name = 'rendez-vous'
        verbose_name_plural = 'rendez-vous'

    def __str__(self):
        return f'RDV {self.patient} — {self.date_heure:%d/%m/%Y %H:%M}'

    @property
    def est_modifiable(self) -> bool:
        return self.statut in {
            StatutRendezVous.EN_ATTENTE,
            StatutRendezVous.PLANIFIE,
            StatutRendezVous.CONFIRME,
        }
