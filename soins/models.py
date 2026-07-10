import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone

from core.models import OptimisticLockModel, TimeStampedModel
from hospitalisation.models import Hospitalisation


class StatutPlanSoins(models.TextChoices):
    ACTIF = 'actif', 'Actif'
    TERMINE = 'termine', 'Terminé'
    ANNULE = 'annule', 'Annulé'


class PlanSoins(TimeStampedModel, OptimisticLockModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hospitalisation = models.ForeignKey(
        Hospitalisation,
        on_delete=models.PROTECT,
        related_name='plans_soins',
    )
    titre = models.CharField(max_length=200)
    description = models.TextField()
    date_debut = models.DateTimeField(default=timezone.now)
    date_fin = models.DateTimeField(null=True, blank=True)
    statut = models.CharField(
        max_length=20,
        choices=StatutPlanSoins.choices,
        default=StatutPlanSoins.ACTIF,
    )
    cree_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='plans_soins_crees',
    )

    class Meta:
        ordering = ['-date_debut']
        verbose_name = 'plan de soins'
        verbose_name_plural = 'plans de soins'

    def __str__(self):
        return f'{self.titre} ({self.get_statut_display()})'


class ConstanteVitale(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hospitalisation = models.ForeignKey(
        Hospitalisation,
        on_delete=models.PROTECT,
        related_name='constantes_vitales',
    )
    temperature = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    tension_systolique = models.PositiveSmallIntegerField(null=True, blank=True)
    tension_diastolique = models.PositiveSmallIntegerField(null=True, blank=True)
    frequence_cardiaque = models.PositiveSmallIntegerField(null=True, blank=True)
    frequence_respiratoire = models.PositiveSmallIntegerField(null=True, blank=True)
    saturation_o2 = models.PositiveSmallIntegerField(null=True, blank=True)
    glycemie = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    mesure_le = models.DateTimeField(default=timezone.now)
    infirmier = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='constantes_saisies',
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-mesure_le']
        indexes = [models.Index(fields=['mesure_le'])]
        verbose_name = 'constante vitale'
        verbose_name_plural = 'constantes vitales'

    def __str__(self):
        return f'Constantes {self.mesure_le:%d/%m/%Y %H:%M}'


class InterventionInfirmiere(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hospitalisation = models.ForeignKey(
        Hospitalisation,
        on_delete=models.PROTECT,
        related_name='interventions_infirmieres',
    )
    plan_soins = models.ForeignKey(
        PlanSoins,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='interventions',
    )
    type_intervention = models.CharField(max_length=100)
    description = models.TextField()
    realisee_le = models.DateTimeField(default=timezone.now)
    infirmier = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='interventions_realisees',
    )

    class Meta:
        ordering = ['-realisee_le']
        indexes = [models.Index(fields=['realisee_le'])]
        verbose_name = 'intervention infirmière'
        verbose_name_plural = 'interventions infirmières'

    def __str__(self):
        return f'{self.type_intervention} — {self.realisee_le:%d/%m/%Y %H:%M}'


class StatutDose(models.TextChoices):
    PLANIFIEE = 'planifiee', 'Planifiée'
    ADMINISTREE = 'administree', 'Administrée'
    OMISE = 'omise', 'Omise'


class DosePlanifiee(TimeStampedModel, OptimisticLockModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plan_soins = models.ForeignKey(
        PlanSoins,
        on_delete=models.PROTECT,
        related_name='doses',
    )
    medicament = models.CharField(max_length=200)
    posologie = models.CharField(max_length=100)
    heure_prevue = models.DateTimeField()
    statut = models.CharField(
        max_length=20,
        choices=StatutDose.choices,
        default=StatutDose.PLANIFIEE,
    )
    administree_le = models.DateTimeField(null=True, blank=True)
    infirmier = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='doses_administrees',
    )

    class Meta:
        ordering = ['heure_prevue']
        indexes = [
            models.Index(fields=['heure_prevue']),
            models.Index(fields=['statut']),
        ]
        verbose_name = 'dose planifiée'
        verbose_name_plural = 'doses planifiées'

    @property
    def est_en_retard(self) -> bool:
        return (
            self.statut == StatutDose.PLANIFIEE
            and self.heure_prevue < timezone.now()
        )

    def __str__(self):
        return f'{self.medicament} — {self.heure_prevue:%d/%m/%Y %H:%M}'
