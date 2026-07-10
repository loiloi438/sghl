from __future__ import annotations

import getpass
import sys
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.hashers import make_password, check_password

from accounts.models import AccountValidation
from accounts.emails import notifier_mfa_code


class Command(BaseCommand):
    help = 'Flux MFA par email pour un administrateur (CLI)'

    def add_arguments(self, parser):
        parser.add_argument('--username', '-u', help='Nom d\'utilisateur (admin)')
        parser.add_argument('--password', '-p', help='Mot de passe (optionnel, pour tests)')

    def handle(self, *args, **options):
        username = options.get('username')
        if not username:
            username = input('Identifiant: ').strip()
        password = options.get('password')
        if not password:
            password = getpass.getpass('Mot de passe: ')

        User = get_user_model()
        user = authenticate(username=username, password=password)
        if user is None or not user.is_active:
            self.stdout.write(self.style.ERROR('Identifiants invalides ou compte inactif.'))
            sys.exit(1)

        # Generate 6-digit code
        from django.utils.crypto import get_random_string

        def send_code():
            code = get_random_string(length=6, allowed_chars='0123456789')
            hash_ = make_password(code)
            AccountValidation.objects.create(user=user, code_hash=hash_)
            sent = notifier_mfa_code(user.id, code)
            # Informative output in CLI (do not rely on this for production security)
            if not sent:
                self.stdout.write(self.style.WARNING('Le code n\'a pas pu être envoyé par e-mail (vérifier la configuration).'))
            self.stdout.write(self.style.SUCCESS('Code MFA envoyé par e-mail (valable 5 minutes).'))
            return code

        # Initial send
        code_sent = send_code()

        # Prompt loop
        while True:
            entered = input('Code MFA (ou tapez "resend" pour renvoyer): ').strip()
            if entered.lower() == 'resend':
                code_sent = send_code()
                continue

            # find latest unused validation
            validation = (
                AccountValidation.objects.filter(user=user, used=False).order_by('-created_at').first()
            )
            if not validation:
                self.stdout.write(self.style.ERROR('Aucun code MFA trouvé. Demandez un nouveau code (tapez "resend").'))
                continue

            # expiry 5 minutes
            if timezone.now() > validation.created_at + timedelta(minutes=5):
                self.stdout.write(self.style.ERROR('Le code a expiré. Demandez un nouveau code (tapez "resend").'))
                continue

            if not check_password(entered, validation.code_hash):
                validation.attempts += 1
                validation.save(update_fields=['attempts'])
                self.stdout.write(self.style.ERROR('Code invalide. Réessayez ou tapez "resend".'))
                continue

            # success
            validation.used = True
            validation.save(update_fields=['used'])
            self.stdout.write(self.style.SUCCESS('Authentification réussie — accès autorisé.'))
            break
