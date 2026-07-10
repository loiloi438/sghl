import logging
from decimal import Decimal
from uuid import UUID

from django.db import transaction
from django.utils import timezone

from facturation.models import Facture
from notifications.push_service import notifier_patient_utilisateur
from rendezvous.models import RendezVous

logger = logging.getLogger(__name__)


def _charger_rdv(rdv_id: UUID):
    try:
        return RendezVous.objects.select_related('patient', 'medecin').get(pk=rdv_id)
    except RendezVous.DoesNotExist:
        return None


def push_rdv_planifie(rdv_id: UUID) -> None:
    rdv = _charger_rdv(rdv_id)
    if not rdv:
        return
    date_locale = timezone.localtime(rdv.date_heure)
    notifier_patient_utilisateur(
        patient=rdv.patient,
        titre='Rendez-vous planifié',
        corps=f'{date_locale:%d/%m/%Y à %H:%M} — Dr {rdv.medecin.get_full_name() or rdv.medecin.username}',
        categorie='rendez_vous',
        donnees={'rdv_id': str(rdv.id), 'statut': 'planifie'},
    )


def push_rdv_confirme(rdv_id: UUID) -> None:
    rdv = _charger_rdv(rdv_id)
    if not rdv:
        return
    date_locale = timezone.localtime(rdv.date_heure)
    notifier_patient_utilisateur(
        patient=rdv.patient,
        titre='Rendez-vous confirmé',
        corps=f'Présentez-vous le {date_locale:%d/%m/%Y à %H:%M}.',
        categorie='rendez_vous',
        donnees={'rdv_id': str(rdv.id), 'statut': 'confirme'},
    )


def push_rdv_annule(rdv_id: UUID, motif: str = '') -> None:
    rdv = _charger_rdv(rdv_id)
    if not rdv:
        return
    notifier_patient_utilisateur(
        patient=rdv.patient,
        titre='Rendez-vous annulé',
        corps=motif or 'Votre rendez-vous a été annulé.',
        categorie='rendez_vous',
        donnees={'rdv_id': str(rdv.id), 'statut': 'annule'},
    )


def push_rdv_rappel_j1(rdv_id: UUID):
    rdv = _charger_rdv(rdv_id)
    if not rdv:
        return None
    date_locale = timezone.localtime(rdv.date_heure)
    return notifier_patient_utilisateur(
        patient=rdv.patient,
        titre='Rappel : RDV demain',
        corps=f'{date_locale:%d/%m/%Y à %H:%M} — {rdv.motif}',
        categorie='rendez_vous',
        donnees={'rdv_id': str(rdv.id), 'type': 'rappel_j1'},
    )


def push_facture_validee(facture_id: UUID) -> None:
    try:
        facture = Facture.objects.select_related('hospitalisation__patient').get(pk=facture_id)
    except Facture.DoesNotExist:
        return
    notifier_patient_utilisateur(
        patient=facture.hospitalisation.patient,
        titre='Nouvelle facture',
        corps=f'Facture {facture.numero_facture} : {facture.montant_total} FCFA à régler.',
        categorie='facturation',
        donnees={'facture_id': str(facture.id)},
    )


def push_paiement_facture(facture_id: UUID, montant: Decimal) -> None:
    try:
        facture = Facture.objects.select_related('hospitalisation__patient').get(pk=facture_id)
    except Facture.DoesNotExist:
        return
    notifier_patient_utilisateur(
        patient=facture.hospitalisation.patient,
        titre='Paiement enregistré',
        corps=f'{montant} FCFA reçus. Reste : {facture.montant_restant} FCFA.',
        categorie='facturation',
        donnees={'facture_id': str(facture.id), 'montant': str(montant)},
    )


def planifier_push_rdv_planifie(rdv_id: UUID) -> None:
    transaction.on_commit(lambda: push_rdv_planifie(rdv_id))


def planifier_push_rdv_confirme(rdv_id: UUID) -> None:
    transaction.on_commit(lambda: push_rdv_confirme(rdv_id))


def planifier_push_rdv_annule(rdv_id: UUID, motif: str = '') -> None:
    m = motif
    transaction.on_commit(lambda: push_rdv_annule(rdv_id, m))


def planifier_push_facture_validee(facture_id: UUID) -> None:
    transaction.on_commit(lambda: push_facture_validee(facture_id))


def planifier_push_paiement(facture_id: UUID, montant: Decimal) -> None:
    m = montant
    transaction.on_commit(lambda: push_paiement_facture(facture_id, m))


def push_rdv_reporte(rdv_id: UUID, ancienne_date: str, motif: str = ''):
    rdv = _charger_rdv(rdv_id)
    if not rdv:
        return None
    return notifier_patient_utilisateur(
        patient=rdv.patient,
        titre='Rendez-vous reporté',
        corps=f'Nouveau créneau : {timezone.localtime(rdv.date_heure):%d/%m/%Y %H:%M} (était {ancienne_date}).',
        categorie='rendez_vous',
        donnees={'rdv_id': str(rdv.id), 'type': 'reporte'},
    )


def push_rdv_modifie(rdv_id: UUID, changements: str):
    rdv = _charger_rdv(rdv_id)
    if not rdv:
        return None
    return notifier_patient_utilisateur(
        patient=rdv.patient,
        titre='Rendez-vous modifié',
        corps=changements or 'Votre rendez-vous a été mis à jour.',
        categorie='rendez_vous',
        donnees={'rdv_id': str(rdv.id), 'type': 'modifie'},
    )


def planifier_push_rdv_reporte(rdv_id: UUID, ancienne_date: str, motif: str = '') -> None:
    ad, mm = ancienne_date, motif
    transaction.on_commit(lambda rid=rdv_id, a=ad, m=mm: push_rdv_reporte(rid, a, m))


def planifier_push_rdv_modifie(rdv_id: UUID, changements: str) -> None:
    tc = changements
    transaction.on_commit(lambda rid=rdv_id, t=tc: push_rdv_modifie(rid, t))
