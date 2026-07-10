from django.contrib import admin

from .models import Batiment, Chambre, Lit, Service


class ServiceInline(admin.TabularInline):
    model = Service
    extra = 0


@admin.register(Batiment)
class BatimentAdmin(admin.ModelAdmin):
    list_display = ('code', 'nom', 'actif', 'created_at')
    search_fields = ('code', 'nom')
    list_filter = ('actif',)
    inlines = [ServiceInline]


class ChambreInline(admin.TabularInline):
    model = Chambre
    extra = 0


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('code', 'nom', 'batiment', 'actif')
    list_filter = ('batiment', 'actif')
    search_fields = ('code', 'nom')


class LitInline(admin.TabularInline):
    model = Lit
    extra = 0


@admin.register(Chambre)
class ChambreAdmin(admin.ModelAdmin):
    list_display = ('numero', 'service', 'actif')
    list_filter = ('service__batiment', 'actif')
    inlines = [LitInline]


@admin.register(Lit)
class LitAdmin(admin.ModelAdmin):
    list_display = ('numero', 'chambre', 'statut', 'actif', 'version')
    list_filter = ('statut', 'actif', 'chambre__service__batiment')
    search_fields = ('numero', 'chambre__numero')
