import os
import re
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sghl.settings')
os.environ.setdefault('EMAIL_BACKEND', 'django.core.mail.backends.locmem.EmailBackend')
os.environ.setdefault('EMAIL_NOTIFICATIONS_ENABLED', 'True')
os.environ.setdefault('OTP_MODE', 'development')
import django

django.setup()

from ninja.testing import TestClient
from django.core import mail
from accounts.models import User, AccountValidation
from api.v1.router import api


def run_mfa_flow():
    print('--- MFA auth flow ---')
    client = TestClient(api)
    username = 'mouangatresor'
    password = '02060024@tr'
    response = client.post('/auth/login/', json={'username': username, 'password': password})
    print('login status:', response.status_code)
    try:
        print('login body:', response.json())
    except Exception:
        print('login content:', response.content)

    validation = AccountValidation.objects.filter(user__username=username, used=False).order_by('-created_at').first()
    print('validation exists:', bool(validation))
    if validation:
        print('validation created_at:', validation.created_at)
        print('validation attempts:', validation.attempts)
    print('emails sent:', len(mail.outbox))
    if mail.outbox:
        last = mail.outbox[-1]
        print('last email subject:', last.subject)
        print('last email body snippet:', last.body[:300].replace('\n', ' '))
        match = re.search(r'(\d{6})', last.body)
        print('found code:', bool(match))
        if match:
            code = match.group(1)
            response2 = client.post('/auth/login/mfa/', json={'username': username, 'code': code})
            print('mfa status:', response2.status_code)
            try:
                print('mfa body:', response2.json())
            except Exception:
                print('mfa content:', response2.content)
            if response2.status_code == 200:
                token = response2.json().get('access_token')
                me = client.get('/auth/me/', headers={'Authorization': f'Bearer {token}'})
                print('me status:', me.status_code)
                try:
                    print('me body:', me.json())
                except Exception:
                    print('me content:', me.content)


def run_patient_registration():
    print('\n--- Patient registration flow ---')
    mail.outbox.clear()
    client = TestClient(api)
    timestamp = int(time.time())
    payload = {
        'nom': 'Test',
        'prenom': 'Patient',
        'date_naissance': '1995-05-05',
        'sexe': 'F',
        'email': f'test.patient.{timestamp}@sghl.local',
        'telephone': '+2420600111222',
        'password': 'Xy9!SecurePass2026',
        'password_confirm': 'Xy9!SecurePass2026',
        'consentement_rgpd': True,
    }
    response = client.post('/auth/register/patient/', json=payload)
    print('register status:', response.status_code)
    try:
        print('register body:', response.json())
    except Exception:
        print('register content:', response.content)
    print('emails sent:', len(mail.outbox))
    validation_emails = [m for m in mail.outbox if 'Validation de votre compte' in m.subject]
    print('validation emails found:', len(validation_emails))
    if validation_emails:
        body = validation_emails[-1].body
        match = re.search(r'(\d{6})', body)
        print('validation code found:', bool(match), match.group(1) if match else None)
        if match:
            code = match.group(1)
            username = response.json().get('username')
            validate = client.post('/auth/validate/', json={'username': username, 'code': code})
            print('validate status:', validate.status_code)
            try:
                print('validate body:', validate.json())
            except Exception:
                print('validate content:', validate.content)


if __name__ == '__main__':
    run_mfa_flow()
    run_patient_registration()
