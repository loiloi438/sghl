from django.contrib import admin

from .models import Facture, LigneFacture, TarifActe


class LigneFactureInline(admin.TabularInline):
    model = LigneFacture
    extra = 0
    readonly_fields = ('code_acte', 'libelle', 'quantite', 'prix_unitaire', 'montant_ligne', 'source')


@admin.register(TarifActe)
class TarifActeAdmin(admin.ModelAdmin):
    list_display = ('code', 'libelle', 'categorie', 'prix_unitaire', 'actif')
    list_filter = ('categorie', 'actif')
    search_fields = ('code', 'libelle')


@admin.register(Facture)
class FactureAdmin(admin.ModelAdmin):
    list_display = (
        'numero_facture',
        'hospitalisation',
        'statut',
        'montant_total',
        'validee_le',
        'payee_le',
    )
    list_filter = ('statut',)
    readonly_fields = (
        'numero_facture',
        'montant_total',
        'validee_le',
        'validee_par',
        'payee_le',
        'enregistree_par',
        'version',
        'created_at',
        'updated_at',
    )
    inlines = [LigneFactureInline]
