import secrets
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from django.conf import settings
from django.utils import timezone
from ninja import Router, Schema
from ninja.errors import HttpError

from accounts.models import Role, User
from api.v1.auth_backend import JWTAuth
from rendezvous.models import RendezVous, StatutRendezVous, TypeConsultation

router = Router(tags=['Téléconsultation'])
jwt_auth = JWTAuth()

ROLES = {Role.ADMIN, Role.MEDECIN}

VISIO_EARLY_MINUTES = getattr(settings, 'SGHL_VISIO_EARLY_MINUTES', 15)
VISIO_LATE_MINUTES = getattr(settings, 'SGHL_VISIO_LATE_MINUTES', 15)


def _check(user: User):
    if user.role not in ROLES:
        raise HttpError(403, 'Accès refusé.')


def _visio_room_name(rdv_id: UUID) -> str:
    prefix = getattr(settings, 'SGHL_JITSI_ROOM_PREFIX', 'sghl-visio')
    return f'{prefix}-{rdv_id.hex}'


def _find_rdv_by_visio_token(token: str) -> Optional[RendezVous]:
    token = (token or '').strip()
    if not token:
        return None
    suffix = f'/visio/{token}'
    return (
        RendezVous.objects.filter(
            type_consultation=TypeConsultation.TELECONSULTATION,
            lien_visio__endswith=suffix,
        )
        .select_related('patient', 'medecin')
        .first()
    )


def _join_window(rdv: RendezVous) -> tuple[datetime, datetime]:
    start = rdv.date_heure - timedelta(minutes=VISIO_EARLY_MINUTES)
    end = rdv.date_heure + timedelta(minutes=rdv.duree_minutes + VISIO_LATE_MINUTES)
    return start, end


def _can_join_rdv(rdv: RendezVous) -> tuple[bool, str]:
    if rdv.statut == StatutRendezVous.ANNULE:
        return False, 'Cette téléconsultation a été annulée.'
    if rdv.statut == StatutRendezVous.TERMINE:
        return False, 'Cette téléconsultation est terminée.'
    if rdv.statut == StatutRendezVous.ABSENT:
        return False, 'Cette téléconsultation a été classée absente.'

    now = timezone.now()
    start, end = _join_window(rdv)
    if now < start:
        return False, (
            f'La salle ouvrira le {timezone.localtime(start).strftime("%d/%m/%Y à %H:%M")} '
            f'({VISIO_EARLY_MINUTES} min avant le rendez-vous).'
        )
    if now > end:
        return False, 'Le créneau de téléconsultation est expiré.'
    return True, ''


class TeleconsultationOut(Schema):
    id: UUID
    patient_id: UUID
    patientName: str
    doctorName: str
    dateTime: str
    duration: int
    status: str
    lien_visio: str


class StatsTeleconsultationOut(Schema):
    consultations_ce_mois: int
    en_cours: int
    satisfaction_rate: int


class VisioSessionOut(Schema):
    id: UUID
    patientName: str
    doctorName: str
    dateTime: str
    duree_minutes: int
    statut: str
    motif: str
    room_name: str
    jitsi_domain: str
    can_join: bool
    join_message: str
    opens_at: str
    closes_at: str


def _status_map(statut: str) -> str:
    if statut in {StatutRendezVous.PLANIFIE, StatutRendezVous.CONFIRME}:
        return 'scheduled'
    if statut == StatutRendezVous.TERMINE:
        return 'completed'
    if statut == StatutRendezVous.ANNULE:
        return 'cancelled'
    return statut


def _serialize(rdv: RendezVous) -> TeleconsultationOut:
    patient = rdv.patient
    medecin = rdv.medecin
    return TeleconsultationOut(
        id=rdv.id,
        patient_id=patient.id,
        patientName=f'{patient.prenom} {patient.nom}',
        doctorName=f'{medecin.first_name} {medecin.last_name}'.strip() or medecin.username,
        dateTime=rdv.date_heure.strftime('%Y-%m-%d %H:%M'),
        duration=rdv.duree_minutes,
        status=_status_map(rdv.statut),
        lien_visio=rdv.lien_visio,
    )


def _serialize_visio_session(rdv: RendezVous) -> VisioSessionOut:
    patient = rdv.patient
    medecin = rdv.medecin
    can_join, join_message = _can_join_rdv(rdv)
    start, end = _join_window(rdv)
    return VisioSessionOut(
        id=rdv.id,
        patientName=f'{patient.prenom} {patient.nom}',
        doctorName=f'{medecin.first_name} {medecin.last_name}'.strip() or medecin.username,
        dateTime=timezone.localtime(rdv.date_heure).strftime('%d/%m/%Y à %H:%M'),
        duree_minutes=rdv.duree_minutes,
        statut=rdv.statut,
        motif=rdv.motif,
        room_name=_visio_room_name(rdv.id),
        jitsi_domain=getattr(settings, 'SGHL_JITSI_DOMAIN', 'meet.jit.si'),
        can_join=can_join,
        join_message=join_message,
        opens_at=timezone.localtime(start).isoformat(),
        closes_at=timezone.localtime(end).isoformat(),
    )


@router.get('/visio/{token}/', response=VisioSessionOut)
def get_visio_session(request, token: str):
    rdv = _find_rdv_by_visio_token(token)
    if not rdv:
        raise HttpError(404, 'Lien de téléconsultation invalide ou expiré.')
    return _serialize_visio_session(rdv)


@router.get('/teleconsultation/stats/', response=StatsTeleconsultationOut, auth=jwt_auth)
def stats_teleconsultation(request):
    _check(request.auth)
    qs = RendezVous.objects.filter(type_consultation=TypeConsultation.TELECONSULTATION)
    now = datetime.now()
    ce_mois = qs.filter(date_heure__year=now.year, date_heure__month=now.month).count()
    en_cours = qs.filter(statut__in={StatutRendezVous.PLANIFIE, StatutRendezVous.CONFIRME}).count()
    return StatsTeleconsultationOut(
        consultations_ce_mois=ce_mois,
        en_cours=en_cours,
        satisfaction_rate=92,
    )


@router.get('/teleconsultation/', response=list[TeleconsultationOut], auth=jwt_auth)
def list_teleconsultations(request, status: Optional[str] = None):
    _check(request.auth)
    qs = RendezVous.objects.filter(
        type_consultation=TypeConsultation.TELECONSULTATION,
    ).select_related('patient', 'medecin').order_by('-date_heure')
    items = [_serialize(r) for r in qs]
    if status:
        items = [i for i in items if i.status == status]
    return items


@router.post('/teleconsultation/{rdv_id}/lien/', response=TeleconsultationOut, auth=jwt_auth)
def regenerate_visio_link(request, rdv_id: UUID):
    _check(request.auth)
    try:
        rdv = RendezVous.objects.select_related('patient', 'medecin').get(
            id=rdv_id,
            type_consultation=TypeConsultation.TELECONSULTATION,
        )
    except RendezVous.DoesNotExist:
        raise HttpError(404, 'Téléconsultation introuvable.')
    token = secrets.token_urlsafe(16)
    base = getattr(settings, 'SGHL_FRONTEND_URL', 'http://localhost:5173').rstrip('/')
    rdv.lien_visio = f'{base}/visio/{token}'
    rdv.save(update_fields=['lien_visio', 'updated_at'])
    return _serialize(rdv)
