import uuid

from django.conf import settings
from django.db import models

from core.models import OptimisticLockModel, TimeStampedModel


class Sexe(models.TextChoices):
    MASCULIN = 'M', 'Masculin'
    FEMININ = 'F', 'Féminin'
    AUTRE = 'A', 'Autre'


class Patient(TimeStampedModel, OptimisticLockModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero_dossier = models.CharField('N° dossier', max_length=20, unique=True)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    date_naissance = models.DateField()
    sexe = models.CharField(max_length=1, choices=Sexe.choices)
    telephone = models.CharField(max_length=20, blank=True, default='')
    email = models.EmailField(blank=True, default='')
    adresse = models.TextField(blank=True, default='')
    photo = models.CharField(max_length=100, blank=True, default='')
    allergies = models.TextField(blank=True, default='')
    antecedents_medicaux = models.TextField(blank=True, default='')
    groupe_sanguin = models.CharField(max_length=5, blank=True, default='')
    traitements_en_cours = models.TextField(blank=True, default='')
    consentement_donnees = models.BooleanField(
        'Consentement traitement des données',
        default=False,
    )
    compte_utilisateur = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='profil_patient',
    )

    class Meta:
        ordering = ['nom', 'prenom']
        indexes = [
            models.Index(fields=['numero_dossier']),
            models.Index(fields=['nom', 'prenom']),
        ]

    def __str__(self):
        return f'{self.numero_dossier} — {self.nom} {self.prenom}'
