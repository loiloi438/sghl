import logging
from decimal import Decimal
from uuid import UUID

from django.conf import settings

from core.email_utils import envoyer_email_template, resoudre_email_patient
from facturation.models import Facture, StatutFacture

logger = logging.getLogger(__name__)


def _charger_facture(facture_id: UUID) -> Facture | None:
    try:
        return Facture.objects.select_related(
            'hospitalisation__patient',
        ).get(pk=facture_id)
    except Facture.DoesNotExist:
        logger.warning('E-mail facture ignoré : %s introuvable.', facture_id)
        return None


def _formater_montant(montant: Decimal) -> str:
    return f'{montant:,.2f}'.replace(',', ' ').replace('.', ',')


def _contexte_facture(facture: Facture) -> dict:
    patient = facture.hospitalisation.patient
    return {
        'patient_nom': f'{patient.prenom} {patient.nom}',
        'numero_dossier': patient.numero_dossier,
        'numero_facture': facture.numero_facture or str(facture.id)[:8],
        'montant_total': _formater_montant(facture.montant_total),
        'montant_paye': _formater_montant(facture.montant_paye),
        'montant_restant': _formater_montant(facture.montant_restant),
        'statut': facture.get_statut_display(),
    }


def notifier_facture_validee(facture_id: UUID) -> bool:
    facture = _charger_facture(facture_id)
    if not facture:
        return False

    destinataire = resoudre_email_patient(facture.hospitalisation.patient)
    if not destinataire:
        logger.info('Pas d\'e-mail pour facture %s.', facture_id)
        return False

    return envoyer_email_template(
        destinataire=destinataire,
        sujet=f'[{settings.SGHL_ETABLISSEMENT}] Facture {facture.numero_facture} disponible',
        template_base='facturation/emails/facture_validee',
        contexte=_contexte_facture(facture),
    )


def notifier_paiement_facture(facture_id: UUID, montant_operation: Decimal) -> bool:
    facture = _charger_facture(facture_id)
    if not facture:
        return False

    if montant_operation <= Decimal('0'):
        return False

    destinataire = resoudre_email_patient(facture.hospitalisation.patient)
    if not destinataire:
        return False

    contexte = _contexte_facture(facture)
    contexte['montant_operation'] = _formater_montant(montant_operation)
    contexte['est_soldee'] = facture.statut == StatutFacture.PAYEE

    sujet = (
        f'[{settings.SGHL_ETABLISSEMENT}] Paiement reçu — facture {facture.numero_facture}'
        if contexte['est_soldee']
        else f'[{settings.SGHL_ETABLISSEMENT}] Paiement partiel — facture {facture.numero_facture}'
    )

    return envoyer_email_template(
        destinataire=destinataire,
        sujet=sujet,
        template_base='facturation/emails/facture_paiement',
        contexte=contexte,
    )
