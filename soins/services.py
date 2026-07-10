from django.utils import timezone

from hospitalisation.models import Hospitalisation, StatutHospitalisation
from soins.models import DosePlanifiee, PlanSoins, StatutDose, StatutPlanSoins


class SoinsError(Exception):
    def __init__(self, message: str, code: str = 'error'):
        self.message = message
        self.code = code
        super().__init__(message)


def get_hospitalisation_active(hospitalisation_id) -> Hospitalisation:
    hospitalisation = get_hospitalisation_or_raise(hospitalisation_id)
    if hospitalisation.statut != StatutHospitalisation.ACTIVE:
        raise SoinsError(
            'Les soins ne sont possibles que pour une hospitalisation active.',
            code='hospitalisation_inactive',
        )
    return hospitalisation


def get_hospitalisation_or_raise(hospitalisation_id) -> Hospitalisation:
    try:
        return Hospitalisation.objects.get(id=hospitalisation_id)
    except Hospitalisation.DoesNotExist:
        raise SoinsError('Hospitalisation introuvable.', code='not_found')


def get_plan_soins_actif(plan_id) -> PlanSoins:
    try:
        plan = PlanSoins.objects.select_related('hospitalisation').get(id=plan_id)
    except PlanSoins.DoesNotExist:
        raise SoinsError('Plan de soins introuvable.', code='not_found')
    get_hospitalisation_active(plan.hospitalisation_id)
    if plan.statut != StatutPlanSoins.ACTIF:
        raise SoinsError('Ce plan de soins n\'est plus actif.', code='plan_inactif')
    return plan


def administrer_dose(*, dose: DosePlanifiee, infirmier, version: int) -> DosePlanifiee:
    get_plan_soins_actif(dose.plan_soins_id)
    if dose.version != version:
        raise SoinsError('Conflit de version : rechargez et réessayez.', code='version_conflict')
    if dose.statut != StatutDose.PLANIFIEE:
        raise SoinsError('Cette dose a déjà été traitée.', code='dose_deja_traitee')

    dose.statut = StatutDose.ADMINISTREE
    dose.administree_le = timezone.now()
    dose.infirmier = infirmier
    dose.bump_version()
    dose.save(update_fields=['statut', 'administree_le', 'infirmier', 'version', 'updated_at'])
    return dose


def marquer_dose_omise(*, dose: DosePlanifiee, infirmier, version: int) -> DosePlanifiee:
    get_plan_soins_actif(dose.plan_soins_id)
    if dose.version != version:
        raise SoinsError('Conflit de version : rechargez et réessayez.', code='version_conflict')
    if dose.statut != StatutDose.PLANIFIEE:
        raise SoinsError('Cette dose a déjà été traitée.', code='dose_deja_traitee')

    dose.statut = StatutDose.OMISE
    dose.infirmier = infirmier
    dose.bump_version()
    dose.save(update_fields=['statut', 'infirmier', 'version', 'updated_at'])
    return dose


def doses_omises(hospitalisation_id=None):
    """Doses planifiées en retard non administrées."""
    qs = DosePlanifiee.objects.filter(
        statut=StatutDose.PLANIFIEE,
        heure_prevue__lt=timezone.now(),
        plan_soins__statut=StatutPlanSoins.ACTIF,
        plan_soins__hospitalisation__statut=StatutHospitalisation.ACTIVE,
    ).select_related('plan_soins__hospitalisation__patient')
    if hospitalisation_id:
        qs = qs.filter(plan_soins__hospitalisation_id=hospitalisation_id)
    return qs.order_by('heure_prevue')
