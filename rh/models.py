import uuid
from datetime import date, timedelta

from django.conf import settings
from django.db import models

from core.models import OptimisticLockModel, TimeStampedModel


class StatutFormation(models.TextChoices):
    PROGRAMMEE = 'programmee', 'Programmée'
    EN_COURS = 'en_cours', 'En cours'
    TERMINEE = 'terminee', 'Terminée'
    ANNULEE = 'annulee', 'Annulée'


class StatutInscription(models.TextChoices):
    INSCRIT = 'inscrit', 'Inscrit'
    PRESENT = 'present', 'Présent'
    VALIDE = 'valide', 'Validé'
    ABSENT = 'absent', 'Absent'


class TypeGarde(models.TextChoices):
    JOUR = 'jour', 'Jour'
    NUIT = 'nuit', 'Nuit'
    WEEK_END = 'week_end', 'Week-end'
    URGENCE = 'urgence', 'Urgence'


class Formation(TimeStampedModel, OptimisticLockModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    titre = models.CharField(max_length=255)
    formateur = models.CharField(max_length=150)
    date_debut = models.DateField()
    date_fin = models.DateField()
    capacite_max = models.PositiveSmallIntegerField(default=20)
    statut = models.CharField(
        max_length=20,
        choices=StatutFormation.choices,
        default=StatutFormation.PROGRAMMEE,
    )
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['-date_debut']
        verbose_name = 'formation'
        verbose_name_plural = 'formations'

    def __str__(self):
        return self.titre

    @property
    def participants_count(self) -> int:
        return self.inscriptions.count()


class InscriptionFormation(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    formation = models.ForeignKey(
        Formation,
        on_delete=models.CASCADE,
        related_name='inscriptions',
    )
    personnel = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='inscriptions_formation',
    )
    statut = models.CharField(
        max_length=20,
        choices=StatutInscription.choices,
        default=StatutInscription.INSCRIT,
    )

    class Meta:
        unique_together = [('formation', 'personnel')]
        verbose_name = 'inscription formation'
        verbose_name_plural = 'inscriptions formation'

    def __str__(self):
        return f'{self.personnel} — {self.formation.titre}'


class Certification(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nom = models.CharField(max_length=255)
    type_certification = models.CharField(max_length=100)
    duree_validite_mois = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text='Durée de validité en mois (null = pas de renouvellement automatique).',
    )
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['nom']
        verbose_name = 'certification'
        verbose_name_plural = 'certifications'

    def __str__(self):
        return self.nom


class CertificationPersonnel(TimeStampedModel, OptimisticLockModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    certification = models.ForeignKey(
        Certification,
        on_delete=models.PROTECT,
        related_name='detenteurs',
    )
    personnel = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='certifications',
    )
    date_obtention = models.DateField()
    date_expiration = models.DateField()
    numero_certificat = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['-date_expiration']
        verbose_name = 'certification personnel'
        verbose_name_plural = 'certifications personnel'

    def __str__(self):
        return f'{self.personnel} — {self.certification.nom}'

    @property
    def est_expiree(self) -> bool:
        return self.date_expiration < date.today()

    @property
    def a_renouveler(self) -> bool:
        if self.est_expiree:
            return True
        return self.date_expiration <= date.today() + timedelta(days=90)

    @property
    def statut_renouvellement(self) -> str:
        if self.est_expiree:
            return 'expirée'
        if self.a_renouveler:
            return 'à renouveler'
        return 'valide'


class Garde(TimeStampedModel, OptimisticLockModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    personnel = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='gardes',
    )
    service = models.ForeignKey(
        'logistics.Service',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='gardes',
    )
    type_garde = models.CharField(max_length=20, choices=TypeGarde.choices)
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField()
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['date_debut']
        indexes = [
            models.Index(fields=['date_debut']),
            models.Index(fields=['personnel', 'date_debut']),
        ]
        verbose_name = 'garde'
        verbose_name_plural = 'gardes'

    def __str__(self):
        return f'{self.personnel} — {self.get_type_garde_display()} ({self.date_debut:%d/%m/%Y})'
