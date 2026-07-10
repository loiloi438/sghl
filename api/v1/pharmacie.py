from datetime import date, datetime, timedelta
from typing import Optional
from uuid import UUID

from django.db.models import F, Q
from ninja import Router, Schema
from ninja.errors import HttpError
from ninja.pagination import paginate

from accounts.models import Role, User
from api.v1.auth_backend import JWTAuth
from audit.services import get_client_ip, log_audit
from hospitalisation.models import StatutHospitalisation
from pharmacie.models import MedicamentStock, OrdreDispensation
from pharmacie.services import (
    PharmacieError,
    approvisionner_stock,
    creer_ordre_dispensation,
    dispenser_ordre,
    get_ordre,
    preparer_ordre,
)
from prescriptions.models import Prescription, StatutPrescription

router = Router(tags=['Pharmacie'])
jwt_auth = JWTAuth()

ROLES_LECTURE = {Role.ADMIN, Role.MEDECIN, Role.INFIRMIER, Role.PHARMACIEN, Role.BIOLOGISTE}
ROLES_PHARMACIE = {Role.ADMIN, Role.PHARMACIEN}


def _check_read(user: User):
    if user.role not in ROLES_LECTURE:
        raise HttpError(403, 'Accès refusé.')


def _check_pharmacie(user: User):
    if user.role not in ROLES_PHARMACIE:
        raise HttpError(403, 'Accès refusé.')


def _handle_error(exc: PharmacieError):
    status_map = {
        'not_found': 404,
        'version_conflict': 409,
        'acces_refuse': 403,
        'ordre_verrouille': 403,
        'stock_insuffisant': 400,
    }
    raise HttpError(status_map.get(exc.code, 400), exc.message)


class MedicamentStockOut(Schema):
    id: UUID
    code: str
    libelle: str
    forme: str
    quantite_stock: int
    unite: str
    seuil_alerte: int
    stock_bas: bool
    date_peremption: Optional[date] = None
    est_perime: bool = False
    peremption_proche: bool = False


class ApprovisionnementIn(Schema):
    quantite: int


class LigneDispensationOut(Schema):
    id: UUID
    medicament: str
    code_stock: str
    posologie: str
    quantite: int


class OrdreDispensationOut(Schema):
    id: UUID
    prescription_id: UUID
    patient_id: UUID
    numero_dossier: str
    patient_nom: str
    medecin_nom: str
    statut: str
    lignes: list[LigneDispensationOut]
    pharmacien_nom: Optional[str]
    prepare_le: Optional[datetime]
    dispense_le: Optional[datetime]
    version: int
    est_verrouille: bool
    created_at: datetime


class PrescriptionADispenserOut(Schema):
    prescription_id: UUID
    patient_id: UUID
    numero_dossier: str
    patient_nom: str
    medecin_nom: str
    validee_le: Optional[datetime]
    medicaments: list[str]
    deja_en_pharmacie: bool


class VersionIn(Schema):
    version: int


def _user_nom(user: User | None) -> Optional[str]:
    if user is None:
        return None
    return f'{user.first_name} {user.last_name}'.strip() or user.username


def _serialize_stock(m: MedicamentStock) -> MedicamentStockOut:
    return MedicamentStockOut(
        id=m.id,
        code=m.code,
        libelle=m.libelle,
        forme=m.forme,
        quantite_stock=m.quantite_stock,
        unite=m.unite,
        seuil_alerte=m.seuil_alerte,
        stock_bas=m.stock_bas,
        date_peremption=m.date_peremption,
        est_perime=m.est_perime,
        peremption_proche=m.peremption_proche,
    )


def _serialize_ordre(o: OrdreDispensation) -> OrdreDispensationOut:
    prescription = o.prescription
    patient = prescription.hospitalisation.patient
    medecin = prescription.medecin
    return OrdreDispensationOut(
        id=o.id,
        prescription_id=prescription.id,
        patient_id=patient.id,
        numero_dossier=patient.numero_dossier,
        patient_nom=f'{patient.prenom} {patient.nom}',
        medecin_nom=_user_nom(medecin) or medecin.username,
        statut=o.statut,
        lignes=[
            LigneDispensationOut(
                id=l.id,
                medicament=l.medicament_stock.libelle,
                code_stock=l.medicament_stock.code,
                posologie=l.ligne_prescription.posologie,
                quantite=l.quantite,
            )
            for l in o.lignes.all()
        ],
        pharmacien_nom=_user_nom(o.pharmacien),
        prepare_le=o.prepare_le,
        dispense_le=o.dispense_le,
        version=o.version,
        est_verrouille=o.est_verrouille,
        created_at=o.created_at,
    )


@router.get('/pharmacie/stock/', response=list[MedicamentStockOut], auth=jwt_auth)
@paginate
def list_stock(request, search: str = '', stock_bas: Optional[bool] = None):
    _check_read(request.auth)
    qs = MedicamentStock.objects.filter(actif=True)
    if search:
        qs = qs.filter(Q(code__icontains=search) | Q(libelle__icontains=search))
    if stock_bas is True:
        qs = qs.filter(quantite_stock__lte=F('seuil_alerte'))
    return [_serialize_stock(m) for m in qs]


@router.get('/pharmacie/stock/alertes/', response=list[MedicamentStockOut], auth=jwt_auth)
def alertes_stock(request):
    _check_read(request.auth)
    meds = [m for m in MedicamentStock.objects.filter(actif=True) if m.stock_bas]
    return [_serialize_stock(m) for m in meds]


@router.get('/pharmacie/stock/peremption/', response=list[MedicamentStockOut], auth=jwt_auth)
def alertes_peremption(request):
    """Lots périmés ou péremption dans les 30 jours (CDC)."""
    _check_read(request.auth)
    limite = date.today() + timedelta(days=30)
    qs = MedicamentStock.objects.filter(
        actif=True,
        date_peremption__isnull=False,
        date_peremption__lte=limite,
    ).order_by('date_peremption')
    return [_serialize_stock(m) for m in qs]


@router.post('/pharmacie/stock/{medicament_id}/approvisionner/', response=MedicamentStockOut, auth=jwt_auth)
def approvisionner(request, medicament_id: UUID, payload: ApprovisionnementIn):
    _check_pharmacie(request.auth)
    try:
        medicament = MedicamentStock.objects.get(id=medicament_id, actif=True)
        medicament = approvisionner_stock(
            medicament=medicament,
            quantite=payload.quantite,
            pharmacien=request.auth,
        )
    except MedicamentStock.DoesNotExist:
        raise HttpError(404, 'Médicament introuvable.')
    except PharmacieError as exc:
        _handle_error(exc)

    data = _serialize_stock(medicament)
    log_audit(
        user=request.auth,
        action='UPDATE',
        model_name='MedicamentStock',
        object_id=medicament.id,
        new_value={**data.model_dump(), 'event': 'approvisionnement', 'quantite': payload.quantite},
        ip_address=get_client_ip(request),
    )
    return data


@router.get('/pharmacie/prescriptions-a-dispenser/', response=list[PrescriptionADispenserOut], auth=jwt_auth)
@paginate
def prescriptions_a_dispenser(request):
    _check_pharmacie(request.auth)
    qs = Prescription.objects.filter(
        statut=StatutPrescription.VALIDEE,
        hospitalisation__statut=StatutHospitalisation.ACTIVE,
    ).select_related(
        'hospitalisation__patient',
        'medecin',
    ).prefetch_related('lignes').order_by('-validee_le')

    results = []
    for p in qs:
        patient = p.hospitalisation.patient
        medecin = p.medecin
        deja = OrdreDispensation.objects.filter(prescription_id=p.id).exists()
        results.append(
            PrescriptionADispenserOut(
                prescription_id=p.id,
                patient_id=patient.id,
                numero_dossier=patient.numero_dossier,
                patient_nom=f'{patient.prenom} {patient.nom}',
                medecin_nom=_user_nom(medecin) or medecin.username,
                validee_le=p.validee_le,
                medicaments=[f'{l.medicament} ({l.posologie})' for l in p.lignes.all()],
                deja_en_pharmacie=deja,
            )
        )
    return results


@router.get('/pharmacie/ordres-dispensation/', response=list[OrdreDispensationOut], auth=jwt_auth)
@paginate
def list_ordres(request, statut: Optional[str] = None):
    _check_read(request.auth)
    qs = OrdreDispensation.objects.select_related(
        'prescription__hospitalisation__patient',
        'prescription__medecin',
        'pharmacien',
    ).prefetch_related('lignes__medicament_stock', 'lignes__ligne_prescription')
    if statut:
        qs = qs.filter(statut=statut)
    return [_serialize_ordre(o) for o in qs]


@router.post(
    '/prescriptions/{prescription_id}/ordre-dispensation/',
    response=OrdreDispensationOut,
    auth=jwt_auth,
)
def create_ordre(request, prescription_id: UUID):
    _check_pharmacie(request.auth)
    try:
        prescription = Prescription.objects.select_related(
            'hospitalisation__patient',
            'medecin',
        ).prefetch_related('lignes').get(id=prescription_id)
        ordre = creer_ordre_dispensation(
            prescription=prescription,
            pharmacien=request.auth,
        )
    except Prescription.DoesNotExist:
        raise HttpError(404, 'Prescription introuvable.')
    except PharmacieError as exc:
        _handle_error(exc)

    ordre = get_ordre(ordre.id)
    data = _serialize_ordre(ordre)
    log_audit(
        user=request.auth,
        action='CREATE',
        model_name='OrdreDispensation',
        object_id=ordre.id,
        new_value=data.model_dump(),
        ip_address=get_client_ip(request),
    )
    return data


@router.get('/pharmacie/ordres-dispensation/{ordre_id}/', response=OrdreDispensationOut, auth=jwt_auth)
def get_ordre_detail(request, ordre_id: UUID):
    _check_read(request.auth)
    try:
        ordre = get_ordre(ordre_id)
    except PharmacieError as exc:
        _handle_error(exc)
    return _serialize_ordre(ordre)


@router.post('/pharmacie/ordres-dispensation/{ordre_id}/preparer/', response=OrdreDispensationOut, auth=jwt_auth)
def preparer_ordre_endpoint(request, ordre_id: UUID, payload: VersionIn):
    _check_pharmacie(request.auth)
    try:
        ordre = get_ordre(ordre_id)
        ordre = preparer_ordre(ordre=ordre, pharmacien=request.auth, version=payload.version)
    except PharmacieError as exc:
        _handle_error(exc)

    ordre = get_ordre(ordre.id)
    data = _serialize_ordre(ordre)
    log_audit(
        user=request.auth,
        action='UPDATE',
        model_name='OrdreDispensation',
        object_id=ordre.id,
        new_value={**data.model_dump(), 'event': 'preparation'},
        ip_address=get_client_ip(request),
    )
    return data


@router.post('/pharmacie/ordres-dispensation/{ordre_id}/dispenser/', response=OrdreDispensationOut, auth=jwt_auth)
def dispenser_ordre_endpoint(request, ordre_id: UUID, payload: VersionIn):
    _check_pharmacie(request.auth)
    try:
        ordre = get_ordre(ordre_id)
        ordre = dispenser_ordre(ordre=ordre, pharmacien=request.auth, version=payload.version)
    except PharmacieError as exc:
        _handle_error(exc)

    ordre = get_ordre(ordre.id)
    data = _serialize_ordre(ordre)
    log_audit(
        user=request.auth,
        action='UPDATE',
        model_name='OrdreDispensation',
        object_id=ordre.id,
        new_value={**data.model_dump(), 'event': 'dispensation'},
        ip_address=get_client_ip(request),
    )
    return data
