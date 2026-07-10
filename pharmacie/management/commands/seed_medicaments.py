from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from pharmacie.models import MedicamentStock

# (code, libelle, forme, quantite, unite, seuil_alerte, jours_avant_peremption)
# jours négatif = déjà périmé ; stock <= seuil = alerte stock bas ; <= 30 j = alerte péremption
MEDICAMENTS_DEMO = [
    ('PARA1G', 'Paracétamol 1 g', 'comprimé', 420, 'cp', 80, 240),
    ('AMOX500', 'Amoxicilline 500 mg', 'comprimé', 12, 'cp', 30, 180),
    ('IBUP400', 'Ibuprofène 400 mg', 'comprimé', 85, 'cp', 25, 14),
    ('METF850', 'Metformine 850 mg', 'comprimé', 95, 'cp', 20, -45),
    ('CEFTR1G', 'Ceftriaxone 1 g', 'poudre injectable', 38, 'flacon', 10, 120),
    ('SF09', 'Sérum physiologique 0,9 %', 'perfusion', 6, 'poche', 15, 90),
    ('ASP100', 'Aspirine 100 mg', 'comprimé', 8, 'cp', 40, 200),
    ('OMEP20', 'Oméprazole 20 mg', 'gélule', 55, 'gél', 30, 22),
    ('INSUL100', 'Insuline rapide 100 UI/ml', 'stylo', 4, 'stylo', 12, -12),
    ('VITD1000', 'Vitamine D3 1000 UI', 'gélule', 120, 'gél', 25, 9),
    ('LOSAR50', 'Losartan 50 mg', 'comprimé', 180, 'cp', 35, 300),
    ('ATOR20', 'Atorvastatine 20 mg', 'comprimé', 5, 'cp', 20, 150),
    ('SALB100', 'Salbutamol 100 µg/dose', 'inhalateur', 18, 'unité', 8, 28),
    ('HEP5000', 'Héparine 5000 UI/ml', 'ampoule', 22, 'amp', 10, -90),
    ('DEXA4', 'Dexaméthasone 4 mg', 'ampoule', 64, 'amp', 15, 75),
    ('FURO40', 'Furosémide 40 mg', 'comprimé', 3, 'cp', 25, 60),
    ('TRAM50', 'Tramadol 50 mg', 'gélule', 40, 'gél', 15, 18),
    ('MORPH10', 'Morphine 10 mg/ml', 'ampoule', 9, 'amp', 5, -3),
    ('CIPRO500', 'Ciprofloxacine 500 mg', 'comprimé', 70, 'cp', 20, 45),
    ('RANIT150', 'Ranitidine 150 mg', 'comprimé', 2, 'cp', 30, -20),
]


class Command(BaseCommand):
    help = 'Charge ou met à jour le stock pharmacie de démonstration (alertes stock & péremption).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Désactive les médicaments absents de la liste démo.',
        )

    def handle(self, *args, **options):
        today = timezone.localdate()
        created = 0
        updated = 0
        codes_vus = set()

        for row in MEDICAMENTS_DEMO:
            code, libelle, forme, qty, unite, seuil, jours = row
            codes_vus.add(code)
            peremption = today + timedelta(days=jours)
            obj, was_created = MedicamentStock.objects.update_or_create(
                code=code,
                defaults={
                    'libelle': libelle,
                    'forme': forme,
                    'quantite_stock': qty,
                    'unite': unite,
                    'seuil_alerte': seuil,
                    'date_peremption': peremption,
                    'actif': True,
                },
            )
            if was_created:
                created += 1
            else:
                updated += 1

        if options['reset']:
            désactivés = (
                MedicamentStock.objects.exclude(code__in=codes_vus)
                .filter(actif=True)
                .update(actif=False)
            )
            if désactivés:
                self.stdout.write(f'{désactivés} ancien(s) lot(s) désactivé(s).')

        stock_bas = sum(1 for m in MedicamentStock.objects.filter(actif=True) if m.stock_bas)
        peremption = sum(
            1
            for m in MedicamentStock.objects.filter(actif=True, date_peremption__isnull=False)
            if m.est_perime or m.peremption_proche
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Pharmacie : {created} créé(s), {updated} mis à jour — '
                f'{stock_bas} alerte(s) stock bas, {peremption} alerte(s) péremption.'
            )
        )
