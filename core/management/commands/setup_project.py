from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = (
        'Prépare la base SGHL : migrations à jour, puis données de démonstration '
        '(admin + seed_demo).'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-seed',
            action='store_true',
            help='Appliquer uniquement les migrations, sans recharger les seeds.',
        )

    def handle(self, *args, **options):
        self.stdout.write('Vérification des migrations…')
        call_command('makemigrations', verbosity=1)
        call_command('migrate', verbosity=1)

        tables = set(connection.introspection.table_names())
        if 'rendezvous_rendezvous' in tables:
            self.stdout.write(self.style.SUCCESS('Table rendezvous_rendezvous : OK'))
        else:
            self.stdout.write(
                self.style.WARNING(
                    'Table rendezvous absente — vérifiez INSTALLED_APPS et migrate.'
                )
            )

        pending = []
        from io import StringIO

        out = StringIO()
        call_command('showmigrations', '--plan', stdout=out)
        for line in out.getvalue().splitlines():
            if line.strip().startswith('[ ]'):
                pending.append(line.strip())

        if pending:
            self.stdout.write(self.style.ERROR('Migrations non appliquées :'))
            for line in pending:
                self.stdout.write(f'  {line}')
            return

        self.stdout.write(self.style.SUCCESS('Toutes les migrations sont appliquées.'))

        if options['skip_seed']:
            return

        self.stdout.write('Chargement des données de démonstration…')
        call_command('seed_admin', verbosity=1)
        call_command('seed_demo', verbosity=1)
        self.stdout.write(self.style.SUCCESS('Projet prêt (migrations + seeds).'))
