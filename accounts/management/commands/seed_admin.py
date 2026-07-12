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
        reset_password = env_flag('SGHL_ADMIN_RESET_PASSWORD')
        reset_mfa = env_flag('SGHL_ADMIN_RESET_MFA')

        if not username:
            raise CommandError('SGHL_ADMIN_USERNAME ne peut pas être vide.')
        if not password:
            raise CommandError(
                'SGHL_ADMIN_PASSWORD est obligatoire. '
                'Exemple dev : export SGHL_ADMIN_PASSWORD="VotreMotDePasse@2026"'
            )

        user = User.objects.filter(username=username).first()
        if user is None and email:
            user = User.objects.filter(email=email).first()
            if user is not None and user.username != username:
                user.username = username

        created = user is None

        if created:
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
            )
            user.set_password(password)
            user.is_active = True
            user.save()
        else:
            if email and email != user.email:
                User.objects.filter(email=email).exclude(pk=user.pk).update(email=None)
            user.email = email
            user.role = Role.ADMIN
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True
            if reset_password:
                user.set_password(password)
            if reset_mfa or not user.mfa_secret:
                user.mfa_secret = generate_secret()
                user.mfa_enabled = True
            user.save()

        User.objects.filter(role=Role.ADMIN).exclude(pk=user.pk).delete()

        if created:
            self.stdout.write(self.style.SUCCESS(f'Administrateur créé : {username}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Administrateur mis à jour : {username}'))

        self.stdout.write(self.style.SUCCESS(f'E-mail administrateur : {email}'))

        if created or reset_mfa:
            if settings.DEBUG:
                self.stdout.write(
                    self.style.WARNING(
                        f'Secret TOTP (dev uniquement) : {user.mfa_secret} — '
                        'configurez Google Authenticator puis supprimez ce message des logs.'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        'MFA administrateur (ré)initialisée. '
                        'Configurez le TOTP via l’interface ou un canal sécurisé.'
                    )
                )
        elif reset_password:
            self.stdout.write(self.style.SUCCESS('Mot de passe administrateur réinitialisé.'))

        self.stdout.write(self.style.SUCCESS('Autres comptes admin supprimés pour n’en garder qu’un seul.'))
