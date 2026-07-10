from django.contrib import admin

from inventaire.models import ArticleStock


@admin.register(ArticleStock)
class ArticleStockAdmin(admin.ModelAdmin):
    list_display = ('code', 'nom', 'categorie', 'quantite', 'seuil_alerte', 'actif')
    list_filter = ('categorie', 'actif')
    search_fields = ('code', 'nom')
