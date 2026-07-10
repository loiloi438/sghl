from datetime import datetime, time, timedelta
from typing import TypedDict

from django.db import transaction
from django.utils import timezone

from core.email_utils import resoudre_email_patient
from notifications.integrations import push_rdv_rappel_j1
from rendezvous.emails import notifier_rdv_rappel_j1
from rendezvous.models import RendezVous, StatutRendezVous

STATUTS_RAPPEL_J1 = {StatutRendezVous.PLANIFIE, StatutRendezVous.CONFIRME}


class ResultatRappelsJ1(TypedDict):
    envoyes: int
    ignores_sans_email: int
    echecs: int
    total_eligibles: int


def _plage_demain_locale():
    tz = timezone.get_current_timezone()
    demain = timezone.localdate() + timedelta(days=1)
    debut = timezone.make_aware(datetime.combine(demain, time.min), tz)
    return debut, debut + timedelta(days=1)


def queryset_rappel_j1() -> 'RendezVous.objects':
    debut, fin = _plage_demain_locale()
    return (
        RendezVous.objects.filter(
            date_heure__gte=debut,
            date_heure__lt=fin,
            statut__in=STATUTS_RAPPEL_J1,
            rappel_j1_envoye_le__isnull=True,
        )
        .select_related('patient', 'medecin')
        .order_by('date_heure')
    )


@transaction.atomic
def envoyer_rappels_j1(*, dry_run: bool = False) -> ResultatRappelsJ1:
    rdvs = list(queryset_rappel_j1())
    resultat: ResultatRappelsJ1 = {
        'envoyes': 0,
        'ignores_sans_email': 0,
        'echecs': 0,
        'total_eligibles': len(rdvs),
    }

    for rdv in rdvs:
        if not resoudre_email_patient(rdv.patient):
            resultat['ignores_sans_email'] += 1
            continue
        if dry_run:
            resultat['envoyes'] += 1
            continue

        email_ok = False
        if resoudre_email_patient(rdv.patient):
            email_ok = notifier_rdv_rappel_j1(rdv.id)
        push_ok = push_rdv_rappel_j1(rdv.id) is not None
        if email_ok or push_ok:
            updated = RendezVous.objects.filter(
                pk=rdv.pk,
                rappel_j1_envoye_le__isnull=True,
            ).update(rappel_j1_envoye_le=timezone.now())
            if updated:
                resultat['envoyes'] += 1
            else:
                resultat['ignores_sans_email'] += 1
        elif not resoudre_email_patient(rdv.patient) and rdv.patient.compte_utilisateur_id is None:
            resultat['ignores_sans_email'] += 1
        else:
            resultat['echecs'] += 1

    return resultat
