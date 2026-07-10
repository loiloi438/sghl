from django.contrib import admin

from .models import LigneDispensation, MedicamentStock, OrdreDispensation


class LigneDispensationInline(admin.TabularInline):
    model = LigneDispensation
    extra = 0
    readonly_fields = ('ligne_prescription', 'medicament_stock', 'quantite')


@admin.register(MedicamentStock)
class MedicamentStockAdmin(admin.ModelAdmin):
    list_display = ('code', 'libelle', 'quantite_stock', 'unite', 'seuil_alerte', 'actif')
    list_filter = ('actif',)
    search_fields = ('code', 'libelle')


@admin.register(OrdreDispensation)
class OrdreDispensationAdmin(admin.ModelAdmin):
    list_display = ('id', 'prescription', 'statut', 'pharmacien', 'dispense_le', 'created_at')
    list_filter = ('statut',)
    readonly_fields = ('prepare_le', 'dispense_le', 'version', 'created_at', 'updated_at')
    inlines = [LigneDispensationInline]
