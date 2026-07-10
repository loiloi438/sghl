import uuid
from decimal import Decimal

from django.conf import settings
from django.db import models

from core.models import TimeStampedModel
from patients.models import Patient


class OrganismeAssurance(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=20, unique=True)
    nom = models.CharField(max_length=150)
    taux_couverture = models.PositiveSmallIntegerField(default=80)
    actif = models.BooleanField(default=True)
    contact_email = models.EmailField(blank=True, default='')
    contact_telephone = models.CharField(max_length=30, blank=True, default='')
    notes = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['nom']
        verbose_name = 'organisme assurance'
        verbose_name_plural = 'organismes assurance'

    def __str__(self):
        return self.nom


class AffiliationPatient(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='affiliations')
    organisme = models.ForeignKey(OrganismeAssurance, on_delete=models.PROTECT, related_name='affiliations')
    numero_adherent = models.CharField(max_length=50, blank=True, default='')
    date_debut = models.DateField()
    date_fin = models.DateField(null=True, blank=True)
    actif = models.BooleanField(default=True)

    class Meta:
        ordering = ['-date_debut']
        verbose_name = 'affiliation patient'
        verbose_name_plural = 'affiliations patient'

    def __str__(self):
        return f'{self.patient} — {self.organisme.nom}'
