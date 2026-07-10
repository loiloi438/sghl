from django.contrib import admin

from core.models import ConfigurationEtablissement


@admin.register(ConfigurationEtablissement)
class ConfigurationEtablissementAdmin(admin.ModelAdmin):
    list_display = ('organization_name', 'mfa_required', 'maintenance_mode')
