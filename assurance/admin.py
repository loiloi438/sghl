from django.contrib import admin

from assurance.models import AffiliationPatient, OrganismeAssurance


@admin.register(OrganismeAssurance)
class OrganismeAssuranceAdmin(admin.ModelAdmin):
    list_display = ('code', 'nom', 'taux_couverture', 'actif')
    search_fields = ('code', 'nom')


@admin.register(AffiliationPatient)
class AffiliationPatientAdmin(admin.ModelAdmin):
    list_display = ('patient', 'organisme', 'numero_adherent', 'actif')
    list_filter = ('actif',)
