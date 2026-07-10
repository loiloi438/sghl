import logging

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from accounts.emails import notifier_reinitialisation_mdp
from accounts.models import Role, User

logger = logging.getLogger(__name__)


def _trouver_utilisateur(identifiant: str) -> User | None:
    identifiant = identifiant.strip()
    if not identifiant:
        return None
    user = User.objects.filter(username__iexact=identifiant).first()
    if user:
        return user
    return User.objects.filter(email__iexact=identifiant).first()


def demander_reinitialisation_mdp(*, identifiant: str) -> bool:
    """
    Envoie un lien de réinitialisation si le compte existe.
    Retourne True si un e-mail a été tenté (sans révéler l'existence du compte côté API).
    """
    user = _trouver_utilisateur(identifiant)
    if user is None:
        logger.info('Réinitialisation MDP ignorée : identifiant inconnu.')
        return False

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    frontend = getattr(settings, 'SGHL_FRONTEND_URL', 'http://localhost:5173').rstrip('/')
    lien = f'{frontend}/login?reset={uid}.{token}'

    if user.role == Role.PATIENT and not user.email:
        logger.info(
            'Réinitialisation MDP patient sans e-mail (SMS simulé) user=%s lien=%s',
            user.username,
            lien,
        )
        return True

    return notifier_reinitialisation_mdp(user.id, lien)


def reinitialiser_mot_de_passe(*, uid: str, token: str, new_password: str) -> User:
    try:
        user_id = force_str(urlsafe_base64_decode(uid))
        user = User.objects.get(pk=user_id)
    except (User.DoesNotExist, ValueError, TypeError, OverflowError) as exc:
        raise ValueError('Lien de réinitialisation invalide.') from exc

    if not default_token_generator.check_token(user, token):
        raise ValueError('Lien expiré ou déjà utilisé.')

    user.set_password(new_password)
    user.save(update_fields=['password'])
    return user
