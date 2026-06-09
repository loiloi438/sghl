from datetime import datetime
from typing import Optional
from uuid import UUID

from django.db.models import Q
from ninja import Router, Schema
from ninja.errors import HttpError
from ninja.pagination import paginate

from accounts.models import Role, User
from api.v1.auth_backend import JWTAuth
from audit.services import get_client_ip, log_audit
from laboratoire.models import AnalyseCatalogue, CommandeAnalyse, ResultatAnalyse
from laboratoire.services import (
    LaboratoireError,
    creer_commande,
    enregistrer_affectation,
    enregistrer_prelevement,
    get_commande,
    get_hospitalisation_active,
    publier_commande,
    saisir_resultats,
    valider_commande,
)

router = Router(tags=['Laboratoire'])
jwt_auth = JWTAuth()

ROLES_LECTURE = {Role.ADMIN, Role.MEDECIN, Role.INFIRMIER, Role.BIOLOGISTE, Role.PHARMACIEN}
ROLES_COMMANDE = {Role.ADMIN, Role.MEDECIN}
ROLES_PRELEVEMENT = {Role.ADMIN, Role.MEDECIN, Role.INFIRMIER}
ROLES_LABO = {Role.ADMIN, Role.BIOLOGISTE}


def _check_read(user: User):
    if user.role not in ROLES_LECTURE:
        raise HttpError(403, 'Accès refusé.')


def _check_roles(user: User, roles: set):
    if user.role not in roles:
        raise HttpError(403, 'Accès refusé.')


def _handle_error(exc: LaboratoireError):
    status_map = {
        'not_found': 404,
        'version_conflict': 409,
        'commande_verrouillee': 403,
        'acces_refuse': 403,
        'statut_invalide': 400,
    }
    raise HttpError(status_map.get(exc.code, 400), exc.message)


class AnalyseCatalogueOut(Schema):
    code: str
    libelle: str
    unite_reference: str
    valeur_reference: str


class ResultatOut(Schema):
    id: UUID
    ligne_id: UUID
    code_analyse: str
    libelle: str
    valeur: str
    unite: str
    valeur_reference: str
    commentaire: str


class LigneCommandeOut(Schema):
    id: UUID
    code_analyse: str
    libelle: str
    unite_reference: str
    valeur_reference: str
    resultat: Optional[ResultatOut]


class CommandeAnalyseOut(Schema):
    id: UUID
    hospitalisation_id: UUID
    patient_id: UUID
    numero_dossier: str
    medecin_id: int
    medecin_nom: str
    statut: str
    observations: str
    type_echantillon: str
    reference_echantillon: str
    preleve_le: Optional[datetime]
    affectee_le: Optional[datetime]
    affectee_a_nom: Optional[str]
    validee_le: Optional[datetime]
    validee_par_id: Optional[int]
    publiee_le: Optional[datetime]
    lignes: list[LigneCommandeOut]
    version: int
    est_verrouillee: bool
    created_at: datetime


class CommandeAnalyseIn(Schema):
    codes_analyses: list[str]
    observations: str = ''


class PrelevementIn(Schema):
    type_echantillon: str
    reference_echantillon: str = ''


class AffectationIn(Schema):
    affectee_a_id: int


class ResultatIn(Schema):
    ligne_id: UUID
    valeur: str
    unite: str = ''
    commentaire: str = ''


class ResultatsIn(Schema):
    resultats: list[ResultatIn]


class VersionIn(Schema):
    version: int


def _user_nom(user: User | None) -> Optional[str]:
    if user is None:
        return None
    return f'{user.first_name} {user.last_name}'.strip() or user.username


def _serialize_commande(c: CommandeAnalyse) -> CommandeAnalyseOut:
    patient = c.hospitalisation.patient
    medecin = c.medecin
    lignes_out = []
    for ligne in c.lignes.all():
        resultat = None
        try:
            r = ligne.resultat
            resultat = ResultatOut(
                id=r.id,
                ligne_id=ligne.id,
                code_analyse=ligne.code_analyse,
                libelle=ligne.libelle,
                valeur=r.valeur,
                unite=r.unite,
                valeur_reference=ligne.valeur_reference,
                commentaire=r.commentaire,
            )
        except ResultatAnalyse.DoesNotExist:
            # Pas de résultat pour cette ligne
            pass
        except Exception as exc:
            # Logger l'erreur inattendue mais ne pas interrompre la sérialisation
            import logging

            logging.getLogger(__name__).exception("Erreur lors de la sérialisation d'une ligne de commande: %s", exc)
        lignes_out.append(
            LigneCommandeOut(
                id=ligne.id,
                code_analyse=ligne.code_analyse,
                libelle=ligne.libelle,
                unite_reference=ligne.unite_reference,
                valeur_reference=ligne.valeur_reference,
                resultat=resultat,
            )
        )

    return CommandeAnalyseOut(
        id=c.id,
        hospitalisation_id=c.hospitalisation_id,
        patient_id=patient.id,
        numero_dossier=patient.numero_dossier,
        medecin_id=medecin.id,
        medecin_nom=_user_nom(medecin) or medecin.username,
        statut=c.statut,
        observations=c.observations,
        type_echantillon=c.type_echantillon,
        reference_echantillon=c.reference_echantillon,
        preleve_le=c.preleve_le,
        affectee_le=c.affectee_le,
        affectee_a_nom=_user_nom(c.affectee_a),
        validee_le=c.validee_le,
        validee_par_id=c.validee_par_id,
        publiee_le=c.publiee_le,
        lignes=lignes_out,
        version=c.version,
        est_verrouillee=c.est_verrouillee,
        created_at=c.created_at,
    )


def _load_commande(commande_id: UUID) -> CommandeAnalyse:
    return get_commande(commande_id)


@router.get('/analyses-catalogue/', response=list[AnalyseCatalogueOut], auth=jwt_auth)
@paginate
def list_analyses_catalogue(request, search: str = ''):
    _check_read(request.auth)
    qs = AnalyseCatalogue.objects.filter(actif=True)
    if search:
        qs = qs.filter(Q(code__icontains=search) | Q(libelle__icontains=search))
    return [
        AnalyseCatalogueOut(
            code=a.code,
            libelle=a.libelle,
            unite_reference=a.unite_reference,
            valeur_reference=a.valeur_reference,
        )
        for a in qs
    ]


@router.get(
    '/hospitalisations/{hospitalisation_id}/commandes-analyses/',
    response=list[CommandeAnalyseOut],
    auth=jwt_auth,
)
@paginate
def list_commandes_hospitalisation(request, hospitalisation_id: UUID):
    _check_read(request.auth)
    qs = CommandeAnalyse.objects.filter(
        hospitalisation_id=hospitalisation_id,
    ).select_related(
        'hospitalisation__patient',
        'medecin',
        'affectee_a',
        'validee_par',
        'publiee_par',
    ).prefetch_related('lignes__resultat')
    return [_serialize_commande(c) for c in qs]


@router.post(
    '/hospitalisations/{hospitalisation_id}/commandes-analyses/',
    response=CommandeAnalyseOut,
    auth=jwt_auth,
)
def create_commande_analyse(request, hospitalisation_id: UUID, payload: CommandeAnalyseIn):
    _check_roles(request.auth, ROLES_COMMANDE)
    try:
        hospitalisation = get_hospitalisation_active(hospitalisation_id)
        commande = creer_commande(
            hospitalisation=hospitalisation,
            medecin=request.auth,
            codes_analyses=payload.codes_analyses,
            observations=payload.observations,
        )
    except LaboratoireError as exc:
        _handle_error(exc)

    commande = _load_commande(commande.id)
    data = _serialize_commande(commande)
    log_audit(
        user=request.auth,
        action='CREATE',
        model_name='CommandeAnalyse',
        object_id=commande.id,
        new_value=data.model_dump(),
        ip_address=get_client_ip(request),
    )
    return data


@router.get('/commandes-analyses/{commande_id}/', response=CommandeAnalyseOut, auth=jwt_auth)
def get_commande_detail(request, commande_id: UUID):
    _check_read(request.auth)
    try:
        commande = _load_commande(commande_id)
    except LaboratoireError as exc:
        _handle_error(exc)
    return _serialize_commande(commande)


@router.post('/commandes-analyses/{commande_id}/prelevement/', response=CommandeAnalyseOut, auth=jwt_auth)
def prelevement_endpoint(request, commande_id: UUID, payload: PrelevementIn):
    _check_roles(request.auth, ROLES_PRELEVEMENT)
    try:
        commande = get_commande(commande_id)
        commande = enregistrer_prelevement(
            commande=commande,
            preleveur=request.auth,
            type_echantillon=payload.type_echantillon,
            reference_echantillon=payload.reference_echantillon,
        )
    except LaboratoireError as exc:
        _handle_error(exc)

    commande = _load_commande(commande.id)
    data = _serialize_commande(commande)
    log_audit(
        user=request.auth,
        action='UPDATE',
        model_name='CommandeAnalyse',
        object_id=commande.id,
        new_value={**data.model_dump(), 'event': 'prelevement'},
        ip_address=get_client_ip(request),
    )
    return data


@router.post('/commandes-analyses/{commande_id}/affectation/', response=CommandeAnalyseOut, auth=jwt_auth)
def affectation_endpoint(request, commande_id: UUID, payload: AffectationIn):
    _check_roles(request.auth, ROLES_LABO)
    try:
        from accounts.models import User

        affectee_a = User.objects.get(id=payload.affectee_a_id)
        commande = get_commande(commande_id)
        commande = enregistrer_affectation(
            commande=commande,
            affectee_a=affectee_a,
            affectee_par=request.auth,
        )
    except User.DoesNotExist:
        raise HttpError(404, 'Utilisateur introuvable.')
    except LaboratoireError as exc:
        _handle_error(exc)

    commande = _load_commande(commande.id)
    data = _serialize_commande(commande)
    log_audit(
        user=request.auth,
        action='UPDATE',
        model_name='CommandeAnalyse',
        object_id=commande.id,
        new_value={**data.model_dump(), 'event': 'affectation'},
        ip_address=get_client_ip(request),
    )
    return data


@router.post('/commandes-analyses/{commande_id}/resultats/', response=CommandeAnalyseOut, auth=jwt_auth)
def resultats_endpoint(request, commande_id: UUID, payload: ResultatsIn):
    _check_roles(request.auth, ROLES_LABO)
    try:
        commande = get_commande(commande_id)
        commande = saisir_resultats(
            commande=commande,
            saisi_par=request.auth,
            resultats=[r.model_dump() for r in payload.resultats],
        )
    except LaboratoireError as exc:
        _handle_error(exc)

    commande = _load_commande(commande.id)
    data = _serialize_commande(commande)
    log_audit(
        user=request.auth,
        action='UPDATE',
        model_name='CommandeAnalyse',
        object_id=commande.id,
        new_value={**data.model_dump(), 'event': 'resultats'},
        ip_address=get_client_ip(request),
    )
    return data


@router.post('/commandes-analyses/{commande_id}/valider/', response=CommandeAnalyseOut, auth=jwt_auth)
def valider_commande_endpoint(request, commande_id: UUID, payload: VersionIn):
    _check_roles(request.auth, ROLES_LABO)
    try:
        commande = get_commande(commande_id)
        commande = valider_commande(
            commande=commande,
            biologiste=request.auth,
            version=payload.version,
        )
    except LaboratoireError as exc:
        _handle_error(exc)

    commande = _load_commande(commande.id)
    data = _serialize_commande(commande)
    log_audit(
        user=request.auth,
        action='UPDATE',
        model_name='CommandeAnalyse',
        object_id=commande.id,
        new_value={**data.model_dump(), 'event': 'validation'},
        ip_address=get_client_ip(request),
    )
    return data


@router.post('/commandes-analyses/{commande_id}/publier/', response=CommandeAnalyseOut, auth=jwt_auth)
def publier_commande_endpoint(request, commande_id: UUID, payload: VersionIn):
    _check_roles(request.auth, ROLES_LABO)
    try:
        commande = get_commande(commande_id)
        commande = publier_commande(
            commande=commande,
            biologiste=request.auth,
            version=payload.version,
        )
    except LaboratoireError as exc:
        _handle_error(exc)

    commande = _load_commande(commande.id)
    data = _serialize_commande(commande)
    log_audit(
        user=request.auth,
        action='UPDATE',
        model_name='CommandeAnalyse',
        object_id=commande.id,
        new_value={**data.model_dump(), 'event': 'publication'},
        ip_address=get_client_ip(request),
    )
    return data
