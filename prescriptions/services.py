from django.db import transaction
from django.utils import timezone

from accounts.models import Role, User
from hospitalisation.models import Hospitalisation, StatutHospitalisation
from prescriptions.models import (
    DiagnosticCIM10,
    LignePrescription,
    Prescription,
    PrescriptionDiagnostic,
    StatutPrescription,
)


class PrescriptionError(Exception):
    def __init__(self, message: str, code: str = 'error'):
        self.message = message
        self.code = code
        super().__init__(message)


def get_hospitalisation_active(hospitalisation_id) -> Hospitalisation:
    try:
        hospitalisation = Hospitalisation.objects.get(id=hospitalisation_id)
    except Hospitalisation.DoesNotExist:
        raise PrescriptionError('Hospitalisation introuvable.', code='not_found')
    if hospitalisation.statut != StatutHospitalisation.ACTIVE:
        raise PrescriptionError(
            'Une prescription requiert une hospitalisation active.',
            code='hospitalisation_inactive',
        )
    return hospitalisation


def get_prescription_modifiable(prescription_id) -> Prescription:
    try:
        prescription = Prescription.objects.select_related('hospitalisation').get(id=prescription_id)
    except Prescription.DoesNotExist:
        raise PrescriptionError('Prescription introuvable.', code='not_found')
    if not prescription.est_modifiable:
        raise PrescriptionError(
            'Cette prescription est verrouillée et ne peut plus être modifiée.',
            code='prescription_verrouillee',
        )
    get_hospitalisation_active(prescription.hospitalisation_id)
    return prescription


def get_prescription(prescription_id) -> Prescription:
    try:
        return Prescription.objects.select_related('hospitalisation', 'medecin').get(id=prescription_id)
    except Prescription.DoesNotExist:
        raise PrescriptionError('Prescription introuvable.', code='not_found')


def assert_medecin(user: User):
    if user.role not in {Role.ADMIN, Role.MEDECIN}:
        raise PrescriptionError('Seul un médecin peut effectuer cette action.', code='acces_refuse')


def creer_prescription(
    *,
    hospitalisation: Hospitalisation,
    medecin: User,
    observations: str = '',
    codes_cim10: list[str] | None = None,
) -> Prescription:
    assert_medecin(medecin)
    get_hospitalisation_active(hospitalisation.id)

    prescription = Prescription.objects.create(
        hospitalisation=hospitalisation,
        medecin=medecin,
        observations=observations,
    )

    if codes_cim10:
        _ajouter_diagnostics(prescription, codes_cim10)

    return prescription


def _ajouter_diagnostics(prescription: Prescription, codes: list[str]):
    for code in codes:
        try:
            diagnostic = DiagnosticCIM10.objects.get(code=code, actif=True)
        except DiagnosticCIM10.DoesNotExist:
            raise PrescriptionError(f'Code CIM-10 invalide : {code}.', code='cim10_invalide')
        PrescriptionDiagnostic.objects.get_or_create(
            prescription=prescription,
            code_cim10=diagnostic.code,
            defaults={'libelle': diagnostic.libelle},
        )


def ajouter_ligne(
    *,
    prescription: Prescription,
    medicament: str,
    posologie: str,
    duree_traitement: str = '',
    voie_administration: str = 'orale',
    instructions: str = '',
    ordre: int = 1,
) -> LignePrescription:
    if not prescription.est_modifiable:
        raise PrescriptionError(
            'Cette prescription est verrouillée.',
            code='prescription_verrouillee',
        )
    return LignePrescription.objects.create(
        prescription=prescription,
        medicament=medicament,
        posologie=posologie,
        duree_traitement=duree_traitement,
        voie_administration=voie_administration,
        instructions=instructions,
        ordre=ordre,
    )


@transaction.atomic
def valider_prescription(*, prescription: Prescription, medecin: User, version: int) -> Prescription:
    assert_medecin(medecin)
    presc = Prescription.objects.select_for_update().get(pk=prescription.pk)

    if presc.version != version:
        raise PrescriptionError('Conflit de version : rechargez et réessayez.', code='version_conflict')
    if presc.statut != StatutPrescription.BROUILLON:
        raise PrescriptionError('Cette prescription ne peut plus être validée.', code='prescription_verrouillee')
    if not presc.lignes.exists():
        raise PrescriptionError(
            'Ajoutez au moins un médicament avant validation.',
            code='prescription_vide',
        )
    if not presc.diagnostics.exists():
        raise PrescriptionError(
            'Associez au moins un diagnostic CIM-10 avant validation.',
            code='diagnostic_manquant',
        )

    get_hospitalisation_active(presc.hospitalisation_id)

    presc.statut = StatutPrescription.VALIDEE
    presc.validee_le = timezone.now()
    presc.validee_par = medecin
    presc.bump_version()
    presc.save(update_fields=['statut', 'validee_le', 'validee_par', 'version', 'updated_at'])
    return presc
