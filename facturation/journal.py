from decimal import Decimal

from accounts.models import User
from facturation.models import EcritureComptable, Facture, TypeEcritureComptable


def enregistrer_ecriture(
    *,
    facture: Facture,
    type_ecriture: str,
    montant: Decimal,
    libelle: str,
    comptable: User,
) -> EcritureComptable:
    """Append-only : aucune modification ultérieure."""
    return EcritureComptable.objects.create(
        facture=facture,
        type_ecriture=type_ecriture,
        montant=montant,
        libelle=libelle,
        comptable=comptable,
    )


def journal_validation(facture: Facture, comptable: User) -> EcritureComptable:
    return enregistrer_ecriture(
        facture=facture,
        type_ecriture=TypeEcritureComptable.VALIDATION,
        montant=facture.montant_total,
        libelle=f'Validation facture {facture.numero_facture or facture.id}',
        comptable=comptable,
    )


def journal_paiement_patient(
    facture: Facture,
    montant: Decimal,
    comptable: User,
    reference: str = '',
) -> EcritureComptable:
    ref = f' ({reference})' if reference else ''
    return enregistrer_ecriture(
        facture=facture,
        type_ecriture=TypeEcritureComptable.PAIEMENT_PATIENT,
        montant=montant,
        libelle=f'Paiement patient{ref}',
        comptable=comptable,
    )


def journal_paiement_tiers(
    facture: Facture,
    montant: Decimal,
    organisme: str,
    comptable: User,
) -> EcritureComptable:
    return enregistrer_ecriture(
        facture=facture,
        type_ecriture=TypeEcritureComptable.PAIEMENT_TIERS,
        montant=montant,
        libelle=f'Tiers payant — {organisme}',
        comptable=comptable,
    )
