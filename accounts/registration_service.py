import re
from datetime import date, timedelta

from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from django.utils.crypto import get_random_string

from accounts.emails import (
    notifier_inscription_patient,
    notifier_validation_code,
    notifier_validation_code_user,
)
from accounts.jwt_service import login_user
from accounts.models import Role, User, AccountValidation
from patients.models import Patient, Sexe


class InscriptionPatientError(Exception):
    def __init__(self, message: str, status: int = 400):
        self.message = message
        self.status = status
        super().__init__(message)


def _generer_numero_dossier() -> str:
    year = date.today().year
    prefix = f'P-{year}-'
    numeros = Patient.objects.filter(numero_dossier__startswith=prefix).values_list(
        'numero_dossier', flat=True
    )
    max_seq = 0
    for numero in numeros:
        try:
            seq = int(numero.rsplit('-', 1)[-1])
        except ValueError:
            continue
        if seq > max_seq:
            max_seq = seq
    return f'{prefix}{max_seq + 1:03d}'


def _generer_username(*, email: str, telephone: str) -> str:
    if email:
        base = email.split('@')[0][:30]
    else:
        digits = ''.join(c for c in telephone if c.isdigit())[-10:] or 'patient'
        base = f'pat{digits}'
    base = re.sub(r'[^\w.-]', '', base) or 'patient'
    candidate = base[:30]
    suffix = 1
    while User.objects.filter(username=candidate).exists():
        candidate = f'{base[:26]}{suffix}'
        suffix += 1
    return candidate


def _generer_code_validation(length: int = 6) -> str:
    digits = '0123456789'
    return get_random_string(length=length, allowed_chars=digits)


def _create_account_validation(user: User, patient: Patient) -> str:
    code = _generer_code_validation()
    # hash code for storage
    hash_ = make_password(code)
    AccountValidation.objects.create(user=user, code_hash=hash_)
    # send e-mail (synchronously so tests using locmem capture it)
    try:
        notifier_validation_code(user.id, patient.id, code)
    except Exception:
        # don't fail registration if email sending fails
        pass
    return code


def inscrire_patient(
    *,
    nom: str,
    prenom: str,
    date_naissance: date,
    sexe: str,
    email: str = '',
    telephone: str = '',
    password: str,
    password_confirm: str,
    consentement_rgpd: bool,
) -> tuple[User, str]:
    """Crée un compte patient + dossier. Retourne (user inactif, code validation).
    Une validation par code est générée et envoyée par e-mail si possible.
    """
    nom = nom.strip()
    prenom = prenom.strip()
    email = email.strip().lower()
    telephone = telephone.strip()

    if not consentement_rgpd:
        raise InscriptionPatientError(
            'Le consentement au traitement des données est obligatoire.',
        )
    if not nom or not prenom:
        raise InscriptionPatientError('Nom et prénom sont obligatoires.')
    if sexe not in Sexe.values:
        raise InscriptionPatientError('Sexe invalide.')
    if not email:
        raise InscriptionPatientError('Un e-mail est requis pour valider le compte.')
    if password != password_confirm:
        raise InscriptionPatientError('Les mots de passe ne correspondent pas.')
    if email and User.objects.filter(email__iexact=email).exists():
        raise InscriptionPatientError('Un compte existe déjà avec cet e-mail.')
    if email and Patient.objects.filter(email__iexact=email).exists():
        raise InscriptionPatientError('Un dossier patient existe déjà avec cet e-mail.')

    username = _generer_username(email=email, telephone=telephone)

    try:
        validate_password(password, user=User(username=username, email=email))
    except ValidationError as exc:
        raise InscriptionPatientError(' '.join(exc.messages)) from exc

    with transaction.atomic():
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role=Role.PATIENT,
            first_name=prenom,
            last_name=nom,
        )
        # create patient record
        patient = Patient.objects.create(
            numero_dossier=_generer_numero_dossier(),
            nom=nom,
            prenom=prenom,
            date_naissance=date_naissance,
            sexe=sexe,
            telephone=telephone,
            email=email,
            consentement_donnees=True,
            compte_utilisateur=user,
        )
        # mark account inactive until validation
        user.is_active = False
        user.save(update_fields=['is_active'])

    # generate and send validation code
    validation_code = _create_account_validation(user, patient)
    # send generic welcome/inscription email as well (synchronously in tests)
    try:
        notifier_inscription_patient(user.id, patient.id)
    except Exception:
        pass
    return user, validation_code


def verifier_code_validation(*, username: str, code: str) -> User:
    """Vérifie le code entré par l'utilisateur et active le compte si valide.
    Renvoie l'utilisateur si tout est OK, lève InscriptionPatientError sinon.
    """
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        raise InscriptionPatientError('Utilisateur introuvable.', 404)

    # get latest non-used validation
    validation = (
        AccountValidation.objects.filter(user=user, used=False).order_by('-created_at').first()
    )
    if not validation:
        raise InscriptionPatientError('Aucun code de validation trouvé. Demandez un nouveau code.', 400)

    # check expiry (10 minutes)
    if timezone.now() > validation.created_at + timedelta(minutes=10):
        raise InscriptionPatientError('Le code a expiré. Demandez un nouveau code.', 400)

    # limit attempts
    if validation.attempts >= 5:
        raise InscriptionPatientError('Trop de tentatives. Demandez un nouveau code.', 429)

    if not check_password(code, validation.code_hash):
        validation.attempts += 1
        validation.save(update_fields=['attempts'])
        raise InscriptionPatientError('Code invalide.', 400)

    # mark used and activate user
    validation.used = True
    validation.save(update_fields=['used'])
    user.is_active = True
    user.save(update_fields=['is_active'])
    return user


def renvoyer_code_validation(*, username: str) -> bool:
    """Génère et envoie un nouveau code de validation pour l'utilisateur donné."""
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        raise InscriptionPatientError('Utilisateur introuvable.', 404)

    patient = None
    try:
        patient = Patient.objects.get(compte_utilisateur=user)
    except Patient.DoesNotExist:
        pass

    if patient:
        _create_account_validation(user, patient)
    else:
        code = _generer_code_validation()
        hash_ = make_password(code)
        AccountValidation.objects.create(user=user, code_hash=hash_)
        notifier_validation_code_user(user.id, code)
    return True
