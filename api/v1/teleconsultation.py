import secrets
from datetime import datetime
from typing import Optional
from uuid import UUID

from django.conf import settings
from ninja import Router, Schema
from ninja.errors import HttpError

from accounts.models import Role, User
from api.v1.auth_backend import JWTAuth
from rendezvous.models import RendezVous, StatutRendezVous, TypeConsultation

router = Router(tags=['Téléconsultation'])
jwt_auth = JWTAuth()

ROLES = {Role.ADMIN, Role.MEDECIN}


def _check(user: User):
    if user.role not in ROLES:
        raise HttpError(403, 'Accès refusé.')


class TeleconsultationOut(Schema):
    id: UUID
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
        patientName=f'{patient.prenom} {patient.nom}',
        doctorName=f'{medecin.first_name} {medecin.last_name}'.strip() or medecin.username,
        dateTime=rdv.date_heure.strftime('%Y-%m-%d %H:%M'),
        duration=rdv.duree_minutes,
        status=_status_map(rdv.statut),
        lien_visio=rdv.lien_visio,
    )


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
    base = getattr(settings, 'SGHL_FRONTEND_URL', 'http://localhost:5173')
    rdv.lien_visio = f'{base}/visio/{token}'
    rdv.save(update_fields=['lien_visio', 'updated_at'])
    return _serialize(rdv)
