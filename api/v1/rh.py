from datetime import date, datetime, timedelta
from typing import Optional
from uuid import UUID

from django.utils import timezone
from ninja import Router, Schema
from ninja.errors import HttpError

from accounts.models import Role, User
from api.v1.auth_backend import JWTAuth
from api.v1.personnel import get_default_profile_photo
from audit.services import get_client_ip, log_audit
from logistics.models import Service
from rh.models import (
    Certification,
    CertificationPersonnel,
    Formation,
    Garde,
    InscriptionFormation,
    StatutFormation,
)
from rh.services import (
    RhError,
    assert_admin,
    attribuer_certification,
    changer_statut_formation,
    compter_gardes_semaine,
    creer_certification_catalogue,
    creer_formation,
    creer_garde,
    inscrire_personnel,
    modifier_formation,
    modifier_garde,
    personnel_conformite,
    renouveler_certification,
    stats_rh,
    supprimer_garde,
    valider_inscription,
)

router = Router(tags=['RH'])
jwt_auth = JWTAuth()


def _handle_error(exc: RhError):
    status_map = {
        'not_found': 404,
        'version_conflict': 409,
        'acces_refuse': 403,
        'creneau_indisponible': 409,
        'dates_invalides': 400,
        'statut_invalide': 400,
        'personnel_invalide': 400,
        'capacite_atteinte': 409,
        'deja_inscrit': 409,
    }
    raise HttpError(status_map.get(exc.code, 400), exc.message)


def _check_admin(user: User):
    try:
        assert_admin(user)
    except RhError as exc:
        _handle_error(exc)


class StatsRhOut(Schema):
    formations_actives: int
    personnel_qualifie_pct: int
    certifications_a_renouveler: int
    gardes_semaine: int
    effectif_staff: int


class FormationOut(Schema):
    id: UUID
    titre: str
    formateur: str
    date_debut: date
    date_fin: date
    capacite_max: int
    participants_count: int
    statut: str
    statut_label: str
    description: str
    version: int


class FormationIn(Schema):
    titre: str
    formateur: str
    date_debut: date
    date_fin: date
    capacite_max: int = 20
    description: str = ''


class FormationUpdateIn(Schema):
    version: int
    titre: Optional[str] = None
    formateur: Optional[str] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    capacite_max: Optional[int] = None
    description: Optional[str] = None


class StatutFormationIn(Schema):
    version: int
    statut: str


class InscriptionIn(Schema):
    personnel_id: int


class CertificationCatalogueOut(Schema):
    id: UUID
    nom: str
    type_certification: str
    duree_validite_mois: Optional[int]
    holders_count: int
    expiration_moyenne: Optional[date]
    renewal_status: str


class CertificationCatalogueIn(Schema):
    nom: str
    type_certification: str
    duree_validite_mois: Optional[int] = None
    description: str = ''


class CertificationPersonnelOut(Schema):
    id: UUID
    certification_id: UUID
    certification_nom: str
    personnel_id: int
    personnel_nom: str
    date_obtention: date
    date_expiration: date
    numero_certificat: str
    statut_renouvellement: str
    version: int


class CertificationPersonnelIn(Schema):
    certification_id: UUID
    personnel_id: int
    date_obtention: date
    date_expiration: date
    numero_certificat: str = ''


class RenouvelerCertIn(Schema):
    version: int
    date_obtention: date
    date_expiration: date
    numero_certificat: str = ''


class PersonnelConformiteOut(Schema):
    id: int
    full_name: str
    role: str
    role_label: str
    trainings_completed: int
    active_certs: int
    compliant: bool
    certs_expiring_soon: int
    photo_url: str


class GardeOut(Schema):
    id: UUID
    personnel_id: int
    personnel_nom: str
    service_id: Optional[UUID]
    service_nom: Optional[str]
    type_garde: str
    type_garde_label: str
    date_debut: datetime
    date_fin: datetime
    notes: str
    version: int


class GardeIn(Schema):
    personnel_id: int
    type_garde: str
    date_debut: datetime
    date_fin: datetime
    service_id: Optional[UUID] = None
    notes: str = ''


class GardeUpdateIn(Schema):
    version: int
    personnel_id: Optional[int] = None
    type_garde: Optional[str] = None
    date_debut: Optional[datetime] = None
    date_fin: Optional[datetime] = None
    service_id: Optional[UUID] = None
    notes: Optional[str] = None


class JourSemaineOut(Schema):
    date: str
    count: int


class StaffOptionOut(Schema):
    id: int
    full_name: str
    role: str
    role_label: str


def _serialize_formation(f: Formation) -> FormationOut:
    return FormationOut(
        id=f.id,
        titre=f.titre,
        formateur=f.formateur,
        date_debut=f.date_debut,
        date_fin=f.date_fin,
        capacite_max=f.capacite_max,
        participants_count=f.participants_count,
        statut=f.statut,
        statut_label=f.get_statut_display(),
        description=f.description,
        version=f.version,
    )


def _serialize_cert_catalogue(c: Certification) -> CertificationCatalogueOut:
    detenteurs = list(c.detenteurs.all())
    holders = len(detenteurs)
    exp_dates = [d.date_expiration for d in detenteurs if d.date_expiration]
    exp_moy = None
    if exp_dates:
        avg_ord = sum(d.toordinal() for d in exp_dates) // len(exp_dates)
        exp_moy = date.fromordinal(avg_ord)
    a_renouveler = any(d.a_renouveler for d in detenteurs)
    return CertificationCatalogueOut(
        id=c.id,
        nom=c.nom,
        type_certification=c.type_certification,
        duree_validite_mois=c.duree_validite_mois,
        holders_count=holders,
        expiration_moyenne=exp_moy,
        renewal_status='À renouveler' if a_renouveler else 'En cours',
    )


def _serialize_cert_personnel(cp: CertificationPersonnel) -> CertificationPersonnelOut:
    return CertificationPersonnelOut(
        id=cp.id,
        certification_id=cp.certification_id,
        certification_nom=cp.certification.nom,
        personnel_id=cp.personnel_id,
        personnel_nom=f'{cp.personnel.first_name} {cp.personnel.last_name}'.strip() or cp.personnel.username,
        date_obtention=cp.date_obtention,
        date_expiration=cp.date_expiration,
        numero_certificat=cp.numero_certificat,
        statut_renouvellement=cp.statut_renouvellement,
        version=cp.version,
    )


def _serialize_garde(g: Garde) -> GardeOut:
    return GardeOut(
        id=g.id,
        personnel_id=g.personnel_id,
        personnel_nom=f'{g.personnel.first_name} {g.personnel.last_name}'.strip() or g.personnel.username,
        service_id=g.service_id,
        service_nom=str(g.service) if g.service else None,
        type_garde=g.type_garde,
        type_garde_label=g.get_type_garde_display(),
        date_debut=g.date_debut,
        date_fin=g.date_fin,
        notes=g.notes,
        version=g.version,
    )


@router.get('/rh/stats/', response=StatsRhOut, auth=jwt_auth)
def rh_stats(request):
    _check_admin(request.auth)
    return stats_rh()


@router.get('/rh/formations/', response=list[FormationOut], auth=jwt_auth)
def list_formations(request, statut: str | None = None):
    _check_admin(request.auth)
    qs = Formation.objects.all()
    if statut:
        qs = qs.filter(statut=statut)
    return [_serialize_formation(f) for f in qs]


@router.post('/rh/formations/', response=FormationOut, auth=jwt_auth)
def create_formation(request, payload: FormationIn):
    _check_admin(request.auth)
    try:
        formation = creer_formation(**payload.dict())
    except RhError as exc:
        _handle_error(exc)
    log_audit(
        user=request.auth,
        action='create',
        model_name='Formation',
        object_id=formation.id,
        new_value=payload.dict(),
        ip_address=get_client_ip(request),
    )
    return _serialize_formation(formation)


@router.patch('/rh/formations/{formation_id}/', response=FormationOut, auth=jwt_auth)
def update_formation(request, formation_id: UUID, payload: FormationUpdateIn):
    _check_admin(request.auth)
    try:
        formation = Formation.objects.get(id=formation_id)
    except Formation.DoesNotExist:
        raise HttpError(404, 'Formation introuvable.')
    old = _serialize_formation(formation).dict()
    fields = {k: v for k, v in payload.dict(exclude={'version'}).items() if v is not None}
    try:
        formation = modifier_formation(formation=formation, version=payload.version, **fields)
    except RhError as exc:
        _handle_error(exc)
    log_audit(
        user=request.auth,
        action='update',
        model_name='Formation',
        object_id=formation.id,
        old_value=old,
        new_value=_serialize_formation(formation).dict(),
        ip_address=get_client_ip(request),
    )
    return _serialize_formation(formation)


@router.post('/rh/formations/{formation_id}/statut/', response=FormationOut, auth=jwt_auth)
def update_formation_statut(request, formation_id: UUID, payload: StatutFormationIn):
    _check_admin(request.auth)
    try:
        formation = Formation.objects.get(id=formation_id)
    except Formation.DoesNotExist:
        raise HttpError(404, 'Formation introuvable.')
    try:
        formation = changer_statut_formation(
            formation=formation,
            version=payload.version,
            statut=payload.statut,
        )
    except RhError as exc:
        _handle_error(exc)
    return _serialize_formation(formation)


@router.post('/rh/formations/{formation_id}/inscriptions/', auth=jwt_auth)
def add_inscription(request, formation_id: UUID, payload: InscriptionIn):
    _check_admin(request.auth)
    try:
        formation = Formation.objects.get(id=formation_id)
        personnel = User.objects.get(id=payload.personnel_id)
    except Formation.DoesNotExist:
        raise HttpError(404, 'Formation introuvable.')
    except User.DoesNotExist:
        raise HttpError(404, 'Personnel introuvable.')
    try:
        inscription = inscrire_personnel(formation=formation, personnel=personnel)
    except RhError as exc:
        _handle_error(exc)
    log_audit(
        user=request.auth,
        action='create',
        model_name='InscriptionFormation',
        object_id=inscription.id,
        new_value={'formation_id': str(formation_id), 'personnel_id': payload.personnel_id},
        ip_address=get_client_ip(request),
    )
    return {'detail': 'Inscription enregistrée.'}


@router.post('/rh/formations/{formation_id}/inscriptions/{inscription_id}/valider/', auth=jwt_auth)
def validate_inscription(request, formation_id: UUID, inscription_id: UUID):
    _check_admin(request.auth)
    try:
        inscription = InscriptionFormation.objects.select_related('formation', 'personnel').get(
            id=inscription_id,
            formation_id=formation_id,
        )
    except InscriptionFormation.DoesNotExist:
        raise HttpError(404, 'Inscription introuvable.')
    inscription = valider_inscription(inscription=inscription)
    log_audit(
        user=request.auth,
        action='update',
        model_name='InscriptionFormation',
        object_id=inscription.id,
        new_value={'statut': inscription.statut},
        ip_address=get_client_ip(request),
    )
    return {'detail': 'Inscription validée.', 'statut': inscription.statut}


class InscriptionOut(Schema):
    id: UUID
    personnel_id: int
    personnel_nom: str
    statut: str


@router.get('/rh/formations/{formation_id}/inscriptions/', response=list[InscriptionOut], auth=jwt_auth)
def list_formation_inscriptions(request, formation_id: UUID):
    _check_admin(request.auth)
    try:
        formation = Formation.objects.get(id=formation_id)
    except Formation.DoesNotExist:
        raise HttpError(404, 'Formation introuvable.')
    return [
        InscriptionOut(
            id=ins.id,
            personnel_id=ins.personnel_id,
            personnel_nom=f'{ins.personnel.first_name} {ins.personnel.last_name}'.strip() or ins.personnel.username,
            statut=ins.statut,
        )
        for ins in formation.inscriptions.select_related('personnel')
    ]


@router.get('/rh/certifications/', response=list[CertificationCatalogueOut], auth=jwt_auth)
def list_certifications(request):
    _check_admin(request.auth)
    certs = Certification.objects.prefetch_related('detenteurs').all()
    return [_serialize_cert_catalogue(c) for c in certs]


@router.post('/rh/certifications/', response=CertificationCatalogueOut, auth=jwt_auth)
def create_certification(request, payload: CertificationCatalogueIn):
    _check_admin(request.auth)
    cert = creer_certification_catalogue(**payload.dict())
    log_audit(
        user=request.auth,
        action='create',
        model_name='Certification',
        object_id=cert.id,
        new_value=payload.dict(),
        ip_address=get_client_ip(request),
    )
    return _serialize_cert_catalogue(cert)


@router.get('/rh/certifications/personnel/', response=list[CertificationPersonnelOut], auth=jwt_auth)
def list_certifications_personnel(request, personnel_id: int | None = None):
    _check_admin(request.auth)
    qs = CertificationPersonnel.objects.select_related('certification', 'personnel')
    if personnel_id:
        qs = qs.filter(personnel_id=personnel_id)
    return [_serialize_cert_personnel(cp) for cp in qs]


@router.post('/rh/certifications/personnel/', response=CertificationPersonnelOut, auth=jwt_auth)
def assign_certification(request, payload: CertificationPersonnelIn):
    _check_admin(request.auth)
    try:
        certification = Certification.objects.get(id=payload.certification_id)
        personnel = User.objects.get(id=payload.personnel_id)
    except Certification.DoesNotExist:
        raise HttpError(404, 'Certification introuvable.')
    except User.DoesNotExist:
        raise HttpError(404, 'Personnel introuvable.')
    try:
        cp = attribuer_certification(
            certification=certification,
            personnel=personnel,
            date_obtention=payload.date_obtention,
            date_expiration=payload.date_expiration,
            numero_certificat=payload.numero_certificat,
        )
    except RhError as exc:
        _handle_error(exc)
    log_audit(
        user=request.auth,
        action='create',
        model_name='CertificationPersonnel',
        object_id=cp.id,
        new_value=payload.dict(),
        ip_address=get_client_ip(request),
    )
    return _serialize_cert_personnel(cp)


@router.post(
    '/rh/certifications/personnel/{cert_id}/renouveler/',
    response=CertificationPersonnelOut,
    auth=jwt_auth,
)
def renew_certification_endpoint(request, cert_id: UUID, payload: RenouvelerCertIn):
    _check_admin(request.auth)
    try:
        cp = CertificationPersonnel.objects.select_related('certification', 'personnel').get(id=cert_id)
    except CertificationPersonnel.DoesNotExist:
        raise HttpError(404, 'Certification personnel introuvable.')
    try:
        cp = renouveler_certification(
            cert_personnel=cp,
            version=payload.version,
            date_obtention=payload.date_obtention,
            date_expiration=payload.date_expiration,
            numero_certificat=payload.numero_certificat,
        )
    except RhError as exc:
        _handle_error(exc)
    log_audit(
        user=request.auth,
        action='update',
        model_name='CertificationPersonnel',
        object_id=cp.id,
        new_value={'action': 'renouvellement', **payload.dict()},
        ip_address=get_client_ip(request),
    )
    return _serialize_cert_personnel(cp)


@router.get('/rh/personnel/', response=list[PersonnelConformiteOut], auth=jwt_auth)
def list_personnel_conformite(request):
    _check_admin(request.auth)
    rows = personnel_conformite()
    return [
        PersonnelConformiteOut(
            **row,
            photo_url=get_default_profile_photo(User.objects.get(id=row['id'])),
        )
        for row in rows
    ]


@router.get('/rh/staff/', response=list[StaffOptionOut], auth=jwt_auth)
def list_staff_options(request):
    _check_admin(request.auth)
    staff_roles = {Role.MEDECIN, Role.INFIRMIER, Role.BIOLOGISTE, Role.PHARMACIEN, Role.ADMIN}
    users = User.objects.filter(role__in=staff_roles).order_by('last_name', 'first_name')
    return [
        StaffOptionOut(
            id=u.id,
            full_name=f'{u.first_name} {u.last_name}'.strip() or u.username,
            role=u.role,
            role_label=u.get_role_display(),
        )
        for u in users
    ]


@router.get('/rh/gardes/', response=list[GardeOut], auth=jwt_auth)
def list_gardes(
    request,
    date_debut: date | None = None,
    date_fin: date | None = None,
    personnel_id: int | None = None,
):
    _check_admin(request.auth)
    qs = Garde.objects.select_related('personnel', 'service').all()
    if date_debut:
        qs = qs.filter(date_debut__date__gte=date_debut)
    if date_fin:
        qs = qs.filter(date_debut__date__lte=date_fin)
    if personnel_id:
        qs = qs.filter(personnel_id=personnel_id)
    return [_serialize_garde(g) for g in qs]


@router.get('/rh/gardes/semaine/', response=list[JourSemaineOut], auth=jwt_auth)
def gardes_semaine(request, debut: date | None = None):
    _check_admin(request.auth)
    if debut is None:
        today = timezone.localdate()
        debut = today - timedelta(days=today.weekday())
    return compter_gardes_semaine(debut)


@router.post('/rh/gardes/', response=GardeOut, auth=jwt_auth)
def create_garde(request, payload: GardeIn):
    _check_admin(request.auth)
    try:
        personnel = User.objects.get(id=payload.personnel_id)
    except User.DoesNotExist:
        raise HttpError(404, 'Personnel introuvable.')
    service = None
    if payload.service_id:
        try:
            service = Service.objects.get(id=payload.service_id)
        except Service.DoesNotExist:
            raise HttpError(404, 'Service introuvable.')
    try:
        garde = creer_garde(
            personnel=personnel,
            type_garde=payload.type_garde,
            date_debut=payload.date_debut,
            date_fin=payload.date_fin,
            service=service,
            notes=payload.notes,
        )
    except RhError as exc:
        _handle_error(exc)
    log_audit(
        user=request.auth,
        action='create',
        model_name='Garde',
        object_id=garde.id,
        new_value=payload.dict(),
        ip_address=get_client_ip(request),
    )
    return _serialize_garde(garde)


@router.patch('/rh/gardes/{garde_id}/', response=GardeOut, auth=jwt_auth)
def update_garde(request, garde_id: UUID, payload: GardeUpdateIn):
    _check_admin(request.auth)
    try:
        garde = Garde.objects.select_related('personnel', 'service').get(id=garde_id)
    except Garde.DoesNotExist:
        raise HttpError(404, 'Garde introuvable.')
    fields = {}
    if payload.personnel_id is not None:
        try:
            fields['personnel'] = User.objects.get(id=payload.personnel_id)
        except User.DoesNotExist:
            raise HttpError(404, 'Personnel introuvable.')
    if payload.type_garde is not None:
        fields['type_garde'] = payload.type_garde
    if payload.date_debut is not None:
        fields['date_debut'] = payload.date_debut
    if payload.date_fin is not None:
        fields['date_fin'] = payload.date_fin
    if payload.notes is not None:
        fields['notes'] = payload.notes
    if payload.service_id is not None:
        if payload.service_id:
            try:
                fields['service'] = Service.objects.get(id=payload.service_id)
            except Service.DoesNotExist:
                raise HttpError(404, 'Service introuvable.')
        else:
            fields['service'] = None
    try:
        garde = modifier_garde(garde=garde, version=payload.version, **fields)
    except RhError as exc:
        _handle_error(exc)
    return _serialize_garde(garde)


@router.delete('/rh/gardes/{garde_id}/', auth=jwt_auth)
def delete_garde(request, garde_id: UUID, version: int):
    _check_admin(request.auth)
    try:
        garde = Garde.objects.get(id=garde_id)
    except Garde.DoesNotExist:
        raise HttpError(404, 'Garde introuvable.')
    try:
        supprimer_garde(garde=garde, version=version)
    except RhError as exc:
        _handle_error(exc)
    log_audit(
        user=request.auth,
        action='delete',
        model_name='Garde',
        object_id=garde_id,
        ip_address=get_client_ip(request),
    )
    return {'detail': 'Garde supprimée.'}
