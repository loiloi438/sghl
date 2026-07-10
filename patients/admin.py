from django.contrib import admin

from .models import Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('numero_dossier', 'nom', 'prenom', 'date_naissance', 'sexe', 'consentement_donnees')
    search_fields = ('numero_dossier', 'nom', 'prenom')
    list_filter = ('sexe', 'consentement_donnees')
