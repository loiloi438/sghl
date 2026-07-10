from datetime import date, datetime, timedelta

from django.db import transaction
from django.db.models import Count
from django.utils import timezone

from accounts.models import Role, User
from logistics.models import Service
from rh.models import (
    Certification,
    CertificationPersonnel,
    Formation,
    Garde,
    InscriptionFormation,
    StatutFormation,
    StatutInscription,
)


STAFF_ROLES = {
    Role.ADMIN,
    Role.MEDECIN,
    Role.INFIRMIER,
    Role.BIOLOGISTE,
    Role.PHARMACIEN,
}


class RhError(Exception):
    def __init__(self, message: str, code: str = 'error'):
        self.message = message
        self.code = code
        super().__init__(message)


def assert_admin(user: User):
    if user.role != Role.ADMIN:
        raise RhError('Accès réservé à l’administrateur.', code='acces_refuse')


def _assert_staff_user(user: User):
    if user.role not in STAFF_ROLES:
        raise RhError('Personnel invalide.', code='personnel_invalide')


def _verifier_dates_formation(date_debut: date, date_fin: date):
    if date_fin < date_debut:
        raise RhError('La date de fin doit être postérieure à la date de début.', code='dates_invalides')


def _verifier_creneau_garde(
    *,
    personnel: User,
    date_debut: datetime,
    date_fin: datetime,
    exclude_id=None,
):
    if date_fin <= date_debut:
        raise RhError('La fin de garde doit être postérieure au début.', code='dates_invalides')
    qs = Garde.objects.filter(personnel=personnel)
    if exclude_id:
        qs = qs.exclude(id=exclude_id)
    for garde in qs:
        if date_debut < garde.date_fin and date_fin > garde.date_debut:
            raise RhError(
                'Ce personnel a déjà une garde sur ce créneau.',
                code='creneau_indisponible',
            )


@transaction.atomic
def creer_formation(
    *,
    titre: str,
    formateur: str,
    date_debut: date,
    date_fin: date,
    capacite_max: int = 20,
    description: str = '',
) -> Formation:
    _verifier_dates_formation(date_debut, date_fin)
    return Formation.objects.create(
        titre=titre,
        formateur=formateur,
        date_debut=date_debut,
        date_fin=date_fin,
        capacite_max=capacite_max,
        description=description,
    )


@transaction.atomic
def modifier_formation(
    *,
    formation: Formation,
    version: int,
    **fields,
) -> Formation:
    if formation.version != version:
        raise RhError('Conflit de version.', code='version_conflict')
    date_debut = fields.get('date_debut', formation.date_debut)
    date_fin = fields.get('date_fin', formation.date_fin)
    _verifier_dates_formation(date_debut, date_fin)
    for key, value in fields.items():
        if value is not None:
            setattr(formation, key, value)
    formation.bump_version()
    formation.save()
    return formation


@transaction.atomic
def changer_statut_formation(
    *,
    formation: Formation,
    version: int,
    statut: str,
) -> Formation:
    if formation.version != version:
        raise RhError('Conflit de version.', code='version_conflict')
    if statut not in StatutFormation.values:
        raise RhError('Statut invalide.', code='statut_invalide')
    formation.statut = statut
    formation.bump_version()
    formation.save(update_fields=['statut', 'version', 'updated_at'])
    return formation


@transaction.atomic
def inscrire_personnel(
    *,
    formation: Formation,
    personnel: User,
) -> InscriptionFormation:
    if formation.statut == StatutFormation.ANNULEE:
        raise RhError('Formation annulée.', code='statut_invalide')
    if formation.inscriptions.count() >= formation.capacite_max:
        raise RhError('Capacité maximale atteinte.', code='capacite_atteinte')
    _assert_staff_user(personnel)
    inscription, created = InscriptionFormation.objects.get_or_create(
        formation=formation,
        personnel=personnel,
    )
    if not created:
        raise RhError('Personnel déjà inscrit.', code='deja_inscrit')
    return inscription


@transaction.atomic
def valider_inscription(
    *,
    inscription: InscriptionFormation,
) -> InscriptionFormation:
    inscription.statut = StatutInscription.VALIDE
    inscription.save(update_fields=['statut', 'updated_at'])
    return inscription


@transaction.atomic
def creer_certification_catalogue(
    *,
    nom: str,
    type_certification: str,
    duree_validite_mois: int | None = None,
    description: str = '',
) -> Certification:
    return Certification.objects.create(
        nom=nom,
        type_certification=type_certification,
        duree_validite_mois=duree_validite_mois,
        description=description,
    )


@transaction.atomic
def attribuer_certification(
    *,
    certification: Certification,
    personnel: User,
    date_obtention: date,
    date_expiration: date,
    numero_certificat: str = '',
) -> CertificationPersonnel:
    _assert_staff_user(personnel)
    if date_expiration < date_obtention:
        raise RhError('Date d’expiration invalide.', code='dates_invalides')
    return CertificationPersonnel.objects.create(
        certification=certification,
        personnel=personnel,
        date_obtention=date_obtention,
        date_expiration=date_expiration,
        numero_certificat=numero_certificat,
    )


@transaction.atomic
def renouveler_certification(
    *,
    cert_personnel: CertificationPersonnel,
    version: int,
    date_obtention: date,
    date_expiration: date,
    numero_certificat: str = '',
) -> CertificationPersonnel:
    if cert_personnel.version != version:
        raise RhError('Conflit de version.', code='version_conflict')
    if date_expiration < date_obtention:
        raise RhError('Date d’expiration invalide.', code='dates_invalides')
    cert_personnel.date_obtention = date_obtention
    cert_personnel.date_expiration = date_expiration
    if numero_certificat:
        cert_personnel.numero_certificat = numero_certificat
    cert_personnel.bump_version()
    cert_personnel.save()
    return cert_personnel


@transaction.atomic
def creer_garde(
    *,
    personnel: User,
    type_garde: str,
    date_debut: datetime,
    date_fin: datetime,
    service: Service | None = None,
    notes: str = '',
) -> Garde:
    _assert_staff_user(personnel)
    _verifier_creneau_garde(
        personnel=personnel,
        date_debut=date_debut,
        date_fin=date_fin,
    )
    return Garde.objects.create(
        personnel=personnel,
        service=service,
        type_garde=type_garde,
        date_debut=date_debut,
        date_fin=date_fin,
        notes=notes,
    )


@transaction.atomic
def modifier_garde(
    *,
    garde: Garde,
    version: int,
    **fields,
) -> Garde:
    if garde.version != version:
        raise RhError('Conflit de version.', code='version_conflict')
    date_debut = fields.get('date_debut', garde.date_debut)
    date_fin = fields.get('date_fin', garde.date_fin)
    personnel = fields.get('personnel', garde.personnel)
    _verifier_creneau_garde(
        personnel=personnel,
        date_debut=date_debut,
        date_fin=date_fin,
        exclude_id=garde.id,
    )
    for key, value in fields.items():
        if value is not None:
            setattr(garde, key, value)
    garde.bump_version()
    garde.save()
    return garde


@transaction.atomic
def supprimer_garde(*, garde: Garde, version: int):
    if garde.version != version:
        raise RhError('Conflit de version.', code='version_conflict')
    garde.delete()


def compter_gardes_semaine(debut: date) -> list[dict]:
    fin = debut + timedelta(days=6)
    counts = (
        Garde.objects.filter(
            date_debut__date__gte=debut,
            date_debut__date__lte=fin,
        )
        .values('date_debut__date')
        .annotate(count=Count('id'))
    )
    count_map = {row['date_debut__date']: row['count'] for row in counts}
    return [
        {'date': (debut + timedelta(days=i)).isoformat(), 'count': count_map.get(debut + timedelta(days=i), 0)}
        for i in range(7)
    ]


def stats_rh() -> dict:
    today = date.today()
    staff_qs = User.objects.filter(role__in=STAFF_ROLES)
    staff_count = staff_qs.count()
    formations_actives = Formation.objects.filter(
        statut__in={StatutFormation.PROGRAMMEE, StatutFormation.EN_COURS},
    ).count()
    certs_a_renouveler = CertificationPersonnel.objects.filter(
        date_expiration__lte=today + timedelta(days=90),
    ).count()
    conformes = 0
    for user in staff_qs:
        certs = user.certifications.all()
        if not certs.exists():
            continue
        if all(not c.est_expiree for c in certs):
            conformes += 1
    qualified_pct = round((conformes / staff_count) * 100) if staff_count else 0
    gardes_semaine = Garde.objects.filter(
        date_debut__gte=timezone.now(),
        date_debut__lt=timezone.now() + timedelta(days=7),
    ).count()
    return {
        'formations_actives': formations_actives,
        'personnel_qualifie_pct': qualified_pct,
        'certifications_a_renouveler': certs_a_renouveler,
        'gardes_semaine': gardes_semaine,
        'effectif_staff': staff_count,
    }


def personnel_conformite() -> list[dict]:
    today = date.today()
    staff = User.objects.filter(role__in=STAFF_ROLES).order_by('last_name', 'first_name')
    result = []
    for user in staff:
        certs = list(user.certifications.select_related('certification'))
        inscriptions = user.inscriptions_formation.filter(statut=StatutInscription.VALIDE)
        active_certs = [c for c in certs if not c.est_expiree]
        compliant = bool(active_certs) and all(not c.est_expiree for c in certs)
        result.append({
            'id': user.id,
            'full_name': f'{user.first_name} {user.last_name}'.strip() or user.username,
            'role': user.role,
            'role_label': user.get_role_display(),
            'trainings_completed': inscriptions.count(),
            'active_certs': len(active_certs),
            'compliant': compliant,
            'certs_expiring_soon': sum(1 for c in certs if c.a_renouveler and not c.est_expiree),
        })
    return result
