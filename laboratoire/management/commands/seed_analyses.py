from django.core.management.base import BaseCommand

from laboratoire.models import AnalyseCatalogue

ANALYSES_DEMO = [
    ('NFS', 'Numération formule sanguine', '', 'Voir normes laboratoire'),
    ('GLY', 'Glycémie à jeun', 'g/L', '0,70 - 1,10'),
    ('CRP', 'Protéine C-réactive', 'mg/L', '< 5'),
    ('CREAT', 'Créatininémie', 'mg/L', '6 - 12'),
    ('UREE', 'Urée sanguine', 'g/L', '0,15 - 0,50'),
    ('IONO', 'Ionogramme sanguin', '', 'Na/K/Cl'),
    ('TP', 'Taux de prothrombine', '%', '70 - 100'),
    ('HIV', 'Dépistage VIH', '', 'Négatif'),
]


class Command(BaseCommand):
    help = 'Charge le catalogue d\'analyses de démonstration.'

    def handle(self, *args, **options):
        created = 0
        for code, libelle, unite, valeur in ANALYSES_DEMO:
            _, was_created = AnalyseCatalogue.objects.get_or_create(
                code=code,
                defaults={
                    'libelle': libelle,
                    'unite_reference': unite,
                    'valeur_reference': valeur,
                },
            )
            if was_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(f'{created} analyse(s) ajoutée(s) au catalogue.'))
