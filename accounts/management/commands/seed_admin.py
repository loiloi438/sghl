import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from accounts.mfa_service import generate_secret
from accounts.models import Role, User
from core.env_utils import env_flag


class Command(BaseCommand):
    help = 'Crée ou met à jour le compte administrateur SGHL (mot de passe via variable d’environnement).'

    def handle(self, *args, **options):
        if not settings.DEBUG and not env_flag('SGHL_SEED_ADMIN'):
            raise CommandError(
                'seed_admin est désactivé en production. '
                'Définissez SGHL_SEED_ADMIN=true uniquement lors du premier déploiement.'
            )

        username = os.getenv('SGHL_ADMIN_USERNAME', 'tresormouanga').strip()
        password = os.getenv('SGHL_ADMIN_PASSWORD', '').strip()
        email = os.getenv('SGHL_ADMIN_EMAIL', 'mouangatresor673@gmail.com').strip()
        reset_mfa = env_flag('SGHL_ADMIN_RESET_MFA')

        if not username:
            raise CommandError('SGHL_ADMIN_USERNAME ne peut pas être vide.')
        if not password:
            raise CommandError(
                'SGHL_ADMIN_PASSWORD est obligatoire. '
                'Exemple dev : export SGHL_ADMIN_PASSWORD="VotreMotDePasse@2026"'
            )

        deleted, _ = User.objects.filter(role=Role.ADMIN).delete()
        if deleted:
            self.stdout.write(self.style.WARNING(f'Comptes admin supprimés : {deleted}'))

        if email:
            User.objects.filter(email__iexact=email).update(email=None)
        User.objects.filter(username__iexact=username).delete()

        secret = generate_secret()
        user = User(
            username=username,
            email=email,
            role=Role.ADMIN,
            is_staff=True,
            is_superuser=True,
            first_name='Tresor',
            last_name='Mouanga',
            mfa_enabled=True,
            mfa_secret=secret,
            is_active=True,
        )
        user.set_password(password)
        user.save()

        self.stdout.write(self.style.SUCCESS(f'Administrateur créé : {username}'))

        self.stdout.write(self.style.SUCCESS(f'E-mail administrateur : {email}'))

        if settings.DEBUG:
            self.stdout.write(
                self.style.WARNING(
                    f'Secret TOTP (dev uniquement) : {user.mfa_secret} — '
                    'configurez Google Authenticator puis supprimez ce message des logs.'
                )
            )
        elif reset_mfa:
            self.stdout.write(self.style.WARNING('MFA administrateur réinitialisée.'))
        else:
            self.stdout.write(self.style.SUCCESS('Mot de passe administrateur défini.'))
