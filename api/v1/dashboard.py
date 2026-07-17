from datetime import datetime

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from ninja import Router, Schema
from ninja.errors import HttpError

from accounts.models import Role, User
from api.v1.auth_backend import JWTAuth
from core.dashboard_services import cas_a_surveiller, indicateurs_tableau_de_bord, overview_tableau_de_bord
from facturation.models import Facture, StatutFacture
from messagerie.models import MessageInterne

router = Router(tags=['Tableau de bord'])
jwt_auth = JWTAuth()

ROLES_DASHBOARD = {
    Role.ADMIN,
    Role.MEDECIN,
    Role.INFIRMIER,
    Role.BIOLOGISTE,
    Role.PHARMACIEN,
    Role.COMPTABLE,
    Role.SECRETAIRE,
}

ROLES_COMPTES_CREABLES = {
    Role.ADMIN,
    Role.MEDECIN,
    Role.INFIRMIER,
    Role.BIOLOGISTE,
    Role.PHARMACIEN,
    Role.COMPTABLE,
    Role.SECRETAIRE,
}


class CasSurveillerOut(Schema):
    patient_nom: str
    patient_dossier: str
    motif: str
    niveau: str
    service: str


class DashboardStatsOut(Schema):
    patients_actifs: int
    rdv_aujourdhui: int
    rdv_planifies: int
    prescriptions_en_attente: int
    factures_en_attente: int = 0
    messages_non_lus: int = 0


class ChartPointOut(Schema):
    label: str
    value: float
    color: str = '#38bdf8'


class ActivitySeriesOut(Schema):
    label: str
    color: str
    values: list[int]


class ActivityChartOut(Schema):
    labels: list[str]
    series: list[ActivitySeriesOut]


class CompteRecentOut(Schema):
    id: int
    full_name: str
    role: str
    role_label: str
    date_joined: datetime
    is_active: bool


class RdvAValiderOut(Schema):
    id: str
    patient_nom: str
    medecin_nom: str
    date_heure: datetime
    motif: str
    statut: str


class NotificationDashOut(Schema):
    id: str
    titre: str
    corps: str
    categorie: str
    lu: bool
    created_at: datetime


class MessageDashOut(Schema):
    id: str
    sujet: str
    expediteur: str
    lu: bool
    created_at: datetime


class DashboardKpisOut(Schema):
    utilisateurs_actifs: int
    patients_actifs: int
    rdv_aujourdhui: int
    rdv_planifies: int
    prescriptions_en_attente: int
    factures_en_attente: int
    messages_non_lus: int


class DashboardOverviewOut(Schema):
    role: str
    kpis: DashboardKpisOut
    rdv_par_service: list[ChartPointOut]
    paiements_mensuels: list[ChartPointOut]
    activite_personnel: ActivityChartOut
    derniers_comptes: list[CompteRecentOut]
    rdv_a_valider: list[RdvAValiderOut]
    notifications: list[NotificationDashOut]
    messages_du_jour: list[MessageDashOut]
    cas_a_surveiller: list[CasSurveillerOut]


class CompteCreateIn(Schema):
    username: str
    email: str = ''
    first_name: str
    last_name: str
    role: str
    password: str


class CompteOut(Schema):
    id: int
    username: str
    full_name: str
    email: str
    role: str
    role_label: str
    is_active: bool
    date_joined: datetime


def _check_dashboard(user: User):
    if user.role not in ROLES_DASHBOARD:
        raise HttpError(403, 'Accès refusé.')


def _check_admin(user: User):
    if user.role != Role.ADMIN:
        raise HttpError(403, 'Réservé à l’administrateur.')


@router.get('/dashboard/stats/', response=DashboardStatsOut, auth=jwt_auth)
def stats_tableau_de_bord(request):
    _check_dashboard(request.auth)
    stats = indicateurs_tableau_de_bord()
    stats['factures_en_attente'] = Facture.objects.filter(
        statut__in={StatutFacture.VALIDEE, StatutFacture.PARTIELLEMENT_PAYEE},
    ).count()
    stats['messages_non_lus'] = MessageInterne.objects.filter(
        destinataire=request.auth,
        lu=False,
    ).count()
    return DashboardStatsOut(**stats)


@router.get('/dashboard/cas-a-surveiller/', response=list[CasSurveillerOut], auth=jwt_auth)
def list_cas_a_surveiller(request):
    _check_dashboard(request.auth)
    return [CasSurveillerOut(**row) for row in cas_a_surveiller()]


@router.get('/dashboard/overview/', response=DashboardOverviewOut, auth=jwt_auth)
def overview_tableau_de_bord_api(request):
    _check_dashboard(request.auth)
    data = overview_tableau_de_bord(request.auth)
    return DashboardOverviewOut(
        role=data['role'],
        kpis=DashboardKpisOut(**data['kpis']),
        rdv_par_service=[ChartPointOut(**p) for p in data['rdv_par_service']],
        paiements_mensuels=[ChartPointOut(**p) for p in data['paiements_mensuels']],
        activite_personnel=ActivityChartOut(
            labels=data['activite_personnel']['labels'],
            series=[ActivitySeriesOut(**s) for s in data['activite_personnel']['series']],
        ),
        derniers_comptes=[CompteRecentOut(**c) for c in data['derniers_comptes']],
        rdv_a_valider=[RdvAValiderOut(**r) for r in data['rdv_a_valider']],
        notifications=[NotificationDashOut(**n) for n in data['notifications']],
        messages_du_jour=[MessageDashOut(**m) for m in data['messages_du_jour']],
        cas_a_surveiller=[CasSurveillerOut(**c) for c in data['cas_a_surveiller']],
    )


@router.get('/comptes/', response=list[CompteOut], auth=jwt_auth)
def list_comptes(request, role: str | None = None, search: str | None = None):
    _check_admin(request.auth)
    qs = User.objects.all().order_by('-date_joined')
    if role:
        qs = qs.filter(role=role)
    if search:
        from django.db.models import Q

        qs = qs.filter(
            Q(username__icontains=search)
            | Q(first_name__icontains=search)
            | Q(last_name__icontains=search)
            | Q(email__icontains=search)
        )
    return [
        CompteOut(
            id=u.id,
            username=u.username,
            full_name=f'{u.first_name} {u.last_name}'.strip() or u.username,
            email=u.email or '',
            role=u.role,
            role_label=u.get_role_display(),
            is_active=u.is_active,
            date_joined=u.date_joined,
        )
        for u in qs[:100]
    ]


@router.post('/comptes/', response=CompteOut, auth=jwt_auth)
def create_compte(request, payload: CompteCreateIn):
    _check_admin(request.auth)
    role = (payload.role or '').strip().lower()
    if role not in ROLES_COMPTES_CREABLES and role != Role.PATIENT:
        raise HttpError(400, 'Rôle invalide.')
    username = payload.username.strip()
    if not username:
        raise HttpError(400, 'Identifiant requis.')
    if User.objects.filter(username__iexact=username).exists():
        raise HttpError(400, 'Cet identifiant existe déjà.')
    email = (payload.email or '').strip() or None
    if email and User.objects.filter(email__iexact=email).exists():
        raise HttpError(400, 'Cet e-mail est déjà utilisé.')
    try:
        validate_password(payload.password)
    except ValidationError as exc:
        raise HttpError(400, ' '.join(exc.messages)) from exc

    user = User.objects.create_user(
        username=username,
        email=email,
        password=payload.password,
        first_name=payload.first_name.strip(),
        last_name=payload.last_name.strip(),
        role=role,
        is_active=True,
    )
    return CompteOut(
        id=user.id,
        username=user.username,
        full_name=f'{user.first_name} {user.last_name}'.strip() or user.username,
        email=user.email or '',
        role=user.role,
        role_label=user.get_role_display(),
        is_active=user.is_active,
        date_joined=user.date_joined,
    )
