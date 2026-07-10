"""Helpers réservés aux tests E2E (Playwright) — disponibles uniquement si DEBUG=True."""

import re
from datetime import timedelta

from django.conf import settings
from django.core import mail
from django.utils import timezone
from ninja import Router, Schema
from ninja.errors import HttpError

from accounts.models import Role, User
from patients.models import Patient
from rendezvous.models import RendezVous, StatutRendezVous, TypeConsultation

router = Router(tags=['E2E'])


class MfaCodeOut(Schema):
    code: str


class VisioE2ESessionOut(Schema):
    token: str
    patient_name: str
    doctor_name: str
    motif: str
    date_time: str
    can_join: bool


@router.get('/test/e2e/mfa-code/', response=MfaCodeOut)
def e2e_mfa_code(request, username: str):
    if not settings.DEBUG:
        raise HttpError(404, 'Not found')

    if not username.strip():
        raise HttpError(400, 'username requis')

    try:
        user = User.objects.get(username=username.strip())
    except User.DoesNotExist:
        raise HttpError(404, f'Utilisateur {username} introuvable.')

    pattern = re.compile(r'\b(\d{6})\b')
    for message in reversed(mail.outbox):
        if 'code de connexion' not in message.subject.lower():
            continue
        recipients = ' '.join(getattr(message, 'to', []) or [])
        if user.email and user.email not in recipients and user.email not in message.body:
            if username not in message.body:
                continue
        match = pattern.search(message.body)
        if match:
            return MfaCodeOut(code=match.group(1))

    raise HttpError(404, f'Aucun e-mail MFA récent pour {username}.')


@router.get('/test/e2e/visio-session/', response=VisioE2ESessionOut)
def e2e_visio_session(request, future: bool = False, token: str = 'e2e-visio-token'):
    if not settings.DEBUG:
        raise HttpError(404, 'Not found')

    token = (token or 'e2e-visio-token').strip()
    if not token:
        raise HttpError(400, 'token requis')

    patient = Patient.objects.filter(numero_dossier='P-2026-001').first() or Patient.objects.first()
    medecin = User.objects.filter(username='medecin', role=Role.MEDECIN).first()
    if not patient or not medecin:
        raise HttpError(500, 'Données seed insuffisantes (patient ou médecin).')

    frontend = getattr(settings, 'SGHL_FRONTEND_URL', 'http://localhost:5173').rstrip('/')
    lien_visio = f'{frontend}/visio/{token}'
    date_heure = timezone.now() + (timedelta(days=2) if future else timedelta(minutes=5))

    rdv = RendezVous.objects.filter(lien_visio__endswith=f'/visio/{token}').first()
    if rdv:
        rdv.patient = patient
        rdv.medecin = medecin
        rdv.date_heure = date_heure
        rdv.motif = 'Consultation visio E2E'
        rdv.type_consultation = TypeConsultation.TELECONSULTATION
        rdv.statut = StatutRendezVous.CONFIRME
        rdv.lien_visio = lien_visio
        rdv.duree_minutes = 30
        rdv.save(
            update_fields=[
                'patient',
                'medecin',
                'date_heure',
                'motif',
                'type_consultation',
                'statut',
                'lien_visio',
                'duree_minutes',
                'updated_at',
            ],
        )
    else:
        rdv = RendezVous.objects.create(
            patient=patient,
            medecin=medecin,
            date_heure=date_heure,
            motif='Consultation visio E2E',
            type_consultation=TypeConsultation.TELECONSULTATION,
            statut=StatutRendezVous.CONFIRME,
            lien_visio=lien_visio,
            duree_minutes=30,
        )

    from api.v1.teleconsultation import _can_join_rdv

    can_join, _ = _can_join_rdv(rdv)
    return VisioE2ESessionOut(
        token=token,
        patient_name=f'{patient.prenom} {patient.nom}',
        doctor_name=f'{medecin.first_name} {medecin.last_name}'.strip() or medecin.username,
        motif=rdv.motif,
        date_time=rdv.date_heure.strftime('%Y-%m-%d %H:%M'),
        can_join=can_join,
    )
