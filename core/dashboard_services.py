from datetime import date, timedelta

from django.db.models import Count
from django.db.models.functions import TruncDate

from facturation.models import Facture, StatutFacture
from hospitalisation.models import Hospitalisation, StatutHospitalisation
from logistics.models import Lit, StatutLit
from prescriptions.models import Prescription, StatutPrescription
from rendezvous.models import RendezVous, StatutRendezVous
from rendezvous.services import compter_rdv_jour


def compter_patients_actifs() -> int:
    return Hospitalisation.objects.filter(statut=StatutHospitalisation.ACTIVE).count()


def compter_prescriptions_en_attente() -> int:
    return Prescription.objects.filter(statut=StatutPrescription.BROUILLON).count()


def compter_rdv_planifies() -> int:
    return RendezVous.objects.filter(
        statut__in={StatutRendezVous.PLANIFIE, StatutRendezVous.CONFIRME},
    ).count()


def indicateurs_tableau_de_bord() -> dict:
    return {
        'patients_actifs': compter_patients_actifs(),
        'rdv_aujourdhui': compter_rdv_jour(),
        'rdv_planifies': compter_rdv_planifies(),
        'prescriptions_en_attente': compter_prescriptions_en_attente(),
    }


def _range_days(date_debut: date, date_fin: date):
    courant = date_debut
    while courant <= date_fin:
        yield courant
        courant += timedelta(days=1)


def _count_by_day(queryset, field_name: str, date_debut: date, date_fin: date) -> dict[date, int]:
    rows = (
        queryset.filter(**{f'{field_name}__date__range': (date_debut, date_fin)})
        .annotate(jour=TruncDate(field_name))
        .values('jour')
        .annotate(total=Count('id'))
    )
    return {row['jour']: row['total'] for row in rows}


def generer_rapport_statistiques(date_debut: date, date_fin: date) -> dict:
    admissions = Hospitalisation.objects.filter(
        date_admission__date__range=(date_debut, date_fin)
    )
    rendez_vous = RendezVous.objects.filter(date_heure__date__range=(date_debut, date_fin))
    prescriptions = Prescription.objects.filter(created_at__date__range=(date_debut, date_fin))
    factures = Facture.objects.filter(created_at__date__range=(date_debut, date_fin))

    lits_actifs = Lit.objects.filter(actif=True).count()
    lits_occupes = Hospitalisation.objects.filter(statut=StatutHospitalisation.ACTIVE).values('lit_id').distinct().count()
    taux_occupation = round((lits_occupes / lits_actifs) * 100, 1) if lits_actifs else 0.0

    admissions_par_jour = _count_by_day(admissions, 'date_admission', date_debut, date_fin)
    rendez_vous_par_jour = _count_by_day(rendez_vous, 'date_heure', date_debut, date_fin)
    prescriptions_par_jour = _count_by_day(prescriptions, 'created_at', date_debut, date_fin)
    factures_par_jour = _count_by_day(factures, 'created_at', date_debut, date_fin)

    jours = []
    for jour in _range_days(date_debut, date_fin):
        jours.append(
            {
                'date': jour,
                'admissions': admissions_par_jour.get(jour, 0),
                'rendez_vous': rendez_vous_par_jour.get(jour, 0),
                'prescriptions': prescriptions_par_jour.get(jour, 0),
                'factures': factures_par_jour.get(jour, 0),
            }
        )

    hospitalisations_par_service = [
        {
            'service': row['lit__chambre__service__nom'] or row['lit__chambre__service__code'],
            'code_service': row['lit__chambre__service__code'],
            'count': row['total'],
        }
        for row in admissions.values('lit__chambre__service__nom', 'lit__chambre__service__code').annotate(total=Count('id')).order_by('-total')
    ]

    rendez_vous_par_statut = [
        {'statut': row['statut'], 'count': row['total']}
        for row in rendez_vous.values('statut').annotate(total=Count('id')).order_by('-total')
    ]

    factures_par_statut = [
        {'statut': row['statut'], 'count': row['total']}
        for row in factures.values('statut').annotate(total=Count('id')).order_by('-total')
    ]

    prescriptions_par_statut = [
        {'statut': row['statut'], 'count': row['total']}
        for row in prescriptions.values('statut').annotate(total=Count('id')).order_by('-total')
    ]

    return {
        'date_debut': date_debut,
        'date_fin': date_fin,
        'kpis': {
            'admissions': admissions.count(),
            'rendez_vous': rendez_vous.count(),
            'prescriptions': prescriptions.count(),
            'factures': factures.count(),
            'lits_actifs': lits_actifs,
            'lits_occupes': lits_occupes,
            'taux_occupation': taux_occupation,
            'factures_validees': factures.filter(statut=StatutFacture.VALIDEE).count(),
            'factures_partiellement_payees': factures.filter(statut=StatutFacture.PARTIELLEMENT_PAYEE).count(),
            'factures_payees': factures.filter(statut=StatutFacture.PAYEE).count(),
        },
        'evolution_journaliere': jours,
        'hospitalisations_par_service': hospitalisations_par_service,
        'rendez_vous_par_statut': rendez_vous_par_statut,
        'factures_par_statut': factures_par_statut,
        'prescriptions_par_statut': prescriptions_par_statut,
    }
