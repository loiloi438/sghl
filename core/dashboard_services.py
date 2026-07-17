from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Count, Sum
from django.db.models.functions import TruncDate, TruncMonth
from django.utils import timezone

from accounts.models import Role, User
from facturation.models import EcritureComptable, Facture, StatutFacture, TypeEcritureComptable
from hospitalisation.models import Hospitalisation, StatutHospitalisation
from logistics.models import Lit
from messagerie.models import MessageInterne
from notifications.models import NotificationInbox
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


def cas_a_surveiller() -> list[dict]:
    """Cas cliniques nécessitant une attention (démo + données réelles)."""
    from soins.models import ConstanteVitale

    cas = []
    for hosp in Hospitalisation.objects.filter(statut=StatutHospitalisation.ACTIVE).select_related(
        'patient',
    )[:10]:
        patient = hosp.patient
        const = (
            ConstanteVitale.objects.filter(hospitalisation=hosp)
            .order_by('-mesure_le')
            .first()
        )
        niveau = 'stable'
        motif = hosp.motif_admission or 'Suivi post-admission'
        if const:
            if const.temperature and float(const.temperature) >= 38.0:
                niveau = 'urgent'
                motif = f'Fièvre {const.temperature}°C — surveillance rapprochée'
            elif const.tension_systolique and const.tension_systolique >= 140:
                niveau = 'attention'
                motif = f'Tension élevée {const.tension_systolique}/{const.tension_diastolique or "—"} mmHg'
        cas.append(
            {
                'patient_nom': f'{patient.prenom} {patient.nom}',
                'patient_dossier': patient.numero_dossier,
                'motif': motif,
                'niveau': niveau,
                'service': 'Médecine interne',
            }
        )
    if not cas:
        cas = [
            {
                'patient_nom': 'Marie Dupont',
                'patient_dossier': 'P-2026-002',
                'motif': 'Fièvre 38,2°C — prise de constantes',
                'niveau': 'urgent',
                'service': 'Médecine interne',
            },
            {
                'patient_nom': 'Philippe Moussavou',
                'patient_dossier': 'P-2026-003',
                'motif': 'Suivi post-opératoire — stable',
                'niveau': 'stable',
                'service': 'Chirurgie',
            },
        ]
    return cas


def indicateurs_tableau_de_bord() -> dict:
    return {
        'patients_actifs': compter_patients_actifs(),
        'rdv_aujourdhui': compter_rdv_jour(),
        'rdv_planifies': compter_rdv_planifies(),
        'prescriptions_en_attente': compter_prescriptions_en_attente(),
    }


def compter_utilisateurs_actifs() -> int:
    return User.objects.filter(is_active=True).count()


def _classifier_service_rdv(motif: str) -> str:
    texte = (motif or '').lower()
    if any(k in texte for k in ('pédiat', 'pediatr', 'enfant', 'nourrisson')):
        return 'Pédiatrie'
    if any(k in texte for k in ('labo', 'analyse', 'bilan', 'prélèvement', 'prelevement')):
        return 'Laboratoire'
    if any(k in texte for k in ('urgence', 'urgences')):
        return 'Urgences'
    return 'Consultations'


def rdv_par_service(limite_jours: int = 30) -> list[dict]:
    debut = timezone.now() - timedelta(days=limite_jours)
    compteurs: dict[str, int] = {}
    for motif in RendezVous.objects.filter(date_heure__gte=debut).values_list('motif', flat=True):
        service = _classifier_service_rdv(motif)
        compteurs[service] = compteurs.get(service, 0) + 1
    if not compteurs:
        return [
            {'label': 'Consultations', 'value': 0, 'color': '#38bdf8'},
            {'label': 'Pédiatrie', 'value': 0, 'color': '#34d399'},
            {'label': 'Laboratoire', 'value': 0, 'color': '#a78bfa'},
        ]
    couleurs = {
        'Consultations': '#38bdf8',
        'Pédiatrie': '#34d399',
        'Laboratoire': '#a78bfa',
        'Urgences': '#f97316',
    }
    return [
        {'label': label, 'value': value, 'color': couleurs.get(label, '#94a3b8')}
        for label, value in sorted(compteurs.items(), key=lambda item: -item[1])
    ]


def paiements_mensuels(nb_mois: int = 5) -> list[dict]:
    aujourd_hui = timezone.localdate().replace(day=1)
    mois_cibles = []
    for i in range(nb_mois - 1, -1, -1):
        annee = aujourd_hui.year
        mois = aujourd_hui.month - i
        while mois <= 0:
            mois += 12
            annee -= 1
        mois_cibles.append(date(annee, mois, 1))

    debut = mois_cibles[0]
    rows = (
        EcritureComptable.objects.filter(
            type_ecriture__in={
                TypeEcritureComptable.PAIEMENT_PATIENT,
                TypeEcritureComptable.PAIEMENT_TIERS,
            },
            created_at__date__gte=debut,
        )
        .annotate(mois=TruncMonth('created_at'))
        .values('mois')
        .annotate(total=Sum('montant'))
    )
    par_mois = {}
    for row in rows:
        mois = row['mois']
        if mois is None:
            continue
        cle = mois.date().replace(day=1) if hasattr(mois, 'date') else mois.replace(day=1)
        par_mois[cle] = row['total'] or Decimal('0')
    labels_fr = {
        1: 'Jan',
        2: 'Fév',
        3: 'Mar',
        4: 'Avr',
        5: 'Mai',
        6: 'Juin',
        7: 'Juil',
        8: 'Aoû',
        9: 'Sep',
        10: 'Oct',
        11: 'Nov',
        12: 'Déc',
    }
    return [
        {
            'label': labels_fr[m.month],
            'value': float(par_mois.get(m, Decimal('0'))),
            'color': '#38bdf8',
        }
        for m in mois_cibles
    ]


def activite_personnel(nb_jours: int = 7) -> dict:
    debut = timezone.now() - timedelta(days=nb_jours - 1)
    jours = [(debut + timedelta(days=i)).date() for i in range(nb_jours)]
    labels = [j.strftime('%d/%m') for j in jours]

    def serie_pour(queryset, field_name: str) -> list[int]:
        rows = (
            queryset.filter(**{f'{field_name}__date__gte': jours[0]})
            .annotate(jour=TruncDate(field_name))
            .values('jour')
            .annotate(total=Count('id'))
        )
        par_jour = {row['jour']: row['total'] for row in rows}
        return [par_jour.get(j, 0) for j in jours]

    return {
        'labels': labels,
        'series': [
            {
                'label': 'Médecins',
                'color': '#38bdf8',
                'values': serie_pour(
                    RendezVous.objects.filter(medecin__role=Role.MEDECIN),
                    'date_heure',
                ),
            },
            {
                'label': 'Infirmiers',
                'color': '#34d399',
                'values': serie_pour(Prescription.objects.all(), 'created_at'),
            },
            {
                'label': 'Secrétaires',
                'color': '#fbbf24',
                'values': serie_pour(
                    RendezVous.objects.filter(cree_par__role=Role.SECRETAIRE),
                    'created_at',
                ),
            },
        ],
    }


def derniers_comptes(limite: int = 8) -> list[dict]:
    users = User.objects.order_by('-date_joined')[:limite]
    return [
        {
            'id': u.id,
            'full_name': f'{u.first_name} {u.last_name}'.strip() or u.username,
            'role': u.role,
            'role_label': u.get_role_display(),
            'date_joined': u.date_joined,
            'is_active': u.is_active,
        }
        for u in users
    ]


def rdv_a_valider(limite: int = 8) -> list[dict]:
    qs = (
        RendezVous.objects.filter(statut=StatutRendezVous.EN_ATTENTE)
        .select_related('patient', 'medecin')
        .order_by('date_heure')[:limite]
    )
    return [
        {
            'id': str(r.id),
            'patient_nom': f'{r.patient.prenom} {r.patient.nom}'.strip(),
            'medecin_nom': f'{r.medecin.first_name} {r.medecin.last_name}'.strip() or r.medecin.username,
            'date_heure': r.date_heure,
            'motif': r.motif,
            'statut': r.statut,
        }
        for r in qs
    ]


def notifications_recentes(user: User, limite: int = 6) -> list[dict]:
    qs = NotificationInbox.objects.filter(utilisateur=user).order_by('-created_at')[:limite]
    return [
        {
            'id': str(n.id),
            'titre': n.titre,
            'corps': n.corps,
            'categorie': n.categorie,
            'lu': n.lu,
            'created_at': n.created_at,
        }
        for n in qs
    ]


def messages_du_jour(user: User, limite: int = 5) -> list[dict]:
    debut = timezone.localdate()
    qs = (
        MessageInterne.objects.filter(
            destinataire=user,
            created_at__date=debut,
        )
        .select_related('expediteur')
        .order_by('-created_at')[:limite]
    )
    return [
        {
            'id': str(m.id),
            'sujet': m.sujet,
            'expediteur': (
                f'{m.expediteur.first_name} {m.expediteur.last_name}'.strip()
                or m.expediteur.username
            ),
            'lu': m.lu,
            'created_at': m.created_at,
        }
        for m in qs
    ]


def overview_tableau_de_bord(user: User) -> dict:
    stats = indicateurs_tableau_de_bord()
    factures_en_attente = Facture.objects.filter(
        statut__in={StatutFacture.VALIDEE, StatutFacture.PARTIELLEMENT_PAYEE},
    ).count()
    messages_non_lus = MessageInterne.objects.filter(destinataire=user, lu=False).count()
    is_admin = user.role == Role.ADMIN
    can_finance = user.role in {Role.ADMIN, Role.COMPTABLE}
    can_rdv = user.role in {
        Role.ADMIN,
        Role.MEDECIN,
        Role.INFIRMIER,
        Role.SECRETAIRE,
        Role.COMPTABLE,
    }

    return {
        'role': user.role,
        'kpis': {
            'utilisateurs_actifs': compter_utilisateurs_actifs() if is_admin else stats['patients_actifs'],
            'patients_actifs': stats['patients_actifs'],
            'rdv_aujourdhui': stats['rdv_aujourdhui'],
            'rdv_planifies': stats['rdv_planifies'],
            'prescriptions_en_attente': stats['prescriptions_en_attente'],
            'factures_en_attente': factures_en_attente,
            'messages_non_lus': messages_non_lus,
        },
        'rdv_par_service': rdv_par_service(),
        'paiements_mensuels': paiements_mensuels() if can_finance else [],
        'activite_personnel': activite_personnel() if is_admin else {'labels': [], 'series': []},
        'derniers_comptes': derniers_comptes() if is_admin else [],
        'rdv_a_valider': rdv_a_valider() if can_rdv else [],
        'notifications': notifications_recentes(user),
        'messages_du_jour': messages_du_jour(user),
        'cas_a_surveiller': cas_a_surveiller() if user.role in {
            Role.ADMIN,
            Role.MEDECIN,
            Role.INFIRMIER,
            Role.BIOLOGISTE,
        } else [],
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
