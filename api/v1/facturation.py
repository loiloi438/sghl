from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from ninja import Router, Schema
from ninja.errors import HttpError
from ninja.pagination import paginate

from accounts.models import Role, User
from api.v1.auth_backend import JWTAuth
from audit.services import get_client_ip, log_audit
from facturation.models import EcritureComptable, Facture, StatutFacture, TarifActe
from facturation.services import (
    FacturationError,
    enregistrer_paiement,
    generer_facture,
    get_facture,
    valider_facture,
)
from hospitalisation.models import Hospitalisation, StatutHospitalisation

router = Router(tags=['Facturation'])
jwt_auth = JWTAuth()

ROLES_LECTURE = {Role.ADMIN, Role.COMPTABLE, Role.MEDECIN}
ROLES_FACTURATION = {Role.ADMIN, Role.COMPTABLE}


def _check_read(user: User):
    if user.role not in ROLES_LECTURE:
        raise HttpError(403, 'Accès refusé.')


def _check_comptable(user: User):
    if user.role not in ROLES_FACTURATION:
        raise HttpError(403, 'Accès refusé.')


def _handle_error(exc: FacturationError):
    status_map = {
        'not_found': 404,
        'version_conflict': 409,
        'facture_verrouillee': 403,
        'acces_refuse': 403,
    }
    raise HttpError(status_map.get(exc.code, 400), exc.message)


class TarifActeOut(Schema):
    code: str
    libelle: str
    categorie: str
    prix_unitaire: Decimal


class LigneFactureOut(Schema):
    id: UUID
    code_acte: str
    libelle: str
    quantite: int
    prix_unitaire: Decimal
    montant_ligne: Decimal
    source: str


class FactureOut(Schema):
    id: UUID
    hospitalisation_id: UUID
    patient_id: UUID
    numero_dossier: str
    patient_nom: str
    numero_facture: Optional[str]
    statut: str
    montant_total: Decimal
    montant_paye: Decimal
    tiers_payant_organisme: str
    tiers_payant_montant: Decimal
    montant_restant: Decimal
    lignes: list[LigneFactureOut]
    validee_le: Optional[datetime]
    payee_le: Optional[datetime]
    mode_paiement: str
    reference_paiement: str
    version: int
    est_verrouillee: bool
    created_at: datetime


class HospitalisationAFacturerOut(Schema):
    hospitalisation_id: UUID
    patient_id: UUID
    numero_dossier: str
    patient_nom: str
    statut_hospitalisation: str
    facture_id: Optional[UUID]
    facture_statut: Optional[str]
    montant_total: Optional[Decimal]


class VersionIn(Schema):
    version: int


class PaiementIn(Schema):
    version: int
    mode_paiement: str
    reference_paiement: str = ''
    montant: Optional[Decimal] = None
    tiers_payant_organisme: str = ''
    tiers_payant_montant: Optional[Decimal] = None


class EcritureComptableOut(Schema):
    id: UUID
    type_ecriture: str
    montant: Decimal
    libelle: str
    created_at: datetime


def _serialize_facture(f: Facture) -> FactureOut:
    patient = f.hospitalisation.patient
    return FactureOut(
        id=f.id,
        hospitalisation_id=f.hospitalisation_id,
        patient_id=patient.id,
        numero_dossier=patient.numero_dossier,
        patient_nom=f'{patient.prenom} {patient.nom}',
        numero_facture=f.numero_facture,
        statut=f.statut,
        montant_total=f.montant_total,
        montant_paye=f.montant_paye,
        tiers_payant_organisme=f.tiers_payant_organisme,
        tiers_payant_montant=f.tiers_payant_montant,
        montant_restant=f.montant_restant,
        lignes=[
            LigneFactureOut(
                id=l.id,
                code_acte=l.code_acte,
                libelle=l.libelle,
                quantite=l.quantite,
                prix_unitaire=l.prix_unitaire,
                montant_ligne=l.montant_ligne,
                source=l.source,
            )
            for l in f.lignes.all()
        ],
        validee_le=f.validee_le,
        payee_le=f.payee_le,
        mode_paiement=f.mode_paiement,
        reference_paiement=f.reference_paiement,
        version=f.version,
        est_verrouillee=f.est_verrouillee,
        created_at=f.created_at,
    )


@router.get('/facturation/tarifs/', response=list[TarifActeOut], auth=jwt_auth)
@paginate
def list_tarifs(request):
    _check_read(request.auth)
    return [
        TarifActeOut(
            code=t.code,
            libelle=t.libelle,
            categorie=t.categorie,
            prix_unitaire=t.prix_unitaire,
        )
        for t in TarifActe.objects.filter(actif=True)
    ]


@router.get('/facturation/hospitalisations-a-facturer/', response=list[HospitalisationAFacturerOut], auth=jwt_auth)
@paginate
def hospitalisations_a_facturer(request):
    _check_comptable(request.auth)
    qs = Hospitalisation.objects.filter(
        statut__in=[StatutHospitalisation.ACTIVE, StatutHospitalisation.SORTIE],
    ).select_related('patient', 'facture').order_by('-date_admission')

    results = []
    for h in qs:
        patient = h.patient
        facture = getattr(h, 'facture', None)
        if facture and facture.statut == StatutFacture.PAYEE:
            continue
        results.append(
            HospitalisationAFacturerOut(
                hospitalisation_id=h.id,
                patient_id=patient.id,
                numero_dossier=patient.numero_dossier,
                patient_nom=f'{patient.prenom} {patient.nom}',
                statut_hospitalisation=h.statut,
                facture_id=facture.id if facture else None,
                facture_statut=facture.statut if facture else None,
                montant_total=facture.montant_total if facture else None,
            )
        )
    return results


@router.get('/facturation/factures/', response=list[FactureOut], auth=jwt_auth)
@paginate
def list_factures(request, statut: Optional[str] = None):
    _check_read(request.auth)
    qs = Facture.objects.select_related(
        'hospitalisation__patient',
    ).prefetch_related('lignes')
    if statut:
        qs = qs.filter(statut=statut)
    return [_serialize_facture(f) for f in qs]


@router.get('/facturation/factures/{facture_id}/', response=FactureOut, auth=jwt_auth)
def get_facture_detail(request, facture_id: UUID):
    _check_read(request.auth)
    try:
        facture = get_facture(facture_id)
    except FacturationError as exc:
        _handle_error(exc)
    return _serialize_facture(facture)


@router.get('/hospitalisations/{hospitalisation_id}/facture/', response=FactureOut, auth=jwt_auth)
def get_facture_hospitalisation(request, hospitalisation_id: UUID):
    _check_read(request.auth)
    try:
        facture = Facture.objects.select_related(
            'hospitalisation__patient',
        ).prefetch_related('lignes').get(hospitalisation_id=hospitalisation_id)
    except Facture.DoesNotExist:
        raise HttpError(404, 'Aucune facture pour cette hospitalisation.')
    return _serialize_facture(facture)


@router.post('/hospitalisations/{hospitalisation_id}/facture/generer/', response=FactureOut, auth=jwt_auth)
def generer_facture_endpoint(request, hospitalisation_id: UUID):
    _check_comptable(request.auth)
    try:
        hospitalisation = Hospitalisation.objects.get(id=hospitalisation_id)
        facture = generer_facture(
            hospitalisation=hospitalisation,
            comptable=request.auth,
        )
    except Hospitalisation.DoesNotExist:
        raise HttpError(404, 'Hospitalisation introuvable.')
    except FacturationError as exc:
        _handle_error(exc)

    facture = get_facture(facture.id)
    data = _serialize_facture(facture)
    log_audit(
        user=request.auth,
        action='CREATE',
        model_name='Facture',
        object_id=facture.id,
        new_value=data.model_dump(mode='json'),
        ip_address=get_client_ip(request),
    )
    return data


@router.post('/facturation/factures/{facture_id}/valider/', response=FactureOut, auth=jwt_auth)
def valider_facture_endpoint(request, facture_id: UUID, payload: VersionIn):
    _check_comptable(request.auth)
    try:
        facture = get_facture(facture_id)
        facture = valider_facture(
            facture=facture,
            comptable=request.auth,
            version=payload.version,
        )
    except FacturationError as exc:
        _handle_error(exc)

    facture = get_facture(facture.id)
    data = _serialize_facture(facture)
    log_audit(
        user=request.auth,
        action='UPDATE',
        model_name='Facture',
        object_id=facture.id,
        new_value={**data.model_dump(mode='json'), 'event': 'validation'},
        ip_address=get_client_ip(request),
    )
    return data


@router.post('/facturation/factures/{facture_id}/paiement/', response=FactureOut, auth=jwt_auth)
def paiement_facture_endpoint(request, facture_id: UUID, payload: PaiementIn):
    _check_comptable(request.auth)
    try:
        facture = get_facture(facture_id)
        facture = enregistrer_paiement(
            facture=facture,
            comptable=request.auth,
            version=payload.version,
            mode_paiement=payload.mode_paiement,
            reference_paiement=payload.reference_paiement,
            montant=payload.montant,
            tiers_payant_organisme=payload.tiers_payant_organisme,
            tiers_payant_montant=payload.tiers_payant_montant,
        )
    except FacturationError as exc:
        _handle_error(exc)

    facture = get_facture(facture.id)
    data = _serialize_facture(facture)
    log_audit(
        user=request.auth,
        action='UPDATE',
        model_name='Facture',
        object_id=facture.id,
        new_value={**data.model_dump(mode='json'), 'event': 'paiement'},
        ip_address=get_client_ip(request),
    )
    return data


@router.get(
    '/facturation/factures/{facture_id}/journal/',
    response=list[EcritureComptableOut],
    auth=jwt_auth,
)
def journal_facture(request, facture_id: UUID):
    _check_comptable(request.auth)
    try:
        facture = get_facture(facture_id)
    except FacturationError as exc:
        _handle_error(exc)
    return [
        EcritureComptableOut(
            id=e.id,
            type_ecriture=e.type_ecriture,
            montant=e.montant,
            libelle=e.libelle,
            created_at=e.created_at,
        )
        for e in EcritureComptable.objects.filter(facture=facture).order_by('created_at')
    ]
