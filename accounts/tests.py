import re

from django.contrib.auth.hashers import make_password
from django.core import mail
from django.test import TestCase, override_settings

from accounts.emails import (
    notifier_mfa_active,
    notifier_mfa_code,
    notifier_validation_code,
)
from accounts.mfa_service import generate_secret, verify_totp
from accounts.models import Role, User
from accounts.rate_limit import (
    clear_login_failures,
    is_login_blocked,
    record_login_failure,
)


@override_settings(
    LOGIN_RATE_LIMIT_ENABLED=True,
    LOGIN_RATE_LIMIT_MAX_ATTEMPTS=3,
    LOGIN_RATE_LIMIT_WINDOW_SECONDS=900,
)
class LoginRateLimitTests(TestCase):
    def test_blocks_after_max_failures(self):
        ip, user = '127.0.0.1', 'admin'
        self.assertFalse(is_login_blocked(ip, user))
        for _ in range(3):
            record_login_failure(ip, user)
        self.assertTrue(is_login_blocked(ip, user))
        clear_login_failures(ip, user)
        self.assertFalse(is_login_blocked(ip, user))


class MfaServiceTests(TestCase):
    def test_totp_roundtrip(self):
        secret = generate_secret()
        import pyotp

        code = pyotp.TOTP(secret).now()
        self.assertTrue(verify_totp(secret, code))
        self.assertFalse(verify_totp(secret, '000000'))


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    EMAIL_NOTIFICATIONS_ENABLED=True,
)
class PatientRegistrationTests(TestCase):
    def test_inscription_patient(self):
        from ninja.testing import TestClient

        from api.v1.router import api

        client = TestClient(api)
        res = client.post(
            '/auth/register/patient/',
            json={
                'nom': 'KIMBEMBE',
                'prenom': 'Marie',
                'date_naissance': '1988-03-12',
                'sexe': 'F',
                'email': 'marie.test@sghl.local',
                'telephone': '+2420600111222',
                'password': 'Xy9!SecurePass2026',
                'password_confirm': 'Xy9!SecurePass2026',
                'consentement_rgpd': True,
            },
        )
        self.assertEqual(res.status_code, 200, res.content)
        body = res.json()
        self.assertIn('username', body)
        self.assertIn('detail', body)
        # should send validation code + welcome email when possible
        self.assertEqual(len(mail.outbox), 2)

    def test_inscription_sans_consentement_refusee(self):
        from ninja.testing import TestClient

        from api.v1.router import api

        client = TestClient(api)
        res = client.post(
            '/auth/register/patient/',
            json={
                'nom': 'X',
                'prenom': 'Y',
                'date_naissance': '1990-01-01',
                'sexe': 'M',
                'email': 'x@test.local',
                'password': 'Test@2026',
                'password_confirm': 'Test@2026',
                'consentement_rgpd': False,
            },
        )
        self.assertEqual(res.status_code, 400)

    def test_validation_code_activation(self):
        from django.core import mail
        from ninja.testing import TestClient

        from api.v1.router import api
        from accounts.models import AccountValidation, User

        client = TestClient(api)
        register_res = client.post(
            '/auth/register/patient/',
            json={
                'nom': 'KIMBEMBE',
                'prenom': 'Marie',
                'date_naissance': '1988-03-12',
                'sexe': 'F',
                'email': 'marie.validation@sghl.local',
                'telephone': '+2420600111222',
                'password': 'Xy9!SecurePass2026',
                'password_confirm': 'Xy9!SecurePass2026',
                'consentement_rgpd': True,
            },
        )
        self.assertEqual(register_res.status_code, 200, register_res.content)
        username = register_res.json()['username']

        self.assertGreaterEqual(len(mail.outbox), 1)
        validation_messages = [m for m in mail.outbox if 'Validation de votre compte' in m.subject]
        self.assertEqual(
            len(validation_messages),
            1,
            f'Expected exactly one validation email, got {len(validation_messages)}',
        )
        body = validation_messages[0].body
        match = re.search(r'code de validation\s*:\s*([0-9]{6})', body, re.IGNORECASE)
        self.assertIsNotNone(match, 'Validation code should appear in validation email body')
        code = match.group(1)

        validate_res = client.post('/auth/validate/', json={'username': username, 'code': code})
        self.assertEqual(validate_res.status_code, 200, validate_res.content)
        payload = validate_res.json()
        self.assertIn('access_token', payload)
        self.assertIn('refresh_token', payload)

        user = User.objects.get(username=username)
        self.assertTrue(user.is_active)
        validation = AccountValidation.objects.filter(user=user, used=True).first()
        self.assertIsNotNone(validation)

    def test_validation_code_invalid(self):
        from ninja.testing import TestClient

        from api.v1.router import api

        client = TestClient(api)
        register_res = client.post(
            '/auth/register/patient/',
            json={
                'nom': 'KIMBEMBE',
                'prenom': 'Marie',
                'date_naissance': '1988-03-12',
                'sexe': 'F',
                'email': 'marie.validation2@sghl.local',
                'telephone': '+2420600111223',
                'password': 'Xy9!SecurePass2026',
                'password_confirm': 'Xy9!SecurePass2026',
                'consentement_rgpd': True,
            },
        )
        self.assertEqual(register_res.status_code, 200, register_res.content)

        invalid_res = client.post(
            '/auth/validate/',
            json={'username': register_res.json()['username'], 'code': 'WRONG1'},
        )
        self.assertEqual(invalid_res.status_code, 400)

    def test_validation_code_resend(self):
        from ninja.testing import TestClient

        from api.v1.router import api

        client = TestClient(api)
        register_res = client.post(
            '/auth/register/patient/',
            json={
                'nom': 'KIMBEMBE',
                'prenom': 'Marie',
                'date_naissance': '1988-03-12',
                'sexe': 'F',
                'email': 'marie.resend@sghl.local',
                'telephone': '+2420600111224',
                'password': 'Xy9!SecurePass2026',
                'password_confirm': 'Xy9!SecurePass2026',
                'consentement_rgpd': True,
            },
        )
        self.assertEqual(register_res.status_code, 200, register_res.content)
        username = register_res.json()['username']

        self.assertEqual(len(mail.outbox), 2)
        original_validation_emails = [m for m in mail.outbox if 'Validation de votre compte' in m.subject]
        self.assertEqual(len(original_validation_emails), 1)

        resend_res = client.post('/auth/validate/resend/', json={'username': username})
        self.assertEqual(resend_res.status_code, 200, resend_res.content)
        self.assertIn('detail', resend_res.json())

        self.assertEqual(len(mail.outbox), 3)
        validation_emails = [m for m in mail.outbox if 'Validation de votre compte' in m.subject]
        self.assertEqual(len(validation_emails), 2)

    def test_validation_code_for_staff_user(self):
        from ninja.testing import TestClient

        from api.v1.router import api

        client = TestClient(api)
        user = User.objects.create_user(
            username='staff_new',
            password='Xy9!SecurePass2026',
            email='staff.new@sghl.local',
            role=Role.MEDECIN,
            is_active=False,
            mfa_enabled=True,
        )
        code = '123456'
        from accounts.models import AccountValidation

        AccountValidation.objects.create(user=user, code_hash=make_password(code))

        validate_res = client.post('/auth/validate/', json={'username': user.username, 'code': code})
        self.assertEqual(validate_res.status_code, 200, validate_res.content)

        user.refresh_from_db()
        self.assertTrue(user.is_active)


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    EMAIL_NOTIFICATIONS_ENABLED=True,
    SGHL_FRONTEND_URL='http://localhost:5173',
)
class PasswordResetTests(TestCase):
    def test_forgot_ne_revele_pas_existence(self):
        from ninja.testing import TestClient

        from api.v1.router import api

        client = TestClient(api)
        User.objects.create_user(
            username='reset_me',
            password='OldPass@2026',
            email='reset_me@test.local',
            role=Role.PATIENT,
        )
        res = client.post('/auth/password/forgot/', json={'identifiant': 'reset_me'})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)

        res_unknown = client.post('/auth/password/forgot/', json={'identifiant': 'nobody'})
        self.assertEqual(res_unknown.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    EMAIL_NOTIFICATIONS_ENABLED=True,
)
class MfaEmailTests(TestCase):
    def test_notification_mfa_active(self):
        user = User.objects.create_user(
            username='staff_mfa_mail',
            password='x',
            role=Role.MEDECIN,
            email='staff.mfa@test.local',
            first_name='Alice',
            last_name='Demo',
        )
        self.assertTrue(notifier_mfa_active(user.id))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('deux facteurs', mail.outbox[0].body)
        self.assertEqual(mail.outbox[0].to, ['staff.mfa@test.local'])


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    EMAIL_NOTIFICATIONS_ENABLED=False,
    OTP_MODE='development',
)
class MfaDevelopmentModeTests(TestCase):
    def test_mfa_code_logs_instead_of_fails(self):
        user = User.objects.create_user(
            username='staff_mfa_dev',
            password='x',
            role=Role.MEDECIN,
            email='',
            first_name='Bob',
            last_name='Dev',
        )
        from django.core import mail

        self.assertTrue(notifier_mfa_code(user.id, '123456'))
        self.assertEqual(len(mail.outbox), 0)

    def test_validation_code_logs_instead_of_fails(self):
        from patients.models import Patient

        user = User.objects.create_user(
            username='patient_dev',
            password='x',
            role=Role.PATIENT,
            email='',
            first_name='Dev',
            last_name='Patient',
        )
        patient = Patient.objects.create(
            numero_dossier='P-2026-999',
            nom='Patient',
            prenom='Dev',
            date_naissance='1990-01-01',
            sexe='M',
            telephone='+2420600000000',
            email='',
            consentement_donnees=True,
            compte_utilisateur=user,
        )
        self.assertTrue(notifier_validation_code(user.id, patient.id, 'ABC123'))
        self.assertEqual(len(mail.outbox), 0)


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    EMAIL_NOTIFICATIONS_ENABLED=True,
)
class StaffMfaLoginTests(TestCase):
    def test_staff_login_requires_mfa_email_code(self):
        from ninja.testing import TestClient

        from api.v1.router import api

        client = TestClient(api)
        User.objects.create_user(
            username='medecin_mfa',
            password='Medecin@SGHL2026',
            email='medecin.mfa@sghl.local',
            role=Role.MEDECIN,
            mfa_enabled=True,
            is_active=True,
        )

        login_res = client.post(
            '/auth/login/',
            json={'username': 'medecin_mfa', 'password': 'Medecin@SGHL2026'},
        )
        self.assertEqual(login_res.status_code, 202, login_res.content)

        mfa_messages = [m for m in mail.outbox if 'Code de connexion' in m.subject]
        self.assertEqual(len(mfa_messages), 1)
        match = re.search(r'([0-9]{6})', mfa_messages[0].body)
        self.assertIsNotNone(match, 'Le code MFA doit figurer dans l\'e-mail')
        code = match.group(1)

        mfa_res = client.post(
            '/auth/login/mfa/',
            json={'username': 'medecin_mfa', 'code': code},
        )
        self.assertEqual(mfa_res.status_code, 200, mfa_res.content)
        body = mfa_res.json()
        self.assertIn('access_token', body)
        self.assertIn('refresh_token', body)

    def test_staff_without_mfa_cannot_login(self):
        from ninja.testing import TestClient

        from api.v1.router import api

        client = TestClient(api)
        User.objects.create_user(
            username='medecin_no_mfa',
            password='Medecin@SGHL2026',
            email='medecin.nomfa@sghl.local',
            role=Role.MEDECIN,
            mfa_enabled=False,
            is_active=True,
        )

        login_res = client.post(
            '/auth/login/',
            json={'username': 'medecin_no_mfa', 'password': 'Medecin@SGHL2026'},
        )
        self.assertEqual(login_res.status_code, 403, login_res.content)

    def test_inactive_patient_cannot_login_before_validation(self):
        from ninja.testing import TestClient

        from api.v1.router import api

        client = TestClient(api)
        User.objects.create_user(
            username='patient_inactif',
            password='Patient@SGHL2026',
            email='patient.inactif@sghl.local',
            role=Role.PATIENT,
            is_active=False,
        )

        login_res = client.post(
            '/auth/login/',
            json={'username': 'patient_inactif', 'password': 'Patient@SGHL2026'},
        )
        self.assertEqual(login_res.status_code, 403, login_res.content)


class PersonnelPermissionsTests(TestCase):
    def setUp(self):
        from ninja.testing import TestClient

        from api.v1.router import api

        self.client = TestClient(api)
        self.medecin = User.objects.create_user(
            username='medecin_personnel',
            password='x',
            role=Role.MEDECIN,
        )
        self.patient = User.objects.create_user(
            username='patient_personnel',
            password='x',
            role=Role.PATIENT,
        )

    def test_patient_ne_peut_pas_lister_le_personnel(self):
        from accounts.test_helpers import auth_headers

        response = self.client.get(
            '/personnel/medecins/',
            headers=auth_headers(self.patient),
        )
        self.assertEqual(response.status_code, 403)

    def test_staff_peut_lister_les_medecins(self):
        from accounts.test_helpers import auth_headers

        response = self.client.get(
            '/personnel/medecins/',
            headers=auth_headers(self.medecin),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]['username'], self.medecin.username)
