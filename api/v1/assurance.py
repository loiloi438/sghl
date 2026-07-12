from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID

from django.db.models import Q, Sum
from ninja import Router, Schema
from ninja.errors import HttpError

from accounts.models import Role, User
from api.v1.auth_backend import JWTAuth
from assurance.models import AffiliationPatient, OrganismeAssurance
from audit.services import get_client_ip, log_audit
from patients.models import Patient

router = Router(tags=['Assurance'])
jwt_auth = JWTAuth()

ROLES = {Role.ADMIN, Role.COMPTABLE, Role.SECRETAIRE}


def _check(user: User):
    if user.role not in ROLES:
        raise HttpError(403, 'Accès refusé.')


class OrganismeOut(Schema):
    id: UUID
    code: str
    nom: str
    assurance: str
    coverage: int
    conventions: int
    active: bool
    contact_email: str
    contact_telephone: str


class OrganismeIn(Schema):
    code: str
    nom: str
    taux_couverture: int = 80
    actif: bool = True
    contact_email: str = ''
    contact_telephone: str = ''
    notes: str = ''


class OrganismeUpdateIn(Schema):
    nom: Optional[str] = None
    taux_couverture: Optional[int] = None
    actif: Optional[bool] = None
    contact_email: Optional[str] = None
    contact_telephone: Optional[str] = None
    notes: Optional[str] = None


class StatsAssuranceOut(Schema):
    conventions_actives: int
    tiers_payants: int
    taux_remboursement_moyen: int


class AffiliationOut(Schema):
    id: UUID
    patient_id: UUID
    patient_nom: str
    organisme_id: UUID
    organisme_nom: str
    numero_adherent: str
    date_debut: date
    date_fin: Optional[date]
    actif: bool


class AffiliationIn(Schema):
    patient_id: UUID
    organisme_id: UUID
    numero_adherent: str = ''
    date_debut: date
    date_fin: Optional[date] = None
    actif: bool = True


class AffiliationUpdateIn(Schema):
    numero_adherent: Optional[str] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    actif: Optional[bool] = None


def _serialize(org: OrganismeAssurance) -> OrganismeOut:
    return OrganismeOut(
        id=org.id,
        code=org.code,
        nom=org.nom,
        assurance=org.nom,
        coverage=org.taux_couverture,
        conventions=org.affiliations.filter(actif=True).count(),
        active=org.actif,
        contact_email=org.contact_email,
        contact_telephone=org.contact_telephone,
    )


def _serialize_affiliation(aff: AffiliationPatient) -> AffiliationOut:
    patient = aff.patient
    return AffiliationOut(
        id=aff.id,
        patient_id=patient.id,
        patient_nom=f'{patient.nom} {patient.prenom}'.strip(),
        organisme_id=aff.organisme_id,
        organisme_nom=aff.organisme.nom,
        numero_adherent=aff.numero_adherent,
        date_debut=aff.date_debut,
        date_fin=aff.date_fin,
        actif=aff.actif,
    )


@router.get('/assurance/stats/', response=StatsAssuranceOut, auth=jwt_auth)
def stats_assurance(request):
    _check(request.auth)
    orgs = OrganismeAssurance.objects.all()
    actifs = orgs.filter(actif=True)
    avg = actifs.aggregate(m=Sum('taux_couverture'))['m'] or 0
    count = actifs.count() or 1
    return StatsAssuranceOut(
        conventions_actives=actifs.count(),
        tiers_payants=orgs.count(),
        taux_remboursement_moyen=round(avg / count),
    )


@router.get('/assurance/organismes/', response=list[OrganismeOut], auth=jwt_auth)
def list_organismes(request, search: str | None = None, actif: bool | None = None):
    _check(request.auth)
    qs = OrganismeAssurance.objects.all()
    if search:
        qs = qs.filter(Q(nom__icontains=search) | Q(code__icontains=search))
    if actif is not None:
        qs = qs.filter(actif=actif)
    return [_serialize(o) for o in qs]


@router.post('/assurance/organismes/', response=OrganismeOut, auth=jwt_auth)
def create_organisme(request, payload: OrganismeIn):
    _check(request.auth)
    org = OrganismeAssurance.objects.create(**payload.dict())
    log_audit(
        user=request.auth,
        action='create',
        model_name='OrganismeAssurance',
        object_id=org.id,
        new_value=payload.dict(),
        ip_address=get_client_ip(request),
    )
    return _serialize(org)


@router.patch('/assurance/organismes/{org_id}/', response=OrganismeOut, auth=jwt_auth)
def update_organisme(request, org_id: UUID, payload: OrganismeUpdateIn):
    _check(request.auth)
    try:
        org = OrganismeAssurance.objects.get(id=org_id)
    except OrganismeAssurance.DoesNotExist:
        raise HttpError(404, 'Organisme introuvable.')
    for key, value in payload.dict(exclude_none=True).items():
        setattr(org, key, value)
    org.save()
    return _serialize(org)


@router.delete('/assurance/organismes/{org_id}/', auth=jwt_auth)
def delete_organisme(request, org_id: UUID):
    _check(request.auth)
    try:
        org = OrganismeAssurance.objects.get(id=org_id)
    except OrganismeAssurance.DoesNotExist:
        raise HttpError(404, 'Organisme introuvable.')
    org.delete()
    log_audit(
        user=request.auth,
        action='delete',
        model_name='OrganismeAssurance',
        object_id=org_id,
        ip_address=get_client_ip(request),
    )
    return {'detail': 'Organisme supprimé.'}


@router.get('/assurance/affiliations/', response=list[AffiliationOut], auth=jwt_auth)
def list_affiliations(
    request,
    patient_id: UUID | None = None,
    organisme_id: UUID | None = None,
    actif: bool | None = None,
):
    _check(request.auth)
    qs = AffiliationPatient.objects.select_related('patient', 'organisme')
    if patient_id:
        qs = qs.filter(patient_id=patient_id)
    if organisme_id:
        qs = qs.filter(organisme_id=organisme_id)
    if actif is not None:
        qs = qs.filter(actif=actif)
    return [_serialize_affiliation(a) for a in qs]


@router.post('/assurance/affiliations/', response=AffiliationOut, auth=jwt_auth)
def create_affiliation(request, payload: AffiliationIn):
    _check(request.auth)
    try:
        patient = Patient.objects.get(id=payload.patient_id)
        organisme = OrganismeAssurance.objects.get(id=payload.organisme_id)
    except Patient.DoesNotExist:
        raise HttpError(404, 'Patient introuvable.')
    except OrganismeAssurance.DoesNotExist:
        raise HttpError(404, 'Organisme introuvable.')
    aff = AffiliationPatient.objects.create(
        patient=patient,
        organisme=organisme,
        numero_adherent=payload.numero_adherent,
        date_debut=payload.date_debut,
        date_fin=payload.date_fin,
        actif=payload.actif,
    )
    log_audit(
        user=request.auth,
        action='create',
        model_name='AffiliationPatient',
        object_id=aff.id,
        new_value=payload.dict(),
        ip_address=get_client_ip(request),
    )
    return _serialize_affiliation(aff)


@router.patch('/assurance/affiliations/{aff_id}/', response=AffiliationOut, auth=jwt_auth)
def update_affiliation(request, aff_id: UUID, payload: AffiliationUpdateIn):
    _check(request.auth)
    try:
        aff = AffiliationPatient.objects.select_related('patient', 'organisme').get(id=aff_id)
    except AffiliationPatient.DoesNotExist:
        raise HttpError(404, 'Affiliation introuvable.')
    for key, value in payload.dict(exclude_none=True).items():
        setattr(aff, key, value)
    aff.save()
    log_audit(
        user=request.auth,
        action='update',
        model_name='AffiliationPatient',
        object_id=aff.id,
        new_value=payload.dict(exclude_none=True),
        ip_address=get_client_ip(request),
    )
    return _serialize_affiliation(aff)


@router.delete('/assurance/affiliations/{aff_id}/', auth=jwt_auth)
def delete_affiliation(request, aff_id: UUID):
    _check(request.auth)
    try:
        aff = AffiliationPatient.objects.get(id=aff_id)
    except AffiliationPatient.DoesNotExist:
        raise HttpError(404, 'Affiliation introuvable.')
    aff.delete()
    log_audit(
        user=request.auth,
        action='delete',
        model_name='AffiliationPatient',
        object_id=aff_id,
        ip_address=get_client_ip(request),
    )
    return {'detail': 'Affiliation supprimée.'}
