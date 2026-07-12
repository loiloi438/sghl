from csv import writer
from datetime import date
from io import StringIO

from django.http import HttpResponse
from ninja import Router, Schema

from accounts.models import Role, User
from api.v1.auth_backend import JWTAuth
from core.dashboard_services import generer_rapport_statistiques
from documents.pdf_builder import build_rapport_statistiques_pdf

router = Router(tags=['Statistiques'])
jwt_auth = JWTAuth()

ROLES_STATISTIQUES = {Role.ADMIN, Role.COMPTABLE, Role.MEDECIN, Role.SECRETAIRE}


class KPIOut(Schema):
    admissions: int
    rendez_vous: int
    prescriptions: int
    factures: int
    lits_actifs: int
    lits_occupes: int
    taux_occupation: float
    factures_validees: int
    factures_partiellement_payees: int
    factures_payees: int


class JourStatOut(Schema):
    date: date
    admissions: int
    rendez_vous: int
    prescriptions: int
    factures: int


class ServiceStatOut(Schema):
    service: str
    code_service: str
    count: int


class StatutStatOut(Schema):
    statut: str
    count: int


class RapportOut(Schema):
    date_debut: date
    date_fin: date
    kpis: KPIOut
    evolution_journaliere: list[JourStatOut]
    hospitalisations_par_service: list[ServiceStatOut]
    rendez_vous_par_statut: list[StatutStatOut]
    factures_par_statut: list[StatutStatOut]
    prescriptions_par_statut: list[StatutStatOut]


def _check(user: User):
    if user.role not in ROLES_STATISTIQUES:
        from ninja.errors import HttpError

        raise HttpError(403, 'Accès refusé.')


def _resolve_period(start_date: date | None, end_date: date | None) -> tuple[date, date]:
    today = date.today()
    if start_date is None and end_date is None:
        start_date = today.replace(day=1)
        end_date = today
    elif start_date is None:
        start_date = end_date
    elif end_date is None:
        end_date = start_date
    if start_date > end_date:
        from ninja.errors import HttpError

        raise HttpError(400, 'La date de début doit précéder la date de fin.')
    return start_date, end_date


@router.get('/statistiques/rapport/', response=RapportOut, auth=jwt_auth)
def rapport(request, start_date: date | None = None, end_date: date | None = None):
    _check(request.auth)
    start_date, end_date = _resolve_period(start_date, end_date)
    return RapportOut(**generer_rapport_statistiques(start_date, end_date))


@router.get('/statistiques/rapport/pdf/', auth=jwt_auth)
def rapport_pdf(request, start_date: date | None = None, end_date: date | None = None):
    _check(request.auth)
    start_date, end_date = _resolve_period(start_date, end_date)
    rapport_data = generer_rapport_statistiques(start_date, end_date)
    pdf = build_rapport_statistiques_pdf(rapport_data, demandeur=request.auth)
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="rapport-statistiques-{start_date.isoformat()}-{end_date.isoformat()}.pdf"'
    )
    return response


@router.get('/statistiques/rapport/csv/', auth=jwt_auth)
def rapport_csv(request, start_date: date | None = None, end_date: date | None = None):
    _check(request.auth)
    start_date, end_date = _resolve_period(start_date, end_date)
    rapport_data = generer_rapport_statistiques(start_date, end_date)

    buffer = StringIO()
    csv_writer = writer(buffer)
    csv_writer.writerow(['date', 'admissions', 'rendez_vous', 'prescriptions', 'factures'])
    for row in rapport_data['evolution_journaliere']:
        csv_writer.writerow([
            row['date'].isoformat(),
            row['admissions'],
            row['rendez_vous'],
            row['prescriptions'],
            row['factures'],
        ])

    response = HttpResponse(buffer.getvalue(), content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = (
        f'attachment; filename="rapport-statistiques-{start_date.isoformat()}-{end_date.isoformat()}.csv"'
    )
    return response