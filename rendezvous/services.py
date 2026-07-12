from datetime import datetime, time, timedelta

from django.db import transaction
from django.utils import timezone

from accounts.models import Role, User
from patients.models import Patient
from notifications.integrations import (
    planifier_push_rdv_annule,
    planifier_push_rdv_confirme,
    planifier_push_rdv_modifie,
    planifier_push_rdv_planifie,
    planifier_push_rdv_reporte,
)
from rendezvous.emails import (
    notifier_rdv_annule,
    notifier_rdv_confirme,
    notifier_rdv_demande_patient,
    notifier_rdv_modifie,
    notifier_rdv_planifie,
    notifier_rdv_reporte,
)
from rendezvous.models import RendezVous, StatutRendezVous, TypeConsultation


class RendezVousError(Exception):
    def __init__(self, message: str, code: str = 'error'):
        self.message = message
        self.code = code
        super().__init__(message)


ACTIFS = {StatutRendezVous.PLANIFIE, StatutRendezVous.CONFIRME}


def assert_staff(user: User):
    if user.role not in {Role.ADMIN, Role.MEDECIN, Role.INFIRMIER, Role.SECRETAIRE}:
        raise RendezVousError('Accès refusé.', code='acces_refuse')


def get_rendez_vous(rdv_id) -> RendezVous:
    try:
        return RendezVous.objects.select_related(
            'patient',
            'medecin',
            'cree_par',
        ).get(id=rdv_id)
    except RendezVous.DoesNotExist:
        raise RendezVousError('Rendez-vous introuvable.', code='not_found')


def _assert_medecin(user: User) -> User:
    if user.role != Role.MEDECIN:
        raise RendezVousError('Médecin introuvable ou invalide.', code='medecin_invalide')
    return user


def _verifier_creneau(
    *,
    medecin: User,
    date_heure: datetime,
    duree_minutes: int,
    exclude_id=None,
):
    fin = date_heure + timedelta(minutes=duree_minutes)
    qs = RendezVous.objects.filter(medecin=medecin, statut__in=ACTIFS)
    if exclude_id:
        qs = qs.exclude(id=exclude_id)
    for rdv in qs:
        rdv_fin = rdv.date_heure + timedelta(minutes=rdv.duree_minutes)
        if date_heure < rdv_fin and fin > rdv.date_heure:
            raise RendezVousError(
                'Ce créneau est déjà réservé pour ce médecin.',
                code='creneau_indisponible',
            )


@transaction.atomic
def creer_rendez_vous(
    *,
    patient: Patient,
    medecin: User,
    date_heure: datetime,
    motif: str,
    auteur: User,
    duree_minutes: int = 30,
    notes: str = '',
    type_consultation: str = TypeConsultation.PRESENTIEL,
    lien_visio: str = '',
) -> RendezVous:
    if auteur.role == Role.PATIENT:
        if patient.compte_utilisateur_id != auteur.id:
            raise RendezVousError('Accès refusé.', code='acces_refuse')
    else:
        assert_staff(auteur)

    medecin = _assert_medecin(medecin)

    if date_heure <= timezone.now():
        raise RendezVousError(
            'Le rendez-vous doit être planifié dans le futur.',
            code='date_invalide',
        )

    _verifier_creneau(medecin=medecin, date_heure=date_heure, duree_minutes=duree_minutes)

    rdv = RendezVous.objects.create(
        patient=patient,
        medecin=medecin,
        date_heure=date_heure,
        duree_minutes=duree_minutes,
        motif=motif,
        notes=notes,
        cree_par=auteur,
        statut=StatutRendezVous.PLANIFIE,
        type_consultation=type_consultation,
        lien_visio=lien_visio,
    )
    rdv_id = rdv.id
    if auteur.role == Role.PATIENT:
        transaction.on_commit(lambda: notifier_rdv_demande_patient(rdv_id))
    else:
        transaction.on_commit(lambda: notifier_rdv_planifie(rdv_id))
    planifier_push_rdv_planifie(rdv_id)
    return rdv


@transaction.atomic
def confirmer_rendez_vous(*, rdv: RendezVous, auteur: User, version: int) -> RendezVous:
    assert_staff(auteur)
    r = RendezVous.objects.select_for_update().get(pk=rdv.pk)
    if r.version != version:
        raise RendezVousError('Conflit de version : rechargez et réessayez.', code='version_conflict')
    if r.statut != StatutRendezVous.PLANIFIE:
        raise RendezVousError('Seul un rendez-vous planifié peut être confirmé.', code='statut_invalide')

    r.statut = StatutRendezVous.CONFIRME
    r.confirme_le = timezone.now()
    r.bump_version()
    r.save(update_fields=['statut', 'confirme_le', 'version', 'updated_at'])
    rdv_id = r.id
    transaction.on_commit(lambda: notifier_rdv_confirme(rdv_id))
    planifier_push_rdv_confirme(rdv_id)
    return r


@transaction.atomic
def annuler_rendez_vous(
    *,
    rdv: RendezVous,
    auteur: User,
    version: int,
    motif_annulation: str = '',
) -> RendezVous:
    r = RendezVous.objects.select_for_update().select_related('patient').get(pk=rdv.pk)

    if auteur.role == Role.PATIENT:
        if r.patient.compte_utilisateur_id != auteur.id:
            raise RendezVousError('Accès refusé.', code='acces_refuse')
    else:
        assert_staff(auteur)

    if r.version != version:
        raise RendezVousError('Conflit de version : rechargez et réessayez.', code='version_conflict')
    if r.statut not in ACTIFS:
        raise RendezVousError('Ce rendez-vous ne peut plus être annulé.', code='statut_invalide')

    r.statut = StatutRendezVous.ANNULE
    r.annule_le = timezone.now()
    r.annule_par = auteur
    r.motif_annulation = motif_annulation
    r.bump_version()
    r.save(
        update_fields=[
            'statut',
            'annule_le',
            'annule_par',
            'motif_annulation',
            'version',
            'updated_at',
        ]
    )
    rdv_id = r.id
    motif = motif_annulation
    transaction.on_commit(lambda: notifier_rdv_annule(rdv_id, motif))
    planifier_push_rdv_annule(rdv_id, motif)
    return r


@transaction.atomic
def modifier_rendez_vous(
    *,
    rdv: RendezVous,
    auteur: User,
    version: int,
    date_heure: datetime | None = None,
    medecin: User | None = None,
    motif: str | None = None,
    notes: str | None = None,
    duree_minutes: int | None = None,
    motif_modification: str = '',
) -> RendezVous:
    assert_staff(auteur)
    r = RendezVous.objects.select_for_update().select_related('patient', 'medecin').get(pk=rdv.pk)

    if r.version != version:
        raise RendezVousError('Conflit de version : rechargez et réessayez.', code='version_conflict')
    if not r.est_modifiable:
        raise RendezVousError('Ce rendez-vous ne peut plus être modifié.', code='statut_invalide')

    ancienne_date = timezone.localtime(r.date_heure).strftime('%d/%m/%Y à %H:%M')
    changements: list[str] = []
    date_reportee = False

    if medecin is not None:
        medecin = _assert_medecin(medecin)
        if medecin.id != r.medecin_id:
            ancien = f'{r.medecin.first_name} {r.medecin.last_name}'.strip() or r.medecin.username
            nouveau = f'{medecin.first_name} {medecin.last_name}'.strip() or medecin.username
            changements.append(f'Médecin : {ancien} → {nouveau}')
            r.medecin = medecin

    nouvelle_date = date_heure if date_heure is not None else r.date_heure
    nouvelle_duree = duree_minutes if duree_minutes is not None else r.duree_minutes

    if date_heure is not None and timezone.localtime(date_heure) != timezone.localtime(r.date_heure):
        if date_heure <= timezone.now():
            raise RendezVousError(
                'Le rendez-vous doit rester planifié dans le futur.',
                code='date_invalide',
            )
        date_reportee = True

    _verifier_creneau(
        medecin=r.medecin,
        date_heure=nouvelle_date,
        duree_minutes=nouvelle_duree,
        exclude_id=r.id,
    )

    if date_heure is not None:
        r.date_heure = date_heure
    if duree_minutes is not None and duree_minutes != r.duree_minutes:
        changements.append(f'Durée : {r.duree_minutes} → {duree_minutes} min')
        r.duree_minutes = duree_minutes
    if motif is not None and motif.strip() and motif != r.motif:
        changements.append(f'Motif : {r.motif} → {motif.strip()}')
        r.motif = motif.strip()
    if notes is not None and notes != r.notes:
        changements.append('Notes mises à jour')
        r.notes = notes

    if not date_reportee and not changements:
        raise RendezVousError('Aucune modification à enregistrer.', code='aucun_changement')

    r.bump_version()
    r.save(
        update_fields=[
            'medecin',
            'date_heure',
            'duree_minutes',
            'motif',
            'notes',
            'version',
            'updated_at',
        ]
    )

    rdv_id = r.id
    if date_reportee:
        ad, mm = ancienne_date, motif_modification
        transaction.on_commit(
            lambda rid=rdv_id, a=ad, m=mm: notifier_rdv_reporte(
                rid, ancienne_date_heure=a, motif_modification=m
            )
        )
        planifier_push_rdv_reporte(rdv_id, ad, mm)
    else:
        texte_changements = '\n'.join(changements)
        tc = texte_changements
        transaction.on_commit(lambda rid=rdv_id, t=tc: notifier_rdv_modifie(rid, changements=t))
        planifier_push_rdv_modifie(rdv_id, tc)

    return r


@transaction.atomic
def terminer_rendez_vous(*, rdv: RendezVous, auteur: User, version: int) -> RendezVous:
    assert_staff(auteur)
    r = RendezVous.objects.select_for_update().get(pk=rdv.pk)
    if r.version != version:
        raise RendezVousError('Conflit de version : rechargez et réessayez.', code='version_conflict')
    if r.statut != StatutRendezVous.CONFIRME:
        raise RendezVousError('Seul un rendez-vous confirmé peut être terminé.', code='statut_invalide')

    r.statut = StatutRendezVous.TERMINE
    r.bump_version()
    r.save(update_fields=['statut', 'version', 'updated_at'])
    return r


@transaction.atomic
def marquer_absent(*, rdv: RendezVous, auteur: User, version: int) -> RendezVous:
    assert_staff(auteur)
    r = RendezVous.objects.select_for_update().get(pk=rdv.pk)
    if r.version != version:
        raise RendezVousError('Conflit de version : rechargez et réessayez.', code='version_conflict')
    if r.statut not in ACTIFS:
        raise RendezVousError('Statut incompatible.', code='statut_invalide')

    r.statut = StatutRendezVous.ABSENT
    r.bump_version()
    r.save(update_fields=['statut', 'version', 'updated_at'])
    return r


def compter_rdv_jour(date_jour=None) -> int:
    jour = date_jour or timezone.localdate()
    tz = timezone.get_current_timezone()
    debut = timezone.make_aware(datetime.combine(jour, time.min), tz)
    fin = debut + timedelta(days=1)
    return RendezVous.objects.filter(
        date_heure__gte=debut,
        date_heure__lt=fin,
        statut__in=ACTIFS | {StatutRendezVous.TERMINE},
    ).count()
