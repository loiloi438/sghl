import uuid

from django.conf import settings
from django.db import models

from core.models import TimeStampedModel


class TypeDocument(models.TextChoices):
    FACTURE = 'facture', 'Facture'
    COMPTE_RENDU_LABO = 'compte_rendu_labo', 'Compte-rendu laboratoire'
    ORDONNANCE = 'ordonnance', 'Ordonnance'


class DocumentSigne(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type_document = models.CharField(max_length=30, choices=TypeDocument.choices)
    facture = models.OneToOneField(
        'facturation.Facture',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='document_pdf',
    )
    commande_analyse = models.OneToOneField(
        'laboratoire.CommandeAnalyse',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='document_pdf',
    )
    prescription = models.OneToOneField(
        'prescriptions.Prescription',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='document_pdf',
    )
    fichier = models.FileField(upload_to='documents/%Y/%m/')
    empreinte_sha256 = models.CharField(max_length=64)
    signature = models.CharField(max_length=64)
    code_verification = models.CharField(max_length=12)
    signe_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='documents_signes',
    )
    signe_le = models.DateTimeField()
    signataire_nom = models.CharField(max_length=200)
    signataire_role = models.CharField(max_length=50)
    numero_reference = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ['-signe_le']
        indexes = [
            models.Index(fields=['type_document']),
            models.Index(fields=['code_verification']),
        ]
        verbose_name = 'document signé'
        verbose_name_plural = 'documents signés'

    def __str__(self):
        ref = self.numero_reference or str(self.id)[:8]
        return f'{self.get_type_document_display()} — {ref}'
