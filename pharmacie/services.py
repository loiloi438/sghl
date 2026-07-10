from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from accounts.models import Role, User
from hospitalisation.models import StatutHospitalisation
from pharmacie.models import (
    LigneDispensation,
    MedicamentStock,
    OrdreDispensation,
    StatutOrdreDispensation,
)
from prescriptions.models import Prescription, StatutPrescription


class PharmacieError(Exception):
    def __init__(self, message: str, code: str = 'error'):
        self.message = message
        self.code = code
        super().__init__(message)


def assert_pharmacien(user: User):
    if user.role not in {Role.ADMIN, Role.PHARMACIEN}:
        raise PharmacieError('Seul un pharmacien peut effectuer cette action.', code='acces_refuse')


def get_ordre(ordre_id) -> OrdreDispensation:
    try:
        return OrdreDispensation.objects.select_related(
            'prescription__hospitalisation__patient',
            'prescription__medecin',
            'pharmacien',
        ).prefetch_related(
            'lignes__medicament_stock',
            'lignes__ligne_prescription',
            'prescription__lignes',
        ).get(id=ordre_id)
    except OrdreDispensation.DoesNotExist:
        raise PharmacieError('Ordre de dispensation introuvable.', code='not_found')


def _verifier_hospitalisation_active(prescription: Prescription):
    if prescription.hospitalisation.statut != StatutHospitalisation.ACTIVE:
        raise PharmacieError(
            'L\'hospitalisation n\'est plus active.',
            code='hospitalisation_inactive',
        )


def trouver_medicament_stock(nom_medicament: str) -> MedicamentStock:
    nom = nom_medicament.strip()
    stock = MedicamentStock.objects.filter(
        actif=True,
    ).filter(
        Q(libelle__icontains=nom) | Q(code__iexact=nom),
    ).first()
    if stock is None:
        raise PharmacieError(
            f'Aucun stock trouvé pour « {nom_medicament} ».',
            code='medicament_introuvable',
        )
    return stock


def creer_ordre_dispensation(*, prescription: Prescription, pharmacien: User) -> OrdreDispensation:
    assert_pharmacien(pharmacien)
    if prescription.statut != StatutPrescription.VALIDEE:
        raise PharmacieError(
            'Seules les prescriptions validées peuvent être dispensées.',
            code='prescription_non_validee',
        )
    _verifier_hospitalisation_active(prescription)
    if OrdreDispensation.objects.filter(prescription_id=prescription.id).exists():
        raise PharmacieError(
            'Un ordre de dispensation existe déjà pour cette prescription.',
            code='ordre_existant',
        )
    if not prescription.lignes.exists():
        raise PharmacieError('Prescription sans médicament.', code='prescription_vide')

    ordre = OrdreDispensation.objects.create(prescription=prescription)
    for ligne_rx in prescription.lignes.all():
        stock = trouver_medicament_stock(ligne_rx.medicament)
        LigneDispensation.objects.create(
            ordre=ordre,
            ligne_prescription=ligne_rx,
            medicament_stock=stock,
            quantite=1,
        )
    return ordre


@transaction.atomic
def preparer_ordre(*, ordre: OrdreDispensation, pharmacien: User, version: int) -> OrdreDispensation:
    assert_pharmacien(pharmacien)
    o = OrdreDispensation.objects.select_for_update().prefetch_related(
        'lignes__medicament_stock',
    ).get(pk=ordre.pk)

    if o.version != version:
        raise PharmacieError('Conflit de version : rechargez et réessayez.', code='version_conflict')
    if o.statut != StatutOrdreDispensation.EN_ATTENTE:
        raise PharmacieError('Cet ordre ne peut plus être préparé.', code='statut_invalide')
    _verifier_hospitalisation_active(o.prescription)

    for ligne in o.lignes.all():
        stock = ligne.medicament_stock
        if stock.quantite_stock < ligne.quantite:
            raise PharmacieError(
                f'Stock insuffisant pour {stock.libelle} '
                f'(disponible : {stock.quantite_stock}, requis : {ligne.quantite}).',
                code='stock_insuffisant',
            )

    o.statut = StatutOrdreDispensation.PREPARE
    o.prepare_le = timezone.now()
    o.bump_version()
    o.save(update_fields=['statut', 'prepare_le', 'version', 'updated_at'])
    return o


@transaction.atomic
def dispenser_ordre(*, ordre: OrdreDispensation, pharmacien: User, version: int) -> OrdreDispensation:
    assert_pharmacien(pharmacien)
    o = OrdreDispensation.objects.select_for_update().prefetch_related(
        'lignes__medicament_stock',
    ).get(pk=ordre.pk)

    if o.version != version:
        raise PharmacieError('Conflit de version : rechargez et réessayez.', code='version_conflict')
    if o.statut not in {StatutOrdreDispensation.EN_ATTENTE, StatutOrdreDispensation.PREPARE}:
        raise PharmacieError('Cet ordre ne peut plus être dispensé.', code='statut_invalide')
    _verifier_hospitalisation_active(o.prescription)

    stock_ids = [ligne.medicament_stock_id for ligne in o.lignes.all()]
    stocks = {
        s.id: s
        for s in MedicamentStock.objects.select_for_update().filter(id__in=stock_ids)
    }

    for ligne in o.lignes.all():
        stock = stocks[ligne.medicament_stock_id]
        if stock.est_perime:
            raise PharmacieError(
                f'Le lot de {stock.libelle} est périmé (péremption : {stock.date_peremption}).',
                code='medicament_perime',
            )
        if stock.quantite_stock < ligne.quantite:
            raise PharmacieError(
                f'Stock insuffisant pour {stock.libelle}.',
                code='stock_insuffisant',
            )

    for ligne in o.lignes.all():
        stock = stocks[ligne.medicament_stock_id]
        stock.quantite_stock -= ligne.quantite
        stock.save(update_fields=['quantite_stock', 'updated_at'])

    o.statut = StatutOrdreDispensation.DISPENSE
    o.pharmacien = pharmacien
    o.dispense_le = timezone.now()
    o.bump_version()
    o.save(update_fields=['statut', 'pharmacien', 'dispense_le', 'version', 'updated_at'])
    return o


@transaction.atomic
def approvisionner_stock(
    *,
    medicament: MedicamentStock,
    quantite: int,
    pharmacien: User,
) -> MedicamentStock:
    assert_pharmacien(pharmacien)
    if quantite <= 0:
        raise PharmacieError('La quantité doit être positive.', code='quantite_invalide')

    med = MedicamentStock.objects.select_for_update().get(pk=medicament.pk)
    med.quantite_stock += quantite
    med.save(update_fields=['quantite_stock', 'updated_at'])
    return med
