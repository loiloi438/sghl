from django.contrib import admin

from .models import AnalyseCatalogue, CommandeAnalyse, LigneCommandeAnalyse, ResultatAnalyse


class LigneCommandeAnalyseInline(admin.TabularInline):
    model = LigneCommandeAnalyse
    extra = 0
    readonly_fields = ('code_analyse', 'libelle', 'unite_reference', 'valeur_reference')


@admin.register(AnalyseCatalogue)
class AnalyseCatalogueAdmin(admin.ModelAdmin):
    list_display = ('code', 'libelle', 'unite_reference', 'valeur_reference', 'actif')
    search_fields = ('code', 'libelle')
    list_filter = ('actif',)


@admin.register(CommandeAnalyse)
class CommandeAnalyseAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'hospitalisation',
        'medecin',
        'statut',
        'validee_le',
        'publiee_le',
        'created_at',
    )
    list_filter = ('statut',)
    readonly_fields = (
        'preleve_le',
        'preleve_par',
        'affectee_le',
        'affectee_a',
        'affectee_par',
        'validee_le',
        'validee_par',
        'publiee_le',
        'publiee_par',
        'version',
        'created_at',
        'updated_at',
    )
    inlines = [LigneCommandeAnalyseInline]


@admin.register(ResultatAnalyse)
class ResultatAnalyseAdmin(admin.ModelAdmin):
    list_display = ('ligne', 'valeur', 'unite', 'saisi_par', 'created_at')
    readonly_fields = ('created_at', 'updated_at')
