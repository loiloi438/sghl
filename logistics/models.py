import uuid

from django.db import models

from core.models import OptimisticLockModel, TimeStampedModel


class Batiment(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=20, unique=True)
    nom = models.CharField(max_length=150)
    actif = models.BooleanField(default=True)

    class Meta:
        ordering = ['code']
        verbose_name = 'bâtiment'
        verbose_name_plural = 'bâtiments'

    def __str__(self):
        return f'{self.code} — {self.nom}'


class Service(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    batiment = models.ForeignKey(Batiment, on_delete=models.PROTECT, related_name='services')
    code = models.CharField(max_length=20)
    nom = models.CharField(max_length=150)
    actif = models.BooleanField(default=True)

    class Meta:
        ordering = ['batiment__code', 'code']
        unique_together = [('batiment', 'code')]
        verbose_name = 'service'
        verbose_name_plural = 'services'

    def __str__(self):
        return f'{self.batiment.code}/{self.code} — {self.nom}'


class Chambre(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    service = models.ForeignKey(Service, on_delete=models.PROTECT, related_name='chambres')
    numero = models.CharField('N° chambre', max_length=20)
    actif = models.BooleanField(default=True)

    class Meta:
        ordering = ['service__code', 'numero']
        unique_together = [('service', 'numero')]
        verbose_name = 'chambre'
        verbose_name_plural = 'chambres'

    def __str__(self):
        return f'{self.service} — Ch. {self.numero}'


class StatutLit(models.TextChoices):
    LIBRE = 'libre', 'Libre'
    OCCUPE = 'occupe', 'Occupé'
    MAINTENANCE = 'maintenance', 'Maintenance'


class Lit(TimeStampedModel, OptimisticLockModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chambre = models.ForeignKey(Chambre, on_delete=models.PROTECT, related_name='lits')
    numero = models.CharField('N° lit', max_length=10)
    statut = models.CharField(max_length=20, choices=StatutLit.choices, default=StatutLit.LIBRE)
    actif = models.BooleanField(default=True)

    class Meta:
        ordering = ['chambre__numero', 'numero']
        unique_together = [('chambre', 'numero')]
        indexes = [
            models.Index(fields=['statut']),
        ]
        verbose_name = 'lit'
        verbose_name_plural = 'lits'

    def __str__(self):
        return f'{self.chambre} — Lit {self.numero} ({self.get_statut_display()})'

    @property
    def est_disponible(self) -> bool:
        return self.actif and self.statut == StatutLit.LIBRE
