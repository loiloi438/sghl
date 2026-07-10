from django.core.management.base import BaseCommand
import os

from accounts.mfa_service import generate_secret
from accounts.models import Role, User


class Command(BaseCommand):
    help = 'Crée un seul compte administrateur pour SGHL.'

    def handle(self, *args, **options):
        username = 'tresormouanga'
        password = '02060024@tr'
        email = os.getenv('SGHL_ADMIN_EMAIL', 'mouangatresor673@gmail.com').strip()

        secret = generate_secret()
        user, created = User.objects.update_or_create(
            username=username,
            defaults={
                'email': email,
                'role': Role.ADMIN,
                'is_staff': True,
                'is_superuser': True,
                'first_name': 'Tresor',
                'last_name': 'Mouanga',
                'mfa_enabled': True,
                'mfa_secret': secret,
            },
        )
        user.email = email
        user.set_password(password)
        user.mfa_enabled = True
        user.mfa_secret = secret
        user.is_active = True
        user.save()

        User.objects.filter(role=Role.ADMIN).exclude(pk=user.pk).delete()

        if created:
            self.stdout.write(self.style.SUCCESS(f'Administrateur créé : {username} / {password}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Administrateur mis à jour : {username} / {password}'))
        self.stdout.write(self.style.SUCCESS(f'E-mail administrateur : {email}'))
        self.stdout.write(self.style.SUCCESS(f'MFA administrateur activée. Secret TOTP : {secret}'))
        self.stdout.write(self.style.SUCCESS('Autres comptes admin supprimés pour n’en garder qu’un seul.'))
