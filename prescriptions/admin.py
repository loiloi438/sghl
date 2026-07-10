from django.contrib import admin

from .models import DiagnosticCIM10, LignePrescription, Prescription, PrescriptionDiagnostic


class LignePrescriptionInline(admin.TabularInline):
    model = LignePrescription
    extra = 0


class PrescriptionDiagnosticInline(admin.TabularInline):
    model = PrescriptionDiagnostic
    extra = 0
    readonly_fields = ('code_cim10', 'libelle')


@admin.register(DiagnosticCIM10)
class DiagnosticCIM10Admin(admin.ModelAdmin):
    list_display = ('code', 'libelle', 'actif')
    search_fields = ('code', 'libelle')
    list_filter = ('actif',)


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'hospitalisation', 'medecin', 'statut', 'validee_le', 'created_at')
    list_filter = ('statut',)
    readonly_fields = ('validee_le', 'validee_par', 'version', 'created_at', 'updated_at')
    inlines = [PrescriptionDiagnosticInline, LignePrescriptionInline]
