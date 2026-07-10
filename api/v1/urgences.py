from datetime import datetime
from typing import Optional
from uuid import UUID

from django.db.models import Q
from django.utils import timezone
from ninja import Router, Schema
from ninja.errors import HttpError

from accounts.models import Role, User
from api.v1.auth_backend import JWTAuth
from audit.services import get_client_ip, log_audit
from patients.models import Patient
from urgences.models import PassageUrgence, StatutPassageUrgence
from urgences.services import UrgencesError, classer_triage, creer_passage_urgence, demarrer_triage

router = Router(tags=['Urgences'])
jwt_auth = JWTAuth()

ROLES = {Role.ADMIN, Role.MEDECIN, Role.INFIRMIER}


def _check(user: User):
    if user.role not in ROLES:
        raise HttpError(403, 'Accès refusé.')


def _handle_error(exc: UrgencesError):
    status_map = {'version_conflict': 409, 'acces_refuse': 403, 'triage_invalide': 400}
    raise HttpError(status_map.get(exc.code, 400), exc.message)


class PassageOut(Schema):
    id: UUID
    name: str
    age: Optional[int]
    gender: str
    complaint: str
    triage: str
    triage_label: str
    statut: str
    arrivalTime: str
    version: int


class StatsUrgencesOut(Schema):
    waiting_triage: int
    in_treatment: int
    avg_wait_minutes: int


class PassageIn(Schema):
    patient_id: Optional[UUID] = None
    nom_libre: str = ''
    age: Optional[int] = None
    sexe: str = ''
    motif: str
    niveau_triage: str = 'orange'


class VersionIn(Schema):
    version: int


class TriageIn(Schema):
    version: int
    niveau_triage: str


def _serialize(p: PassageUrgence) -> PassageOut:
    arrival = timezone.localtime(p.heure_arrivee)
    age = p.age
    gender = p.sexe
    if p.patient:
        from datetime import date
        today = date.today()
        age = age or (
            today.year - p.patient.date_naissance.year
            - ((today.month, today.day) < (p.patient.date_naissance.month, p.patient.date_naissance.day))
        )
        gender = gender or p.patient.sexe
    return PassageOut(
        id=p.id,
        name=p.display_name,
        age=age,
        gender=gender or '—',
        complaint=p.motif,
        triage=p.niveau_triage,
        triage_label=p.get_niveau_triage_display(),
        statut=p.statut,
        arrivalTime=arrival.strftime('%H:%M'),
        version=p.version,
    )


@router.get('/urgences/stats/', response=StatsUrgencesOut, auth=jwt_auth)
def stats_urgences(request):
    _check(request.auth)
    actifs = PassageUrgence.objects.exclude(statut__in={StatutPassageUrgence.SORTI, StatutPassageUrgence.ADMIS})
    waiting = actifs.filter(statut=StatutPassageUrgence.ATTENTE).count()
    in_treatment = actifs.filter(statut__in={StatutPassageUrgence.TRIAGE, StatutPassageUrgence.SOINS}).count()
    now = timezone.now()
    waits = []
    for p in actifs.filter(heure_triage__isnull=False):
        waits.append(int((now - p.heure_arrivee).total_seconds() // 60))
    avg = round(sum(waits) / len(waits)) if waits else 15
    return StatsUrgencesOut(waiting_triage=waiting, in_treatment=in_treatment, avg_wait_minutes=avg)


@router.get('/urgences/passages/', response=list[PassageOut], auth=jwt_auth)
def list_passages(request, triage: str | None = None, search: str | None = None):
    _check(request.auth)
    qs = PassageUrgence.objects.select_related('patient').exclude(
        statut__in={StatutPassageUrgence.SORTI, StatutPassageUrgence.ADMIS},
    )
    if triage:
        qs = qs.filter(niveau_triage=triage)
    if search:
        qs = qs.filter(
            Q(nom_libre__icontains=search)
            | Q(patient__nom__icontains=search)
            | Q(patient__prenom__icontains=search)
        )
    return [_serialize(p) for p in qs]


@router.post('/urgences/passages/', response=PassageOut, auth=jwt_auth)
def create_passage(request, payload: PassageIn):
    _check(request.auth)
    patient = None
    if payload.patient_id:
        try:
            patient = Patient.objects.get(id=payload.patient_id)
        except Patient.DoesNotExist:
            raise HttpError(404, 'Patient introuvable.')
    passage = creer_passage_urgence(
        patient=patient,
        nom_libre=payload.nom_libre,
        age=payload.age,
        sexe=payload.sexe,
        motif=payload.motif,
        niveau_triage=payload.niveau_triage,
    )
    log_audit(
        user=request.auth,
        action='create',
        model_name='PassageUrgence',
        object_id=passage.id,
        new_value=payload.dict(),
        ip_address=get_client_ip(request),
    )
    return _serialize(passage)


@router.post('/urgences/passages/{passage_id}/triage/', response=PassageOut, auth=jwt_auth)
def start_triage(request, passage_id: UUID, payload: VersionIn):
    _check(request.auth)
    try:
        passage = PassageUrgence.objects.select_related('patient').get(id=passage_id)
    except PassageUrgence.DoesNotExist:
        raise HttpError(404, 'Passage introuvable.')
    try:
        passage = demarrer_triage(passage=passage, medecin=request.auth, version=payload.version)
    except UrgencesError as exc:
        _handle_error(exc)
    return _serialize(passage)


@router.post('/urgences/passages/{passage_id}/classer/', response=PassageOut, auth=jwt_auth)
def classify_triage(request, passage_id: UUID, payload: TriageIn):
    _check(request.auth)
    try:
        passage = PassageUrgence.objects.select_related('patient').get(id=passage_id)
    except PassageUrgence.DoesNotExist:
        raise HttpError(404, 'Passage introuvable.')
    try:
        passage = classer_triage(
            passage=passage,
            niveau=payload.niveau_triage,
            version=payload.version,
        )
    except UrgencesError as exc:
        _handle_error(exc)
    return _serialize(passage)
