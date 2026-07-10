from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class OptimisticLockModel(models.Model):
    """Verrouillage optimiste requis par le cahier des charges."""

    version = models.PositiveIntegerField(default=1)

    class Meta:
        abstract = True

    def bump_version(self):
        self.version += 1


class ConfigurationEtablissement(TimeStampedModel, OptimisticLockModel):
    """Singleton de configuration système (pk=1)."""

    organization_name = models.CharField(max_length=255, default='SGHL — Centre Hospitalier')
    address = models.TextField(blank=True, default='')
    phone = models.CharField(max_length=30, blank=True, default='')
    email = models.EmailField(blank=True, default='support@sghl.local')
    finess_number = models.CharField('N° FINESS', max_length=20, blank=True, default='')
    mfa_required = models.BooleanField(default=True)
    session_timeout_minutes = models.PositiveSmallIntegerField(default=15)
    max_login_attempts = models.PositiveSmallIntegerField(default=5)
    audit_logging_enabled = models.BooleanField(default=True)
    encryption_level = models.CharField(max_length=20, default='standard')
    maintenance_mode = models.BooleanField(default=False)
    maintenance_message = models.TextField(blank=True, default='')
    hl7_enabled = models.BooleanField(default=False)
    fhir_enabled = models.BooleanField(default=False)
    insurance_api_enabled = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'configuration établissement'
        verbose_name_plural = 'configuration établissement'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
