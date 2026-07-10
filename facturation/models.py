import uuid
from decimal import Decimal

from django.conf import settings
from django.db import models

from core.models import OptimisticLockModel, TimeStampedModel
from hospitalisation.models import Hospitalisation


class CategorieTarif(models.TextChoices):
    SEJOUR = 'sejour', 'Séjour'
    LABORATOIRE = 'laboratoire', 'Laboratoire'
    PHARMACIE = 'pharmacie', 'Pharmacie'
    SOINS = 'soins', 'Soins'
    DIVERS = 'divers', 'Divers'


class TarifActe(models.Model):
    code = models.CharField(max_length=30, unique=True)
    libelle = models.CharField(max_length=255)
    categorie = models.CharField(max_length=20, choices=CategorieTarif.choices)
    prix_unitaire = models.DecimalField(max_digits=12, decimal_places=2)
    actif = models.BooleanField(default=True)

    class Meta:
        ordering = ['categorie', 'code']
        verbose_name = 'tarif acte'
        verbose_name_plural = 'tarifs actes'

    def __str__(self):
        return f'{self.code} — {self.libelle} ({self.prix_unitaire})'


class StatutFacture(models.TextChoices):
    BROUILLON = 'brouillon', 'Brouillon'
    VALIDEE = 'validee', 'Validée'
    PARTIELLEMENT_PAYEE = 'partiellement_payee', 'Partiellement payée'
    PAYEE = 'payee', 'Payée'
    ANNULEE = 'annulee', 'Annulée'


class SourceLigneFacture(models.TextChoices):
    AUTO_SEJOUR = 'auto_sejour', 'Séjour (auto)'
    AUTO_LABO = 'auto_labo', 'Laboratoire (auto)'
    AUTO_PHARMA = 'auto_pharma', 'Pharmacie (auto)'
    MANUELLE = 'manuelle', 'Manuelle'


class Facture(TimeStampedModel, OptimisticLockModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hospitalisation = models.OneToOneField(
        Hospitalisation,
        on_delete=models.PROTECT,
        related_name='facture',
    )
    numero_facture = models.CharField(max_length=30, unique=True, null=True, blank=True)
    statut = models.CharField(
        max_length=20,
        choices=StatutFacture.choices,
        default=StatutFacture.BROUILLON,
    )
    montant_total = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0'))
    montant_paye = models.DecimalField(
        'Montant payé par le patient',
        max_digits=14,
        decimal_places=2,
        default=Decimal('0'),
    )
    tiers_payant_organisme = models.CharField(max_length=150, blank=True)
    tiers_payant_montant = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('0'),
    )
    validee_le = models.DateTimeField(null=True, blank=True)
    validee_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='factures_validees',
    )
    payee_le = models.DateTimeField(null=True, blank=True)
    enregistree_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='factures_payees',
    )
    mode_paiement = models.CharField(max_length=50, blank=True)
    reference_paiement = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['statut'])]
        verbose_name = 'facture'
        verbose_name_plural = 'factures'

    def __str__(self):
        ref = self.numero_facture or str(self.id)[:8]
        return f'Facture {ref} ({self.get_statut_display()})'

    @property
    def est_modifiable(self) -> bool:
        return self.statut == StatutFacture.BROUILLON

    @property
    def est_verrouillee(self) -> bool:
        return self.statut in {
            StatutFacture.VALIDEE,
            StatutFacture.PARTIELLEMENT_PAYEE,
            StatutFacture.PAYEE,
        }

    @property
    def montant_couvert(self) -> Decimal:
        return self.montant_paye + self.tiers_payant_montant

    @property
    def montant_restant(self) -> Decimal:
        reste = self.montant_total - self.montant_couvert
        return reste if reste > Decimal('0') else Decimal('0')


class TypeEcritureComptable(models.TextChoices):
    VALIDATION = 'validation', 'Validation facture'
    PAIEMENT_PATIENT = 'paiement_patient', 'Paiement patient'
    PAIEMENT_TIERS = 'paiement_tiers', 'Tiers payant'


class EcritureComptable(models.Model):
    """Journal comptable immuable (CDC finances)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    facture = models.ForeignKey(
        Facture,
        on_delete=models.PROTECT,
        related_name='ecritures_comptables',
    )
    type_ecriture = models.CharField(max_length=30, choices=TypeEcritureComptable.choices)
    montant = models.DecimalField(max_digits=14, decimal_places=2)
    libelle = models.CharField(max_length=255)
    comptable = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='ecritures_comptables',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'écriture comptable'
        verbose_name_plural = 'écritures comptables'

    def __str__(self):
        return f'{self.get_type_ecriture_display()} — {self.montant}'


class LigneFacture(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    facture = models.ForeignKey(Facture, on_delete=models.CASCADE, related_name='lignes')
    code_acte = models.CharField(max_length=30)
    libelle = models.CharField(max_length=255)
    quantite = models.PositiveIntegerField(default=1)
    prix_unitaire = models.DecimalField(max_digits=12, decimal_places=2)
    montant_ligne = models.DecimalField(max_digits=14, decimal_places=2)
    source = models.CharField(max_length=20, choices=SourceLigneFacture.choices)

    class Meta:
        ordering = ['code_acte', 'libelle']
        verbose_name = 'ligne de facture'
        verbose_name_plural = 'lignes de facture'

    def __str__(self):
        return f'{self.libelle} x{self.quantite} = {self.montant_ligne}'
