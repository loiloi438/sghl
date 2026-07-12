from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from accounts.models import Role, User
from facturation.emails import notifier_facture_validee, notifier_paiement_facture
from notifications.integrations import planifier_push_facture_validee, planifier_push_paiement
from facturation.journal import journal_paiement_patient, journal_paiement_tiers, journal_validation
from facturation.models import (
    Facture,
    LigneFacture,
    SourceLigneFacture,
    StatutFacture,
    TarifActe,
)
from hospitalisation.models import Hospitalisation
from laboratoire.models import StatutCommandeAnalyse
from prescriptions.models import StatutPrescription


class FacturationError(Exception):
    def __init__(self, message: str, code: str = 'error'):
        self.message = message
        self.code = code
        super().__init__(message)


def assert_comptable(user: User):
    if user.role not in {Role.ADMIN, Role.COMPTABLE, Role.SECRETAIRE}:
        raise FacturationError('Seul un comptable peut effectuer cette action.', code='acces_refuse')


def _assert_peut_payer_en_ligne(utilisateur: User, facture: Facture) -> None:
    if utilisateur.role in {Role.ADMIN, Role.COMPTABLE, Role.SECRETAIRE}:
        return
    if utilisateur.role != Role.PATIENT:
        raise FacturationError('Accès refusé.', code='acces_refuse')
    patient = facture.hospitalisation.patient
    if patient.compte_utilisateur_id != utilisateur.id:
        raise FacturationError('Cette facture ne vous appartient pas.', code='acces_refuse')


def get_tarif(code: str) -> TarifActe:
    try:
        return TarifActe.objects.get(code=code, actif=True)
    except TarifActe.DoesNotExist:
        raise FacturationError(f'Tarif introuvable : {code}.', code='tarif_introuvable')


def get_facture(facture_id) -> Facture:
    try:
        return Facture.objects.select_related(
            'hospitalisation__patient',
            'hospitalisation__lit__chambre__service__batiment',
            'validee_par',
            'enregistree_par',
        ).prefetch_related('lignes').get(id=facture_id)
    except Facture.DoesNotExist:
        raise FacturationError('Facture introuvable.', code='not_found')


def _prochain_numero_facture() -> str:
    year = timezone.now().year
    prefix = f'FACT-{year}-'
    count = Facture.objects.filter(numero_facture__startswith=prefix).count() + 1
    return f'{prefix}{count:04d}'


def _ajouter_ligne(
    facture: Facture,
    *,
    tarif: TarifActe,
    quantite: int,
    libelle: str | None = None,
    source: str,
) -> LigneFacture:
    montant = tarif.prix_unitaire * quantite
    return LigneFacture.objects.create(
        facture=facture,
        code_acte=tarif.code,
        libelle=libelle or tarif.libelle,
        quantite=quantite,
        prix_unitaire=tarif.prix_unitaire,
        montant_ligne=montant,
        source=source,
    )


def _recalculer_total(facture: Facture) -> Decimal:
    total = sum((l.montant_ligne for l in facture.lignes.all()), Decimal('0'))
    facture.montant_total = total
    facture.save(update_fields=['montant_total', 'updated_at'])
    return total


@transaction.atomic
def generer_facture(*, hospitalisation: Hospitalisation, comptable: User) -> Facture:
    assert_comptable(comptable)
    hospitalisation = Hospitalisation.objects.select_related('patient').get(pk=hospitalisation.pk)

    facture = Facture.objects.filter(hospitalisation=hospitalisation).first()
    if facture is None:
        facture = Facture.objects.create(hospitalisation=hospitalisation)
    else:
        facture = Facture.objects.select_for_update().get(pk=facture.pk)

    if not facture.est_modifiable:
        raise FacturationError(
            'Cette facture est verrouillée et ne peut plus être régénérée.',
            code='facture_verrouillee',
        )

    facture.lignes.all().delete()

    tarif_admission = get_tarif('ADMISSION')
    _ajouter_ligne(
        facture,
        tarif=tarif_admission,
        quantite=1,
        source=SourceLigneFacture.AUTO_SEJOUR,
    )

    fin = hospitalisation.date_sortie_effective or timezone.now()
    jours = max(1, (fin.date() - hospitalisation.date_admission.date()).days + 1)
    tarif_jour = get_tarif('SEJOUR_JOUR')
    _ajouter_ligne(
        facture,
        tarif=tarif_jour,
        quantite=jours,
        libelle=f'{tarif_jour.libelle} ({jours} jour(s))',
        source=SourceLigneFacture.AUTO_SEJOUR,
    )

    tarif_labo = None
    commandes = hospitalisation.commandes_analyses.filter(statut=StatutCommandeAnalyse.PUBLIEE)
    for commande in commandes.prefetch_related('lignes'):
        if tarif_labo is None:
            tarif_labo = get_tarif('LAB_ANALYSE')
        for ligne in commande.lignes.all():
            _ajouter_ligne(
                facture,
                tarif=tarif_labo,
                quantite=1,
                libelle=f'{tarif_labo.libelle} — {ligne.libelle}',
                source=SourceLigneFacture.AUTO_LABO,
            )

    from pharmacie.models import StatutOrdreDispensation

    tarif_pharma = None
    for prescription in hospitalisation.prescriptions.filter(
        statut=StatutPrescription.VALIDEE,
    ).select_related('ordre_dispensation').prefetch_related(
        'ordre_dispensation__lignes__medicament_stock',
    ):
        ordre = getattr(prescription, 'ordre_dispensation', None)
        if ordre is None or ordre.statut != StatutOrdreDispensation.DISPENSE:
            continue
        if tarif_pharma is None:
            tarif_pharma = get_tarif('PHARMA_LIGNE')
        for ld in ordre.lignes.all():
            _ajouter_ligne(
                facture,
                tarif=tarif_pharma,
                quantite=ld.quantite,
                libelle=f'{tarif_pharma.libelle} — {ld.medicament_stock.libelle}',
                source=SourceLigneFacture.AUTO_PHARMA,
            )

    _recalculer_total(facture)
    facture.bump_version()
    facture.save(update_fields=['version', 'updated_at'])
    return facture


@transaction.atomic
def valider_facture(*, facture: Facture, comptable: User, version: int) -> Facture:
    assert_comptable(comptable)
    f = Facture.objects.select_for_update().prefetch_related('lignes').get(pk=facture.pk)

    if f.version != version:
        raise FacturationError('Conflit de version : rechargez et réessayez.', code='version_conflict')
    if f.statut != StatutFacture.BROUILLON:
        raise FacturationError('Cette facture ne peut plus être validée.', code='facture_verrouillee')
    if not f.lignes.exists():
        raise FacturationError('Générez la facture avant validation.', code='facture_vide')

    f.statut = StatutFacture.VALIDEE
    f.numero_facture = _prochain_numero_facture()
    f.validee_le = timezone.now()
    f.validee_par = comptable
    f.bump_version()
    f.save(
        update_fields=[
            'statut',
            'numero_facture',
            'validee_le',
            'validee_par',
            'version',
            'updated_at',
        ]
    )
    journal_validation(f, comptable)
    facture_id = f.id
    transaction.on_commit(lambda: notifier_facture_validee(facture_id))
    planifier_push_facture_validee(facture_id)
    return f


def _appliquer_statut_paiement(f: Facture) -> None:
    if f.montant_couvert >= f.montant_total:
        f.statut = StatutFacture.PAYEE
        f.payee_le = timezone.now()
    elif f.montant_couvert > Decimal('0'):
        f.statut = StatutFacture.PARTIELLEMENT_PAYEE
    else:
        f.statut = StatutFacture.VALIDEE
        f.payee_le = None


@transaction.atomic
def enregistrer_paiement(
    *,
    facture: Facture,
    comptable: User,
    version: int,
    mode_paiement: str,
    reference_paiement: str = '',
    montant: Decimal | None = None,
    tiers_payant_organisme: str = '',
    tiers_payant_montant: Decimal | None = None,
) -> Facture:
    assert_comptable(comptable)
    return _enregistrer_paiement_core(
        facture=facture,
        utilisateur=comptable,
        version=version,
        mode_paiement=mode_paiement,
        reference_paiement=reference_paiement,
        montant=montant,
        tiers_payant_organisme=tiers_payant_organisme,
        tiers_payant_montant=tiers_payant_montant,
    )


@transaction.atomic
def enregistrer_paiement_en_ligne(
    *,
    facture: Facture,
    utilisateur: User,
    version: int,
    mode_paiement: str,
    reference_paiement: str = '',
    montant: Decimal | None = None,
) -> Facture:
    _assert_peut_payer_en_ligne(utilisateur, facture)
    return _enregistrer_paiement_core(
        facture=facture,
        utilisateur=utilisateur,
        version=version,
        mode_paiement=mode_paiement,
        reference_paiement=reference_paiement,
        montant=montant,
        tiers_payant_organisme='',
        tiers_payant_montant=None,
    )


@transaction.atomic
def _enregistrer_paiement_core(
    *,
    facture: Facture,
    utilisateur: User,
    version: int,
    mode_paiement: str,
    reference_paiement: str = '',
    montant: Decimal | None = None,
    tiers_payant_organisme: str = '',
    tiers_payant_montant: Decimal | None = None,
) -> Facture:
    f = Facture.objects.select_for_update().get(pk=facture.pk)

    if f.version != version:
        raise FacturationError('Conflit de version : rechargez et réessayez.', code='version_conflict')
    if f.statut not in {StatutFacture.VALIDEE, StatutFacture.PARTIELLEMENT_PAYEE}:
        raise FacturationError(
            'Seule une facture validée ou partiellement payée accepte un paiement.',
            code='statut_invalide',
        )

    montant_patient = montant if montant is not None else f.montant_restant
    if montant_patient < Decimal('0'):
        raise FacturationError('Montant invalide.', code='montant_invalide')
    if montant_patient > f.montant_restant:
        raise FacturationError(
            'Le montant dépasse le reste à payer.',
            code='montant_excessif',
        )

    montant_notif = Decimal('0')
    if montant_patient > Decimal('0'):
        f.montant_paye += montant_patient
        montant_notif = montant_patient
        journal_paiement_patient(f, montant_patient, utilisateur, reference_paiement)

    if tiers_payant_montant and tiers_payant_montant > Decimal('0'):
        if not tiers_payant_organisme.strip():
            raise FacturationError(
                'Organisme tiers payant requis.',
                code='tiers_payant_incomplet',
            )
        reste_apres_patient = f.montant_total - f.montant_paye - f.tiers_payant_montant
        if tiers_payant_montant > reste_apres_patient + Decimal('0.01'):
            raise FacturationError(
                'Montant tiers payant trop élevé.',
                code='montant_excessif',
            )
        f.tiers_payant_organisme = tiers_payant_organisme.strip()
        f.tiers_payant_montant += tiers_payant_montant
        journal_paiement_tiers(f, tiers_payant_montant, f.tiers_payant_organisme, utilisateur)

    _appliquer_statut_paiement(f)
    f.enregistree_par = utilisateur
    f.mode_paiement = mode_paiement
    f.reference_paiement = reference_paiement
    f.bump_version()
    f.save(
        update_fields=[
            'statut',
            'montant_paye',
            'tiers_payant_organisme',
            'tiers_payant_montant',
            'payee_le',
            'enregistree_par',
            'mode_paiement',
            'reference_paiement',
            'version',
            'updated_at',
        ]
    )
    if montant_notif > Decimal('0'):
        facture_id = f.id
        montant = montant_notif
        transaction.on_commit(lambda: notifier_paiement_facture(facture_id, montant))
        planifier_push_paiement(facture_id, montant)
    return f
