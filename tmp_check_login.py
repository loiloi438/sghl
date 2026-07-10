import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sghl.settings')
import django
django.setup()
from ninja.testing import TestClient
from api.v1.router import api
from accounts.models import User

for username, password in [('tresormouanga', 'Admin@SGHL2026'), ('loiloi', 'Admin@SGHL2026')]:
    user = User.objects.filter(username=username).first()
    print('USER', username, 'exists', bool(user), 'active', getattr(user, 'is_active', None), 'mfa', getattr(user, 'mfa_enabled', None), 'email', getattr(user, 'email', None))
    if user:
        print('   check_password', user.check_password(password))
    client = TestClient(api)
    res = client.post('/auth/login/', json={'username': username, 'password': password})
    print('   status', res.status_code, 'body', res.json() if hasattr(res, 'json') else res.content)
