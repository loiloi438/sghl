import logging
from typing import Any, Optional
from uuid import UUID

import requests
from django.conf import settings
from django.contrib.auth import get_user_model

from notifications.models import DeviceToken, NotificationInbox

logger = logging.getLogger(__name__)
User = get_user_model()


def push_actif() -> bool:
    return getattr(settings, 'PUSH_NOTIFICATIONS_ENABLED', True)


def _fcm_configure() -> bool:
    return bool(getattr(settings, 'FCM_SERVER_KEY', '').strip())


def _token_fcm_eligible(token: str) -> bool:
    return not token.startswith('sghl-dev:')


def enregistrer_inbox(
    *,
    utilisateur_id: int,
    titre: str,
    corps: str,
    categorie: str = '',
    donnees: Optional[dict[str, Any]] = None,
) -> NotificationInbox:
    return NotificationInbox.objects.create(
        utilisateur_id=utilisateur_id,
        titre=titre,
        corps=corps,
        categorie=categorie,
        donnees=donnees or {},
    )


def _envoyer_fcm(token: str, titre: str, corps: str, donnees: dict) -> bool:
    cle = settings.FCM_SERVER_KEY.strip()
    payload = {
        'to': token,
        'notification': {'title': titre, 'body': corps},
        'data': {k: str(v) for k, v in donnees.items()},
        'priority': 'high',
    }
    try:
        response = requests.post(
            'https://fcm.googleapis.com/fcm/send',
            headers={
                'Authorization': f'key={cle}',
                'Content-Type': 'application/json',
            },
            json=payload,
            timeout=10,
        )
        if response.status_code != 200:
            logger.warning('FCM HTTP %s : %s', response.status_code, response.text[:200])
            return False
        body = response.json()
        if body.get('failure', 0) > 0:
            logger.warning('FCM échec : %s', body)
            return False
        return True
    except requests.RequestException:
        logger.exception('Erreur réseau FCM')
        return False


def notifier_utilisateur(
    *,
    utilisateur_id: int,
    titre: str,
    corps: str,
    categorie: str = '',
    donnees: Optional[dict[str, Any]] = None,
) -> NotificationInbox:
    donnees = donnees or {}
    inbox = enregistrer_inbox(
        utilisateur_id=utilisateur_id,
        titre=titre,
        corps=corps,
        categorie=categorie,
        donnees=donnees,
    )

    if not push_actif():
        return inbox

    tokens = list(
        DeviceToken.objects.filter(utilisateur_id=utilisateur_id, actif=True).values_list(
            'token',
            flat=True,
        )
    )
    if not tokens:
        logger.debug('Aucun appareil pour utilisateur %s.', utilisateur_id)
        return inbox

    if _fcm_configure():
        for token in tokens:
            if _token_fcm_eligible(token):
                _envoyer_fcm(token, titre, corps, {**donnees, 'id': str(inbox.id)})
            else:
                logger.info(
                    '[PUSH dev] %s → %s : %s',
                    utilisateur_id,
                    token[:24],
                    titre,
                )
    else:
        for token in tokens:
            logger.info(
                '[PUSH console] %s (%s…) : %s — %s',
                utilisateur_id,
                token[:20],
                titre,
                corps[:80],
            )

    return inbox


def notifier_patient_utilisateur(
    *,
    patient,
    titre: str,
    corps: str,
    categorie: str = '',
    donnees: Optional[dict[str, Any]] = None,
) -> Optional[NotificationInbox]:
    compte = patient.compte_utilisateur
    if not compte:
        return None
    return notifier_utilisateur(
        utilisateur_id=compte.id,
        titre=titre,
        corps=corps,
        categorie=categorie,
        donnees=donnees,
    )


def enregistrer_appareil(
    *,
    utilisateur_id: int,
    token: str,
    plateforme: str,
) -> DeviceToken:
    token = token.strip()
    if not token:
        raise ValueError('Token vide.')
    appareil, _ = DeviceToken.objects.update_or_create(
        token=token,
        defaults={
            'utilisateur_id': utilisateur_id,
            'plateforme': plateforme,
            'actif': True,
        },
    )
    return appareil


def desactiver_appareil(*, utilisateur_id: int, token: str) -> None:
    DeviceToken.objects.filter(utilisateur_id=utilisateur_id, token=token.strip()).update(
        actif=False
    )


def marquer_lu(notification_id: UUID, utilisateur_id: int) -> bool:
    updated = NotificationInbox.objects.filter(
        pk=notification_id,
        utilisateur_id=utilisateur_id,
        lu=False,
    ).update(lu=True)
    return updated > 0


def compter_non_lues(utilisateur_id: int) -> int:
    return NotificationInbox.objects.filter(utilisateur_id=utilisateur_id, lu=False).count()
