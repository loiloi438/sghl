from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Envoie un e-mail de test SMTP (diagnostic production Render).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--to',
            default=settings.DEFAULT_FROM_EMAIL,
            help='Destinataire du test (défaut : DEFAULT_FROM_EMAIL)',
        )

    def handle(self, *args, **options):
        destinataire = (options['to'] or '').strip()
        if not destinataire:
            self.stderr.write(self.style.ERROR('Destinataire vide.'))
            return

        self.stdout.write(f'Backend : {settings.EMAIL_BACKEND}')
        if getattr(settings, 'BREVO_API_KEY', '').strip():
            self.stdout.write('Provider: Brevo (API HTTP — compatible Render free)')
        else:
            self.stdout.write(f'Hôte    : {settings.EMAIL_HOST}:{settings.EMAIL_PORT}')
            self.stdout.write(f'User    : {settings.EMAIL_HOST_USER}')
        self.stdout.write(f'From    : {settings.DEFAULT_FROM_EMAIL}')
        self.stdout.write(f'OTP     : {getattr(settings, "OTP_MODE", "?")}')
        self.stdout.write(f'Envoi test → {destinataire}…')

        try:
            send_mail(
                subject='[SGHL] Test SMTP',
                message='Si vous recevez cet e-mail, SMTP fonctionne correctement.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[destinataire],
                fail_silently=False,
            )
        except Exception as exc:
            self.stderr.write(self.style.ERROR(f'Échec SMTP : {exc}'))
            raise

        self.stdout.write(self.style.SUCCESS('E-mail de test envoyé avec succès.'))
