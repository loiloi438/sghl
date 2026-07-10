from django.contrib import admin

from rh.models import (
    Certification,
    CertificationPersonnel,
    Formation,
    Garde,
    InscriptionFormation,
)


class InscriptionFormationInline(admin.TabularInline):
    model = InscriptionFormation
    extra = 0


@admin.register(Formation)
class FormationAdmin(admin.ModelAdmin):
    list_display = ('titre', 'formateur', 'date_debut', 'date_fin', 'statut', 'capacite_max')
    list_filter = ('statut',)
    search_fields = ('titre', 'formateur')
    inlines = [InscriptionFormationInline]


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ('nom', 'type_certification', 'duree_validite_mois')
    search_fields = ('nom', 'type_certification')


@admin.register(CertificationPersonnel)
class CertificationPersonnelAdmin(admin.ModelAdmin):
    list_display = ('personnel', 'certification', 'date_obtention', 'date_expiration')
    list_filter = ('certification',)
    search_fields = ('personnel__username', 'certification__nom')


@admin.register(Garde)
class GardeAdmin(admin.ModelAdmin):
    list_display = ('personnel', 'type_garde', 'date_debut', 'date_fin', 'service')
    list_filter = ('type_garde',)
    search_fields = ('personnel__username', 'notes')
