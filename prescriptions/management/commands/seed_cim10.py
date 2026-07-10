from django.core.management.base import BaseCommand

from prescriptions.models import DiagnosticCIM10

CIM10_DEMO = [
    ('J06.9', 'Infection aiguë des voies respiratoires supérieures, sans précision'),
    ('J18.9', 'Pneumonie, sans précision'),
    ('I10', 'Hypertension essentielle (primitive)'),
    ('E11.9', 'Diabète sucré de type 2, sans complication'),
    ('K35.8', 'Appendicite aiguë, autres formes et sans précision'),
    ('R50.9', 'Fièvre, sans précision'),
    ('N39.0', 'Infection des voies urinaires, site non précisé'),
    ('J02.9', 'Pharyngite aiguë, sans précision'),
]


class Command(BaseCommand):
    help = 'Charge des codes CIM-10 de démonstration.'

    def handle(self, *args, **options):
        created = 0
        for code, libelle in CIM10_DEMO:
            _, was_created = DiagnosticCIM10.objects.get_or_create(
                code=code,
                defaults={'libelle': libelle},
            )
            if was_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(f'{created} code(s) CIM-10 ajouté(s).'))
