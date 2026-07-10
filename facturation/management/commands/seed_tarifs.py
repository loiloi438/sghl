from decimal import Decimal

from django.core.management.base import BaseCommand

from facturation.models import CategorieTarif, TarifActe

TARIFS_DEMO = [
    ('ADMISSION', 'Frais d\'admission', CategorieTarif.SEJOUR, Decimal('15000')),
    ('SEJOUR_JOUR', 'Forfait journalier hospitalisation', CategorieTarif.SEJOUR, Decimal('25000')),
    ('LAB_ANALYSE', 'Analyse de laboratoire', CategorieTarif.LABORATOIRE, Decimal('8000')),
    ('PHARMA_LIGNE', 'Dispensation médicament', CategorieTarif.PHARMACIE, Decimal('3500')),
    ('CONSULT', 'Consultation spécialiste', CategorieTarif.DIVERS, Decimal('12000')),
    ('SOINS_INF', 'Acte infirmier', CategorieTarif.SOINS, Decimal('5000')),
]


class Command(BaseCommand):
    help = 'Charge le catalogue tarifaire de démonstration.'

    def handle(self, *args, **options):
        created = 0
        for code, libelle, categorie, prix in TARIFS_DEMO:
            _, was_created = TarifActe.objects.get_or_create(
                code=code,
                defaults={
                    'libelle': libelle,
                    'categorie': categorie,
                    'prix_unitaire': prix,
                },
            )
            if was_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(f'{created} tarif(s) ajouté(s).'))
