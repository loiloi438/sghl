import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone

from core.models import OptimisticLockModel, TimeStampedModel
from patients.models import Patient


class NiveauTriage(models.TextChoices):
    ROUGE = 'red', 'Urgence majeure'
    ORANGE = 'orange', 'Urgent'
    VERT = 'green', 'Peu urgent'
    BLEU = 'blue', 'Non urgent'


class StatutPassageUrgence(models.TextChoices):
    ATTENTE = 'attente', 'En attente'
    TRIAGE = 'triage', 'Triage en cours'
    SOINS = 'soins', 'En salle de soins'
    SORTI = 'sorti', 'Sorti'
    ADMIS = 'admis', 'Admis en hospitalisation'


class PassageUrgence(TimeStampedModel, OptimisticLockModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(
        Patient,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='passages_urgence',
    )
    nom_libre = models.CharField(max_length=150, blank=True, default='')
    age = models.PositiveSmallIntegerField(null=True, blank=True)
    sexe = models.CharField(max_length=1, blank=True, default='')
    motif = models.TextField()
    niveau_triage = models.CharField(
        max_length=10,
        choices=NiveauTriage.choices,
        default=NiveauTriage.ORANGE,
    )
    statut = models.CharField(
        max_length=20,
        choices=StatutPassageUrgence.choices,
        default=StatutPassageUrgence.ATTENTE,
    )
    heure_arrivee = models.DateTimeField(default=timezone.now)
    heure_triage = models.DateTimeField(null=True, blank=True)
    medecin_triage = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='triages_urgence',
    )
    notes = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['heure_arrivee']
        verbose_name = 'passage urgence'
        verbose_name_plural = 'passages urgence'

    def __str__(self):
        label = str(self.patient) if self.patient else self.nom_libre
        return f'Urgence {label} ({self.get_niveau_triage_display()})'

    @property
    def display_name(self) -> str:
        if self.patient:
            return f'{self.patient.prenom} {self.patient.nom}'
        return self.nom_libre or 'Arrivant inconnu'
