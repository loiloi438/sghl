import os
import traceback
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sghl.settings')
import django
django.setup()
from accounts.models import User
from ninja.testing import TestClient
from api.v1.router import api
import pyotp

# Retrieve MFA secret for existing admin
username = 'tresormouanga'
try:
    user = User.objects.get(username=username)
    print('username:', user.username)
    print('email:', user.email)
    print('role:', user.role)
    print('is_active:', user.is_active)
    print('mfa_enabled:', user.mfa_enabled)
    print('mfa_secret:', user.mfa_secret)
    if user.mfa_secret:
        totp = pyotp.TOTP(user.mfa_secret).now()
        print('current_totp:', totp)
except User.DoesNotExist:
    print('user_not_found')

# Test admin login with MFA
client = TestClient(api)
for username, password in [('tresormouanga', '02060024@tr')]:
    print('\nTesting login for', username)
    payload = {'username': username, 'password': password, 'totp_code': totp}
    res = client.post('/auth/login/', json=payload)
    print('status', res.status_code)
    try:
        print('body', res.json())
    except Exception:
        print('content', res.content)

# Create a patient account test
patient_email = f'test.patient.{os.getpid()}@sghl.local'
print('\nCreating patient account', patient_email)
payload = {
    'nom': 'Test',
    'prenom': 'Patient',
    'date_naissance': '1990-01-01',
    'sexe': 'M',
    'email': patient_email,
    'telephone': '+2420600999001',
    'password': 'TestPassword@2026',
    'password_confirm': 'TestPassword@2026',
    'consentement_rgpd': True,
}
res = client.post('/auth/register/patient/', json=payload)
print('register status', res.status_code)
try:
    print('register body', res.json())
except Exception:
    print('register content', res.content)
