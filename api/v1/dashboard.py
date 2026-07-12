from ninja import Router, Schema
from ninja.errors import HttpError

from accounts.models import Role, User
from api.v1.auth_backend import JWTAuth
from core.dashboard_services import cas_a_surveiller, indicateurs_tableau_de_bord
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


def _check_dashboard(user: User):
    if user.role not in ROLES_DASHBOARD:
        raise HttpError(403, 'Accès refusé.')


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
