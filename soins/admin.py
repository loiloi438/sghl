from django.contrib import admin

from .models import ConstanteVitale, DosePlanifiee, InterventionInfirmiere, PlanSoins


class DosePlanifieeInline(admin.TabularInline):
    model = DosePlanifiee
    extra = 0


@admin.register(PlanSoins)
class PlanSoinsAdmin(admin.ModelAdmin):
    list_display = ('titre', 'hospitalisation', 'statut', 'date_debut', 'cree_par')
    list_filter = ('statut',)
    inlines = [DosePlanifieeInline]


@admin.register(ConstanteVitale)
class ConstanteVitaleAdmin(admin.ModelAdmin):
    list_display = (
        'hospitalisation',
        'mesure_le',
        'temperature',
        'tension_systolique',
        'frequence_cardiaque',
        'infirmier',
    )
    list_filter = ('mesure_le',)


@admin.register(InterventionInfirmiere)
class InterventionInfirmiereAdmin(admin.ModelAdmin):
    list_display = ('type_intervention', 'hospitalisation', 'realisee_le', 'infirmier')
    list_filter = ('type_intervention',)


@admin.register(DosePlanifiee)
class DosePlanifieeAdmin(admin.ModelAdmin):
    list_display = ('medicament', 'plan_soins', 'heure_prevue', 'statut', 'infirmier')
    list_filter = ('statut',)
