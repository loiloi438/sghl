from ninja import Router, Schema
from ninja.errors import HttpError

from accounts.models import Role, User
from api.v1.auth_backend import JWTAuth
from core.dashboard_services import indicateurs_tableau_de_bord

router = Router(tags=['Tableau de bord'])
jwt_auth = JWTAuth()

ROLES_DASHBOARD = {
    Role.ADMIN,
    Role.MEDECIN,
    Role.INFIRMIER,
    Role.BIOLOGISTE,
    Role.PHARMACIEN,
    Role.COMPTABLE,
}


class DashboardStatsOut(Schema):
    patients_actifs: int
    rdv_aujourdhui: int
    rdv_planifies: int
    prescriptions_en_attente: int


def _check_dashboard(user: User):
    if user.role not in ROLES_DASHBOARD:
        raise HttpError(403, 'Accès refusé.')


@router.get('/dashboard/stats/', response=DashboardStatsOut, auth=jwt_auth)
def stats_tableau_de_bord(request):
    _check_dashboard(request.auth)
    return DashboardStatsOut(**indicateurs_tableau_de_bord())
