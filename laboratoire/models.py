import uuid

from django.conf import settings
from django.db import models

from core.models import OptimisticLockModel, TimeStampedModel
from hospitalisation.models import Hospitalisation


class StatutCommandeAnalyse(models.TextChoices):
    COMMANDEE = 'commandee', 'Commandée'
    PRELEVEE = 'prelevee', 'Prélevée'
    AFFECTEE = 'affectee', 'Affectée'
    RESULTATS_SAISIS = 'resultats_saisis', 'Résultats saisis'
    VALIDEE = 'validee', 'Validée'
    PUBLIEE = 'publiee', 'Publiée'
    ANNULEE = 'annulee', 'Annulée'


class AnalyseCatalogue(models.Model):
    code = models.CharField('Code analyse', max_length=20, unique=True)
    libelle = models.CharField(max_length=255)
    unite_reference = models.CharField(max_length=50, blank=True)
    valeur_reference = models.CharField(max_length=100, blank=True)
    actif = models.BooleanField(default=True)

    class Meta:
        ordering = ['code']
        verbose_name = 'analyse catalogue'
        verbose_name_plural = 'catalogue analyses'

    def __str__(self):
        return f'{self.code} — {self.libelle}'


class CommandeAnalyse(TimeStampedModel, OptimisticLockModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hospitalisation = models.ForeignKey(
        Hospitalisation,
        on_delete=models.PROTECT,
        related_name='commandes_analyses',
    )
    medecin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='commandes_analyses_redigees',
    )
    statut = models.CharField(
        max_length=20,
        choices=StatutCommandeAnalyse.choices,
        default=StatutCommandeAnalyse.COMMANDEE,
    )
    observations = models.TextField(blank=True)
    preleve_le = models.DateTimeField(null=True, blank=True)
    preleve_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='prelevements_effectues',
    )
    type_echantillon = models.CharField(max_length=100, blank=True)
    reference_echantillon = models.CharField(max_length=100, blank=True)
    affectee_le = models.DateTimeField(null=True, blank=True)
    affectee_a = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='analyses_affectees',
    )
    affectee_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='affectations_realisees',
    )
    validee_le = models.DateTimeField(null=True, blank=True)
    validee_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='commandes_analyses_validees',
    )
    publiee_le = models.DateTimeField(null=True, blank=True)
    publiee_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='commandes_analyses_publiees',
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['statut']),
            models.Index(fields=['created_at']),
        ]
        verbose_name = 'commande analyse'
        verbose_name_plural = 'commandes analyses'

    def __str__(self):
        return f'Commande {self.id} ({self.get_statut_display()})'

    @property
    def est_verrouillee(self) -> bool:
        return self.statut in {
            StatutCommandeAnalyse.VALIDEE,
            StatutCommandeAnalyse.PUBLIEE,
        }

    @property
    def est_modifiable(self) -> bool:
        return self.statut == StatutCommandeAnalyse.COMMANDEE


class LigneCommandeAnalyse(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    commande = models.ForeignKey(
        CommandeAnalyse,
        on_delete=models.CASCADE,
        related_name='lignes',
    )
    code_analyse = models.CharField(max_length=20)
    libelle = models.CharField(max_length=255)
    unite_reference = models.CharField(max_length=50, blank=True)
    valeur_reference = models.CharField(max_length=100, blank=True)

    class Meta:
        unique_together = [('commande', 'code_analyse')]
        ordering = ['code_analyse']
        verbose_name = 'ligne commande analyse'
        verbose_name_plural = 'lignes commande analyse'

    def __str__(self):
        return f'{self.code_analyse} — {self.libelle}'


class ResultatAnalyse(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ligne = models.OneToOneField(
        LigneCommandeAnalyse,
        on_delete=models.CASCADE,
        related_name='resultat',
    )
    valeur = models.CharField(max_length=100)
    unite = models.CharField(max_length=50, blank=True)
    commentaire = models.TextField(blank=True)
    saisi_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='resultats_analyses_saisis',
    )

    class Meta:
        verbose_name = 'résultat analyse'
        verbose_name_plural = 'résultats analyses'

    def __str__(self):
        return f'{self.ligne.code_analyse} = {self.valeur}'
