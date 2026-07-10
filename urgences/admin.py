from django.contrib import admin

from urgences.models import PassageUrgence


@admin.register(PassageUrgence)
class PassageUrgenceAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'niveau_triage', 'statut', 'heure_arrivee')
    list_filter = ('niveau_triage', 'statut')
