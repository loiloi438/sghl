from datetime import date as date_cls
from datetime import datetime, time, timedelta
from typing import Optional
from uuid import UUID

from django.utils import timezone
import secrets

from django.conf import settings
from ninja import Router, Schema
from ninja.errors import HttpError
from ninja.pagination import paginate

from accounts.models import Role, User
from api.v1.auth_backend import JWTAuth
from audit.services import get_client_ip, log_audit
from patients.models import Patient
from rendezvous.models import RendezVous, StatutRendezVous, TypeConsultation
from rendezvous.services import (
    RendezVousError,
    annuler_rendez_vous,
    compter_rdv_jour,
    confirmer_rendez_vous,
    creer_rendez_vous,
    get_rendez_vous,
    marquer_absent,
    modifier_rendez_vous,
    terminer_rendez_vous,
)

router = Router(tags=['Rendez-vous'])
jwt_auth = JWTAuth()

ROLES_LECTURE = {Role.ADMIN, Role.MEDECIN, Role.INFIRMIER, Role.COMPTABLE}
ROLES_GESTION = {Role.ADMIN, Role.MEDECIN, Role.INFIRMIER}


def _handle_error(exc: RendezVousError):
    status_map = {
        'not_found': 404,
        'version_conflict': 409,
        'acces_refuse': 403,
        'creneau_indisponible': 409,
        'date_invalide': 400,
        'statut_invalide': 400,
        'medecin_invalide': 400,
        'aucun_changement': 400,
    }
    raise HttpError(status_map.get(exc.code, 400), exc.message)


def _check_lecture(user: User):
    if user.role not in ROLES_LECTURE:
        raise HttpError(403, 'Accès refusé.')


def _check_gestion(user: User):
    if user.role not in ROLES_GESTION:
        raise HttpError(403, 'Accès refusé.')


class MedecinOut(Schema):
    id: int
    nom: str


class RendezVousOut(Schema):
    id: UUID
    patient_id: UUID
    numero_dossier: str
    patient_nom: str
    medecin_id: int
    medecin_nom: str
    date_heure: datetime
    duree_minutes: int
    motif: str
    statut: str
    notes: str
    type_consultation: str
    lien_visio: str
    version: int
    created_at: datetime


class RendezVousIn(Schema):
    patient_id: UUID
    medecin_id: int
    date_heure: datetime
    motif: str
    duree_minutes: int = 30
    notes: str = ''
    type_consultation: str = TypeConsultation.PRESENTIEL


class VersionIn(Schema):
    version: int


class AnnulationIn(Schema):
    version: int
    motif_annulation: str = ''


class ModifierRdvIn(Schema):
    version: int
    date_heure: Optional[datetime] = None
    medecin_id: Optional[int] = None
    motif: Optional[str] = None
    notes: Optional[str] = None
    duree_minutes: Optional[int] = None
    motif_modification: str = ''


class StatsRdvOut(Schema):
    rdv_aujourdhui: int
    rdv_planifies: int


class JourSemaineOut(Schema):
    date: str
    count: int


def _serialize_rdv(r: RendezVous) -> RendezVousOut:
    patient = r.patient
    medecin = r.medecin
    medecin_nom = f'{medecin.first_name} {medecin.last_name}'.strip() or medecin.username
    return RendezVousOut(
        id=r.id,
        patient_id=patient.id,
        numero_dossier=patient.numero_dossier,
        patient_nom=f'{patient.prenom} {patient.nom}',
        medecin_id=medecin.id,
        medecin_nom=medecin_nom,
        date_heure=r.date_heure,
        duree_minutes=r.duree_minutes,
        motif=r.motif,
        statut=r.statut,
        notes=r.notes,
        type_consultation=r.type_consultation,
        lien_visio=r.lien_visio or '',
        version=r.version,
        created_at=r.created_at,
    )


def _filter_date(qs, date_str: Optional[str]):
    if not date_str:
        return qs
    try:
        jour = date_cls.fromisoformat(date_str)
    except ValueError:
        raise HttpError(400, 'Format de date invalide (YYYY-MM-DD).')
    tz = timezone.get_current_timezone()
    debut = timezone.make_aware(datetime.combine(jour, time.min), tz)
    fin = debut + timedelta(days=1)
    return qs.filter(date_heure__gte=debut, date_heure__lt=fin)


def _monday_of(anchor: date_cls) -> date_cls:
    return anchor - timedelta(days=anchor.weekday())


def _rdv_queryset_for_user(user: User):
    qs = RendezVous.objects.all()
    if user.role == Role.MEDECIN:
        qs = qs.filter(medecin=user)
    return qs


@router.get('/rendez-vous/semaine/', response=list[JourSemaineOut], auth=jwt_auth)
def semaine_rendez_vous(request, date: Optional[str] = None):
    _check_lecture(request.auth)
    if date:
        try:
            anchor = date_cls.fromisoformat(date)
        except ValueError:
            raise HttpError(400, 'Format de date invalide (YYYY-MM-DD).')
    else:
        anchor = timezone.localdate()
    monday = _monday_of(anchor)
    tz = timezone.get_current_timezone()
    qs = _rdv_queryset_for_user(request.auth)
    jours = []
    for offset in range(7):
        jour = monday + timedelta(days=offset)
        debut = timezone.make_aware(datetime.combine(jour, time.min), tz)
        fin = debut + timedelta(days=1)
        count = qs.filter(date_heure__gte=debut, date_heure__lt=fin).count()
        jours.append(JourSemaineOut(date=jour.isoformat(), count=count))
    return jours


@router.get('/rendez-vous/stats/', response=StatsRdvOut, auth=jwt_auth)
def stats_rendez_vous(request):
    _check_lecture(request.auth)
    return StatsRdvOut(
        rdv_aujourdhui=compter_rdv_jour(),
        rdv_planifies=RendezVous.objects.filter(
            statut__in={StatutRendezVous.PLANIFIE, StatutRendezVous.CONFIRME},
            date_heure__gte=timezone.now(),
        ).count(),
    )


@router.get('/rendez-vous/medecins/', response=list[MedecinOut], auth=jwt_auth)
def list_medecins(request):
    _check_gestion(request.auth)
    return [
        MedecinOut(
            id=u.id,
            nom=f'{u.first_name} {u.last_name}'.strip() or u.username,
        )
        for u in User.objects.filter(role=Role.MEDECIN, is_active=True).order_by('last_name')
    ]


@router.get('/rendez-vous/', response=list[RendezVousOut], auth=jwt_auth)
@paginate
def list_rendez_vous(
    request,
    date: Optional[str] = None,
    statut: Optional[str] = None,
    medecin_id: Optional[int] = None,
):
    _check_lecture(request.auth)
    qs = RendezVous.objects.select_related('patient', 'medecin').order_by('date_heure')
    qs = _filter_date(qs, date)
    if statut:
        qs = qs.filter(statut=statut)
    if medecin_id:
        qs = qs.filter(medecin_id=medecin_id)
    if request.auth.role == Role.MEDECIN:
        qs = qs.filter(medecin=request.auth)
    return [_serialize_rdv(r) for r in qs]


@router.get('/rendez-vous/{rdv_id}/', response=RendezVousOut, auth=jwt_auth)
def detail_rendez_vous(request, rdv_id: UUID):
    _check_lecture(request.auth)
    try:
        rdv = get_rendez_vous(rdv_id)
    except RendezVousError as exc:
        _handle_error(exc)
    if request.auth.role == Role.MEDECIN and rdv.medecin_id != request.auth.id:
        raise HttpError(403, 'Accès refusé.')
    return _serialize_rdv(rdv)


@router.post('/rendez-vous/', response=RendezVousOut, auth=jwt_auth)
def creer_rendez_vous_endpoint(request, payload: RendezVousIn):
    _check_gestion(request.auth)
    try:
        patient = Patient.objects.get(id=payload.patient_id)
        medecin = User.objects.get(id=payload.medecin_id, role=Role.MEDECIN)
        rdv = creer_rendez_vous(
            patient=patient,
            medecin=medecin,
            date_heure=payload.date_heure,
            motif=payload.motif,
            auteur=request.auth,
            duree_minutes=payload.duree_minutes,
            notes=payload.notes,
            type_consultation=payload.type_consultation,
        )
        if payload.type_consultation == TypeConsultation.TELECONSULTATION:
            base = getattr(settings, 'SGHL_FRONTEND_URL', 'http://localhost:5173')
            token = secrets.token_urlsafe(16)
            rdv.lien_visio = f'{base}/visio/{token}'
            rdv.save(update_fields=['lien_visio', 'updated_at'])
    except Patient.DoesNotExist:
        raise HttpError(404, 'Patient introuvable.')
    except User.DoesNotExist:
        raise HttpError(404, 'Médecin introuvable.')
    except RendezVousError as exc:
        _handle_error(exc)

    rdv = get_rendez_vous(rdv.id)
    data = _serialize_rdv(rdv)
    log_audit(
        user=request.auth,
        action='CREATE',
        model_name='RendezVous',
        object_id=rdv.id,
        new_value=data.model_dump(mode='json'),
        ip_address=get_client_ip(request),
    )
    return data


@router.post('/rendez-vous/{rdv_id}/confirmer/', response=RendezVousOut, auth=jwt_auth)
def confirmer_endpoint(request, rdv_id: UUID, payload: VersionIn):
    _check_gestion(request.auth)
    try:
        rdv = get_rendez_vous(rdv_id)
        rdv = confirmer_rendez_vous(rdv=rdv, auteur=request.auth, version=payload.version)
    except RendezVousError as exc:
        _handle_error(exc)
    return _serialize_rdv(get_rendez_vous(rdv.id))


@router.post('/rendez-vous/{rdv_id}/modifier/', response=RendezVousOut, auth=jwt_auth)
def modifier_endpoint(request, rdv_id: UUID, payload: ModifierRdvIn):
    _check_gestion(request.auth)
    try:
        rdv = get_rendez_vous(rdv_id)
        medecin = None
        if payload.medecin_id is not None:
            medecin = User.objects.get(id=payload.medecin_id, role=Role.MEDECIN)
        rdv = modifier_rendez_vous(
            rdv=rdv,
            auteur=request.auth,
            version=payload.version,
            date_heure=payload.date_heure,
            medecin=medecin,
            motif=payload.motif,
            notes=payload.notes,
            duree_minutes=payload.duree_minutes,
            motif_modification=payload.motif_modification,
        )
    except User.DoesNotExist:
        raise HttpError(404, 'Médecin introuvable.')
    except RendezVousError as exc:
        _handle_error(exc)
    return _serialize_rdv(get_rendez_vous(rdv.id))


@router.post('/rendez-vous/{rdv_id}/annuler/', response=RendezVousOut, auth=jwt_auth)
def annuler_endpoint(request, rdv_id: UUID, payload: AnnulationIn):
    _check_gestion(request.auth)
    try:
        rdv = get_rendez_vous(rdv_id)
        rdv = annuler_rendez_vous(
            rdv=rdv,
            auteur=request.auth,
            version=payload.version,
            motif_annulation=payload.motif_annulation,
        )
    except RendezVousError as exc:
        _handle_error(exc)
    return _serialize_rdv(get_rendez_vous(rdv.id))


@router.post('/rendez-vous/{rdv_id}/terminer/', response=RendezVousOut, auth=jwt_auth)
def terminer_endpoint(request, rdv_id: UUID, payload: VersionIn):
    _check_gestion(request.auth)
    try:
        rdv = get_rendez_vous(rdv_id)
        rdv = terminer_rendez_vous(rdv=rdv, auteur=request.auth, version=payload.version)
    except RendezVousError as exc:
        _handle_error(exc)
    return _serialize_rdv(get_rendez_vous(rdv.id))


@router.post('/rendez-vous/{rdv_id}/absent/', response=RendezVousOut, auth=jwt_auth)
def absent_endpoint(request, rdv_id: UUID, payload: VersionIn):
    _check_gestion(request.auth)
    try:
        rdv = get_rendez_vous(rdv_id)
        rdv = marquer_absent(rdv=rdv, auteur=request.auth, version=payload.version)
    except RendezVousError as exc:
        _handle_error(exc)
    return _serialize_rdv(get_rendez_vous(rdv.id))
