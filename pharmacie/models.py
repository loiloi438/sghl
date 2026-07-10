import uuid
from django.conf import settings
from django.db import models
from django.utils import timezone

from core.models import OptimisticLockModel, TimeStampedModel
from prescriptions.models import LignePrescription, Prescription


class MedicamentStock(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=30, unique=True)
    libelle = models.CharField(max_length=200)
    forme = models.CharField(max_length=80, blank=True)
    quantite_stock = models.PositiveIntegerField(default=0)
    unite = models.CharField(max_length=30, default='unité')
    seuil_alerte = models.PositiveIntegerField(default=10)
    date_peremption = models.DateField('Date de péremption', null=True, blank=True)
    actif = models.BooleanField(default=True)

    class Meta:
        ordering = ['libelle']
        verbose_name = 'médicament en stock'
        verbose_name_plural = 'stock pharmacie'

    def __str__(self):
        return f'{self.code} — {self.libelle} ({self.quantite_stock} {self.unite})'

    @property
    def stock_bas(self) -> bool:
        return self.quantite_stock <= self.seuil_alerte

    @property
    def est_perime(self) -> bool:
        if not self.date_peremption:
            return False
        return self.date_peremption < timezone.localdate()

    @property
    def peremption_proche(self) -> bool:
        """Péremption dans les 30 prochains jours (CDC alertes)."""
        if not self.date_peremption or self.est_perime:
            return False
        limite = timezone.localdate().toordinal() + 30
        return self.date_peremption.toordinal() <= limite


class StatutOrdreDispensation(models.TextChoices):
    EN_ATTENTE = 'en_attente', 'En attente'
    PREPARE = 'prepare', 'Préparé'
    DISPENSE = 'dispense', 'Dispensé'
    ANNULE = 'annule', 'Annulé'


class OrdreDispensation(TimeStampedModel, OptimisticLockModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    prescription = models.OneToOneField(
        Prescription,
        on_delete=models.PROTECT,
        related_name='ordre_dispensation',
    )
    statut = models.CharField(
        max_length=20,
        choices=StatutOrdreDispensation.choices,
        default=StatutOrdreDispensation.EN_ATTENTE,
    )
    pharmacien = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='dispensations_effectuees',
    )
    prepare_le = models.DateTimeField(null=True, blank=True)
    dispense_le = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['statut'])]
        verbose_name = 'ordre de dispensation'
        verbose_name_plural = 'ordres de dispensation'

    def __str__(self):
        return f'Ordre {self.id} ({self.get_statut_display()})'

    @property
    def est_verrouille(self) -> bool:
        return self.statut == StatutOrdreDispensation.DISPENSE


class LigneDispensation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ordre = models.ForeignKey(
        OrdreDispensation,
        on_delete=models.CASCADE,
        related_name='lignes',
    )
    ligne_prescription = models.ForeignKey(
        LignePrescription,
        on_delete=models.PROTECT,
        related_name='dispensations',
    )
    medicament_stock = models.ForeignKey(
        MedicamentStock,
        on_delete=models.PROTECT,
        related_name='lignes_dispensation',
    )
    quantite = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = [('ordre', 'ligne_prescription')]
        verbose_name = 'ligne de dispensation'
        verbose_name_plural = 'lignes de dispensation'

    def __str__(self):
        return f'{self.medicament_stock.libelle} x{self.quantite}'
