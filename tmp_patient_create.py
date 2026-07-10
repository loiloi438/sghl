import os
import traceback
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sghl.settings')
import django
django.setup()
from ninja.testing import TestClient
from api.v1.router import api

payload = {
    'nom': 'Test',
    'prenom': 'Patient',
    'date_naissance': '1990-01-01',
    'sexe': 'M',
    'email': f'test.patient.{os.getpid()}@sghl.local',
    'telephone': '+2420600999002',
    'password': 'TestPassword@2026',
    'password_confirm': 'TestPassword@2026',
    'consentement_rgpd': True,
}
client = TestClient(api)
print('payload', payload)
res = client.post('/auth/register/patient/', json=payload)
print('status', res.status_code)
try:
    print('body', res.json())
except Exception:
    print('content', res.content)
