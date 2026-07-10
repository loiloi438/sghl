from django.db import transaction
from django.utils import timezone

from accounts.models import Role, User
from hospitalisation.models import Hospitalisation, StatutHospitalisation
from laboratoire.models import (
    AnalyseCatalogue,
    CommandeAnalyse,
    LigneCommandeAnalyse,
    ResultatAnalyse,
    StatutCommandeAnalyse,
)


class LaboratoireError(Exception):
    def __init__(self, message: str, code: str = 'error'):
        self.message = message
        self.code = code
        super().__init__(message)


def get_hospitalisation_active(hospitalisation_id) -> Hospitalisation:
    try:
        hospitalisation = Hospitalisation.objects.get(id=hospitalisation_id)
    except Hospitalisation.DoesNotExist:
        raise LaboratoireError('Hospitalisation introuvable.', code='not_found')
    if hospitalisation.statut != StatutHospitalisation.ACTIVE:
        raise LaboratoireError(
            'Une commande d\'analyse requiert une hospitalisation active.',
            code='hospitalisation_inactive',
        )
    return hospitalisation


def get_commande(commande_id) -> CommandeAnalyse:
    try:
        return CommandeAnalyse.objects.select_related(
            'hospitalisation__patient',
            'medecin',
            'preleve_par',
            'affectee_a',
            'affectee_par',
            'validee_par',
            'publiee_par',
        ).prefetch_related('lignes__resultat').get(id=commande_id)
    except CommandeAnalyse.DoesNotExist:
        raise LaboratoireError('Commande introuvable.', code='not_found')


def assert_medecin(user: User):
    if user.role not in {Role.ADMIN, Role.MEDECIN}:
        raise LaboratoireError('Seul un médecin peut effectuer cette action.', code='acces_refuse')


def assert_biologiste(user: User):
    if user.role not in {Role.ADMIN, Role.BIOLOGISTE}:
        raise LaboratoireError(
            'Seul un biologiste peut effectuer cette action.',
            code='acces_refuse',
        )


def assert_preleveur(user: User):
    if user.role not in {Role.ADMIN, Role.MEDECIN, Role.INFIRMIER}:
        raise LaboratoireError('Accès refusé pour le prélèvement.', code='acces_refuse')


def assert_saisie_resultats(user: User):
    if user.role not in {Role.ADMIN, Role.BIOLOGISTE}:
        raise LaboratoireError('Accès refusé pour la saisie des résultats.', code='acces_refuse')


def _ajouter_lignes(commande: CommandeAnalyse, codes_analyses: list[str]):
    for code in codes_analyses:
        try:
            analyse = AnalyseCatalogue.objects.get(code=code, actif=True)
        except AnalyseCatalogue.DoesNotExist:
            raise LaboratoireError(f'Analyse invalide : {code}.', code='analyse_invalide')
        LigneCommandeAnalyse.objects.get_or_create(
            commande=commande,
            code_analyse=analyse.code,
            defaults={
                'libelle': analyse.libelle,
                'unite_reference': analyse.unite_reference,
                'valeur_reference': analyse.valeur_reference,
            },
        )


def creer_commande(
    *,
    hospitalisation: Hospitalisation,
    medecin: User,
    codes_analyses: list[str],
    observations: str = '',
) -> CommandeAnalyse:
    assert_medecin(medecin)
    get_hospitalisation_active(hospitalisation.id)
    if not codes_analyses:
        raise LaboratoireError(
            'Sélectionnez au moins une analyse.',
            code='commande_vide',
        )

    commande = CommandeAnalyse.objects.create(
        hospitalisation=hospitalisation,
        medecin=medecin,
        observations=observations,
    )
    _ajouter_lignes(commande, codes_analyses)
    return commande


def _verifier_statut(commande: CommandeAnalyse, statut_attendu: StatutCommandeAnalyse):
    if commande.statut != statut_attendu:
        raise LaboratoireError(
            f'Action impossible au statut « {commande.get_statut_display()} ».',
            code='statut_invalide',
        )


@transaction.atomic
def enregistrer_prelevement(
    *,
    commande: CommandeAnalyse,
    preleveur: User,
    type_echantillon: str,
    reference_echantillon: str = '',
) -> CommandeAnalyse:
    assert_preleveur(preleveur)
    cmd = CommandeAnalyse.objects.select_for_update().get(pk=commande.pk)
    _verifier_statut(cmd, StatutCommandeAnalyse.COMMANDEE)
    get_hospitalisation_active(cmd.hospitalisation_id)

    cmd.statut = StatutCommandeAnalyse.PRELEVEE
    cmd.preleve_le = timezone.now()
    cmd.preleve_par = preleveur
    cmd.type_echantillon = type_echantillon
    cmd.reference_echantillon = reference_echantillon
    cmd.bump_version()
    cmd.save(
        update_fields=[
            'statut',
            'preleve_le',
            'preleve_par',
            'type_echantillon',
            'reference_echantillon',
            'version',
            'updated_at',
        ]
    )
    return cmd


@transaction.atomic
def enregistrer_affectation(
    *,
    commande: CommandeAnalyse,
    affectee_a: User,
    affectee_par: User,
) -> CommandeAnalyse:
    assert_saisie_resultats(affectee_par)
    if affectee_a.role not in {Role.ADMIN, Role.BIOLOGISTE}:
        raise LaboratoireError(
            'L\'affectation doit cibler un biologiste.',
            code='affectation_invalide',
        )

    cmd = CommandeAnalyse.objects.select_for_update().get(pk=commande.pk)
    _verifier_statut(cmd, StatutCommandeAnalyse.PRELEVEE)
    get_hospitalisation_active(cmd.hospitalisation_id)

    cmd.statut = StatutCommandeAnalyse.AFFECTEE
    cmd.affectee_le = timezone.now()
    cmd.affectee_a = affectee_a
    cmd.affectee_par = affectee_par
    cmd.bump_version()
    cmd.save(
        update_fields=[
            'statut',
            'affectee_le',
            'affectee_a',
            'affectee_par',
            'version',
            'updated_at',
        ]
    )
    return cmd


def _toutes_lignes_ont_resultat(commande: CommandeAnalyse) -> bool:
    if not commande.lignes.exists():
        return False
    return not commande.lignes.filter(resultat__isnull=True).exists()


@transaction.atomic
def saisir_resultats(
    *,
    commande: CommandeAnalyse,
    saisi_par: User,
    resultats: list[dict],
) -> CommandeAnalyse:
    assert_saisie_resultats(saisi_par)
    cmd = CommandeAnalyse.objects.select_for_update().get(pk=commande.pk)
    if cmd.est_verrouillee:
        raise LaboratoireError(
            'Les résultats sont verrouillés après validation.',
            code='commande_verrouillee',
        )
    if cmd.statut not in {
        StatutCommandeAnalyse.AFFECTEE,
        StatutCommandeAnalyse.RESULTATS_SAISIS,
    }:
        raise LaboratoireError(
            'La saisie des résultats requiert une commande affectée.',
            code='statut_invalide',
        )
    get_hospitalisation_active(cmd.hospitalisation_id)

    lignes_par_id = {str(l.id): l for l in cmd.lignes.all()}
    for item in resultats:
        ligne_id = str(item['ligne_id'])
        if ligne_id not in lignes_par_id:
            raise LaboratoireError('Ligne de commande introuvable.', code='not_found')
        ligne = lignes_par_id[ligne_id]
        ResultatAnalyse.objects.update_or_create(
            ligne=ligne,
            defaults={
                'valeur': item['valeur'],
                'unite': item.get('unite', ligne.unite_reference),
                'commentaire': item.get('commentaire', ''),
                'saisi_par': saisi_par,
            },
        )

    cmd.refresh_from_db()
    cmd = CommandeAnalyse.objects.prefetch_related('lignes__resultat').get(pk=cmd.pk)
    if _toutes_lignes_ont_resultat(cmd):
        cmd.statut = StatutCommandeAnalyse.RESULTATS_SAISIS
        cmd.bump_version()
        cmd.save(update_fields=['statut', 'version', 'updated_at'])
    return cmd


@transaction.atomic
def valider_commande(*, commande: CommandeAnalyse, biologiste: User, version: int) -> CommandeAnalyse:
    assert_biologiste(biologiste)
    cmd = CommandeAnalyse.objects.select_for_update().prefetch_related('lignes__resultat').get(
        pk=commande.pk
    )

    if cmd.version != version:
        raise LaboratoireError('Conflit de version : rechargez et réessayez.', code='version_conflict')
    _verifier_statut(cmd, StatutCommandeAnalyse.RESULTATS_SAISIS)
    if not _toutes_lignes_ont_resultat(cmd):
        raise LaboratoireError(
            'Tous les résultats doivent être saisis avant validation.',
            code='resultats_incomplets',
        )
    get_hospitalisation_active(cmd.hospitalisation_id)

    cmd.statut = StatutCommandeAnalyse.VALIDEE
    cmd.validee_le = timezone.now()
    cmd.validee_par = biologiste
    cmd.bump_version()
    cmd.save(update_fields=['statut', 'validee_le', 'validee_par', 'version', 'updated_at'])
    return cmd


@transaction.atomic
def publier_commande(*, commande: CommandeAnalyse, biologiste: User, version: int) -> CommandeAnalyse:
    assert_biologiste(biologiste)
    cmd = CommandeAnalyse.objects.select_for_update().get(pk=commande.pk)

    if cmd.version != version:
        raise LaboratoireError('Conflit de version : rechargez et réessayez.', code='version_conflict')
    _verifier_statut(cmd, StatutCommandeAnalyse.VALIDEE)
    get_hospitalisation_active(cmd.hospitalisation_id)

    cmd.statut = StatutCommandeAnalyse.PUBLIEE
    cmd.publiee_le = timezone.now()
    cmd.publiee_par = biologiste
    cmd.bump_version()
    cmd.save(update_fields=['statut', 'publiee_le', 'publiee_par', 'version', 'updated_at'])
    return cmd
