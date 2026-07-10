import uuid
from decimal import Decimal

from django.db import models

from core.models import OptimisticLockModel, TimeStampedModel


class CategorieArticle(models.TextChoices):
    CONSOMMABLE = 'consumable', 'Consommable'
    EQUIPEMENT = 'equipment', 'Équipement'
    MEDICATION = 'medication', 'Médicament'


class ArticleStock(TimeStampedModel, OptimisticLockModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=30, unique=True)
    nom = models.CharField(max_length=255)
    categorie = models.CharField(max_length=20, choices=CategorieArticle.choices, default=CategorieArticle.CONSOMMABLE)
    quantite = models.PositiveIntegerField(default=0)
    seuil_alerte = models.PositiveIntegerField(default=10)
    unite = models.CharField(max_length=20, default='unité')
    valeur_unitaire = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    actif = models.BooleanField(default=True)

    class Meta:
        ordering = ['nom']
        verbose_name = 'article stock'
        verbose_name_plural = 'articles stock'

    def __str__(self):
        return f'{self.code} — {self.nom}'

    @property
    def stock_level(self) -> str:
        if self.quantite <= self.seuil_alerte // 2:
            return 'critical'
        if self.quantite <= self.seuil_alerte:
            return 'low'
        if self.quantite <= self.seuil_alerte * 3:
            return 'normal'
        return 'high'

    @property
    def valeur_totale(self) -> Decimal:
        return self.valeur_unitaire * self.quantite
