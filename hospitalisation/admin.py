from django.contrib import admin

from .models import Hospitalisation


@admin.register(Hospitalisation)
class HospitalisationAdmin(admin.ModelAdmin):
    list_display = (
        'patient',
        'lit',
        'statut',
        'date_admission',
        'date_sortie_effective',
        'medecin_referent',
    )
    list_filter = ('statut', 'date_admission')
    search_fields = ('patient__nom', 'patient__prenom', 'patient__numero_dossier')
    readonly_fields = ('created_at', 'updated_at', 'version')
