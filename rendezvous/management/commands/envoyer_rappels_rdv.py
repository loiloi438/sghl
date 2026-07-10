from django.core.management.base import BaseCommand

from rendezvous.rappels import envoyer_rappels_j1


class Command(BaseCommand):
    help = (
        'Envoie les e-mails de rappel J-1 pour les rendez-vous planifiés ou confirmés '
        'dont la date est demain (fuseau TIME_ZONE du projet).'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Compte les envois sans envoyer ni marquer les RDV.',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        if dry_run:
            self.stdout.write(self.style.WARNING('Mode dry-run : aucun e-mail envoyé.'))

        stats = envoyer_rappels_j1(dry_run=dry_run)

        self.stdout.write(
            f"Éligibles : {stats['total_eligibles']} | "
            f"Envoyés : {stats['envoyes']} | "
            f"Sans e-mail : {stats['ignores_sans_email']} | "
            f"Échecs : {stats['echecs']}"
        )

        if stats['echecs']:
            self.stderr.write(self.style.ERROR('Certains rappels ont échoué (voir les logs).'))
