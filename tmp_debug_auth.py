import os
import traceback
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sghl.settings')
import django
django.setup()
from accounts.models import User
from accounts.registration_service import inscrire_patient
from datetime import date

print('admins', list(User.objects.filter(role='admin').values('username','is_active','mfa_enabled','email')))
print('admin_exists', User.objects.filter(username='admin').exists())
print('tresor_exists', User.objects.filter(username='tresormouanga').exists())
print('admin_usernames', list(User.objects.filter(role='admin').values_list('username', flat=True)))
try:
    user = inscrire_patient(
        nom='Test', prenom='Patient', date_naissance=date(1990,1,1), sexe='M', email='test.patient@example.com', telephone='', password='Test@1234', password_confirm='Test@1234', consentement_rgpd=True
    )
    print('created', user.username, user.email, user.is_active)
except Exception:
    traceback.print_exc()
