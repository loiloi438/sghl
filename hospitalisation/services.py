from datetime import date, datetime, timezone

from django.db import transaction

from hospitalisation.models import Hospitalisation, StatutHospitalisation
from logistics.models import Lit, StatutLit
from patients.models import Patient


class HospitalisationError(Exception):
    def __init__(self, message: str, code: str = 'error'):
        self.message = message
        self.code = code
        super().__init__(message)


def patient_a_hospitalisation_active(patient: Patient) -> bool:
    return Hospitalisation.objects.filter(
        patient=patient,
        statut=StatutHospitalisation.ACTIVE,
    ).exists()


@transaction.atomic
def admettre_patient(
    *,
    patient: Patient,
    lit: Lit,
    motif_admission: str,
    medecin_referent=None,
    date_admission: datetime | None = None,
    date_sortie_prevue: date | None = None,
    lit_version: int,
) -> Hospitalisation:
    lit_verrouille = Lit.objects.select_for_update().get(pk=lit.pk)

    if not lit_verrouille.est_disponible:
        raise HospitalisationError(
            'Ce lit n\'est pas disponible pour une admission.',
            code='lit_indisponible',
        )
    if lit_verrouille.version != lit_version:
        raise HospitalisationError(
            'Conflit de version sur le lit : rechargez et réessayez.',
            code='version_conflict',
        )
    if patient_a_hospitalisation_active(patient):
        raise HospitalisationError(
            'Ce patient a déjà une hospitalisation active.',
            code='patient_deja_hospitalise',
        )

    hospitalisation = Hospitalisation.objects.create(
        patient=patient,
        lit=lit_verrouille,
        medecin_referent=medecin_referent,
        motif_admission=motif_admission,
        date_admission=date_admission or datetime.now(timezone.utc),
        date_sortie_prevue=date_sortie_prevue,
        statut=StatutHospitalisation.ACTIVE,
    )

    lit_verrouille.statut = StatutLit.OCCUPE
    lit_verrouille.bump_version()
    lit_verrouille.save(update_fields=['statut', 'version', 'updated_at'])

    return hospitalisation


@transaction.atomic
def sortir_patient(
    *,
    hospitalisation: Hospitalisation,
    hospitalisation_version: int,
    date_sortie: datetime | None = None,
) -> Hospitalisation:
    hosp = Hospitalisation.objects.select_for_update().get(pk=hospitalisation.pk)

    if hosp.statut != StatutHospitalisation.ACTIVE:
        raise HospitalisationError(
            'Cette hospitalisation n\'est pas active.',
            code='hospitalisation_inactive',
        )
    if hosp.version != hospitalisation_version:
        raise HospitalisationError(
            'Conflit de version : rechargez et réessayez.',
            code='version_conflict',
        )

    lit = Lit.objects.select_for_update().get(pk=hosp.lit_id)

    hosp.statut = StatutHospitalisation.SORTIE
    hosp.date_sortie_effective = date_sortie or datetime.now(timezone.utc)
    hosp.bump_version()
    hosp.save(update_fields=['statut', 'date_sortie_effective', 'version', 'updated_at'])

    lit.statut = StatutLit.LIBRE
    lit.bump_version()
    lit.save(update_fields=['statut', 'version', 'updated_at'])

    return hosp
