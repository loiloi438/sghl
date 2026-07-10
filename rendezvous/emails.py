import logging
from typing import Optional
from uuid import UUID

from django.conf import settings
from django.utils import timezone

from core.email_utils import envoyer_email_template, notifications_actives, resoudre_email_patient
from rendezvous.models import RendezVous

logger = logging.getLogger(__name__)


def _charger_rdv(rdv_id: UUID) -> Optional[RendezVous]:
    try:
        return RendezVous.objects.select_related('patient', 'medecin').get(pk=rdv_id)
    except RendezVous.DoesNotExist:
        logger.warning('E-mail RDV ignoré : rendez-vous %s introuvable.', rdv_id)
        return None


def _contexte_commun(rdv: RendezVous) -> dict:
    patient = rdv.patient
    medecin = rdv.medecin
    medecin_nom = f'{medecin.first_name} {medecin.last_name}'.strip() or medecin.username
    date_locale = timezone.localtime(rdv.date_heure)
    return {
        'etablissement': settings.SGHL_ETABLISSEMENT,
        'patient_nom': f'{patient.prenom} {patient.nom}',
        'numero_dossier': patient.numero_dossier,
        'medecin_nom': medecin_nom,
        'date_heure': date_locale.strftime('%d/%m/%Y à %H:%M'),
        'duree_minutes': rdv.duree_minutes,
        'motif': rdv.motif,
        'notes': rdv.notes,
    }


def _envoyer(
    *,
    destinataire: str,
    sujet: str,
    template_base: str,
    contexte: dict,
) -> bool:
    if not notifications_actives():
        return False
    return envoyer_email_template(
        destinataire=destinataire,
        sujet=sujet,
        template_base=f'rendezvous/emails/{template_base}',
        contexte=contexte,
    )


def _notifier(
    rdv_id: UUID,
    template_base: str,
    sujet: str,
    extra: Optional[dict] = None,
) -> bool:
    rdv = _charger_rdv(rdv_id)
    if not rdv:
        return False

    destinataire = resoudre_email_patient(rdv.patient)
    if not destinataire:
        logger.info(
            'Pas d\'e-mail patient pour le RDV %s (dossier %s).',
            rdv_id,
            rdv.patient.numero_dossier,
        )
        return False

    contexte = _contexte_commun(rdv)
    if extra:
        contexte.update(extra)
    return _envoyer(destinataire=destinataire, sujet=sujet, template_base=template_base, contexte=contexte)


def notifier_rdv_planifie(rdv_id: UUID) -> None:
    _notifier(
        rdv_id,
        'rdv_planifie',
        f'[{settings.SGHL_ETABLISSEMENT}] Rendez-vous planifié',
    )


def notifier_rdv_demande_patient(rdv_id: UUID) -> None:
    _notifier(
        rdv_id,
        'rdv_demande_patient',
        f'[{settings.SGHL_ETABLISSEMENT}] Demande de rendez-vous enregistrée',
    )


def notifier_rdv_reporte(
    rdv_id: UUID,
    *,
    ancienne_date_heure: str,
    motif_modification: str = '',
) -> None:
    _notifier(
        rdv_id,
        'rdv_reporte',
        f'[{settings.SGHL_ETABLISSEMENT}] Rendez-vous reporté',
        extra={
            'ancienne_date_heure': ancienne_date_heure,
            'motif_modification': motif_modification or 'Non précisé',
        },
    )


def notifier_rdv_modifie(rdv_id: UUID, *, changements: str) -> None:
    _notifier(
        rdv_id,
        'rdv_modifie',
        f'[{settings.SGHL_ETABLISSEMENT}] Rendez-vous modifié',
        extra={'changements': changements},
    )


def notifier_rdv_confirme(rdv_id: UUID) -> None:
    _notifier(
        rdv_id,
        'rdv_confirme',
        f'[{settings.SGHL_ETABLISSEMENT}] Rendez-vous confirmé',
    )


def notifier_rdv_annule(rdv_id: UUID, motif_annulation: str = '') -> None:
    _notifier(
        rdv_id,
        'rdv_annule',
        f'[{settings.SGHL_ETABLISSEMENT}] Rendez-vous annulé',
        extra={'motif_annulation': motif_annulation or 'Non précisé'},
    )


def notifier_rdv_rappel_j1(rdv_id: UUID) -> bool:
    rdv = _charger_rdv(rdv_id)
    if not rdv:
        return False
    date_locale = timezone.localtime(rdv.date_heure)
    return _notifier(
        rdv_id,
        'rdv_rappel_j1',
        f'[{settings.SGHL_ETABLISSEMENT}] Rappel : rendez-vous demain',
        extra={'date_jour': date_locale.strftime('%d/%m/%Y')},
    )
