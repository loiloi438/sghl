from django.db import transaction
from django.utils import timezone

from accounts.models import Role, User
from urgences.models import NiveauTriage, PassageUrgence, StatutPassageUrgence


class UrgencesError(Exception):
    def __init__(self, message: str, code: str = 'error'):
        self.message = message
        self.code = code
        super().__init__(message)


@transaction.atomic
def creer_passage_urgence(**kwargs) -> PassageUrgence:
    return PassageUrgence.objects.create(**kwargs)


@transaction.atomic
def demarrer_triage(*, passage: PassageUrgence, medecin: User, version: int) -> PassageUrgence:
    if passage.version != version:
        raise UrgencesError('Conflit de version.', code='version_conflict')
    if medecin.role not in {Role.ADMIN, Role.MEDECIN, Role.INFIRMIER}:
        raise UrgencesError('Accès refusé.', code='acces_refuse')
    passage.statut = StatutPassageUrgence.TRIAGE
    passage.medecin_triage = medecin
    passage.heure_triage = timezone.now()
    passage.bump_version()
    passage.save()
    return passage


@transaction.atomic
def classer_triage(
    *,
    passage: PassageUrgence,
    niveau: str,
    version: int,
) -> PassageUrgence:
    if passage.version != version:
        raise UrgencesError('Conflit de version.', code='version_conflict')
    if niveau not in NiveauTriage.values:
        raise UrgencesError('Niveau de triage invalide.', code='triage_invalide')
    passage.niveau_triage = niveau
    passage.statut = StatutPassageUrgence.SOINS
    passage.bump_version()
    passage.save()
    return passage
