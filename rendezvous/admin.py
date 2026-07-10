from django.contrib import admin

from rendezvous.models import RendezVous


@admin.register(RendezVous)
class RendezVousAdmin(admin.ModelAdmin):
    list_display = (
        'date_heure',
        'patient',
        'medecin',
        'motif',
        'statut',
    )
    list_filter = ('statut', 'medecin')
    search_fields = ('patient__nom', 'patient__prenom', 'motif')
    readonly_fields = (
        'created_at',
        'updated_at',
        'confirme_le',
        'annule_le',
        'rappel_j1_envoye_le',
    )
