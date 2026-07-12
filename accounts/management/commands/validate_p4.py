"""Validation Priorité 4 — endpoints API consommés par l'app mobile patient."""
from django.core.management.base import BaseCommand
from django.test import Client, override_settings


PATIENT_GET_ENDPOINTS = [
    ('Tableau de bord mobile', '/api/v1/patient/tableau-de-bord/'),
    ('Hospitalisations', '/api/v1/patient/hospitalisations/'),
    ('Messages', '/api/v1/patient/messages/'),
    ('Constantes vitales', '/api/v1/patient/constantes-vitales/'),
    ('Plans de soins', '/api/v1/patient/plans-soins/'),
    ('Doses', '/api/v1/patient/doses/'),
    ('Prescriptions', '/api/v1/patient/prescriptions/'),
    ('Résultats laboratoire', '/api/v1/patient/resultats-laboratoire/'),
    ('Factures', '/api/v1/patient/factures/'),
    ('Rendez-vous', '/api/v1/patient/rendez-vous/'),
    ('Médecins RDV', '/api/v1/patient/rendez-vous/medecins/'),
    ('Profil', '/api/v1/patient/profil/'),
    ('Notifications', '/api/v1/patient/notifications/'),
    ('Notifications non lues', '/api/v1/patient/notifications/non-lues/'),
]


class Command(BaseCommand):
    help = 'Exécute les tests API Priorité 4 (parcours mobile patient).'

    def handle(self, *args, **options):
        with override_settings(
            ALLOWED_HOSTS=['testserver', 'localhost', '127.0.0.1'],
        ):
            self._run(Client())

    def _run(self, client):
        results = []

        def ok(label, cond, detail=''):
            status = 'OK' if cond else 'ECHEC'
            results.append((status, label, detail))
            style = self.style.SUCCESS if cond else self.style.ERROR
            self.stdout.write(style(f'[{status}] {label}' + (f' - {detail}' if detail else '')))

        res = client.post(
            '/api/v1/auth/login/',
            {'username': 'patient', 'password': 'Patient@SGHL2026'},
            content_type='application/json',
        )
        tokens = res.json() if res.status_code == 200 else {}
        ok('Connexion patient mobile', res.status_code == 200 and 'access_token' in tokens, f'HTTP {res.status_code}')
        headers = {'HTTP_AUTHORIZATION': f'Bearer {tokens.get("access_token", "")}'}

        for label, path in PATIENT_GET_ENDPOINTS:
            if not tokens.get('access_token'):
                ok(label, False, 'pas de token patient')
                continue
            res = client.get(path, **headers)
            ok(label, res.status_code == 200, f'HTTP {res.status_code}')

        passed = sum(1 for s, _, _ in results if s == 'OK')
        total = len(results)
        self.stdout.write('')
        if passed == total:
            self.stdout.write(self.style.SUCCESS(f'Priorité 4 mobile : {passed}/{total} OK'))
        else:
            self.stdout.write(self.style.ERROR(f'Priorité 4 mobile : {passed}/{total} OK'))
