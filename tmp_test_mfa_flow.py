import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','sghl.settings')
import django
django.setup()
from ninja.testing import TestClient
from api.v1.router import api

client = TestClient(api)
print('step1: password only')
res = client.post('/auth/login/', json={'username':'tresormouanga','password':'02060024@tr'})
print('status', res.status_code)
try:
    print('body', res.json())
except Exception:
    print('content', res.content)

# find code sent (from AccountValidation)
from accounts.models import AccountValidation, User
user = User.objects.get(username='tresormouanga')
val = AccountValidation.objects.filter(user=user, used=False).order_by('-created_at').first()
print('validation exists', bool(val), getattr(val,'attempts',None), getattr(val,'created_at',None))

if val:
    # try login/mfa with wrong code
    print('\nstep2: invalid code')
    r2 = client.post('/auth/login/mfa/', json={'username':'tresormouanga','code':'000000'})
    print('status', r2.status_code)
    try:
        print('body', r2.json())
    except Exception:
        print('content', r2.content)

    # we cannot read the actual code (it's hashed), but we can simulate by reading last email from django.core.mail.outbox
    from django.core import mail
    if mail.outbox:
        print('\nemail subject:', mail.outbox[-1].subject)
        print('email body:', mail.outbox[-1].body)
        import re
        m = re.search(r'(\d{6})', mail.outbox[-1].body)
        if m:
            code = m.group(1)
            print('\nusing code from email:', code)
            r3 = client.post('/auth/login/mfa/', json={'username':'tresormouanga','code':code})
            print('status', r3.status_code)
            try:
                print('body', r3.json())
            except Exception:
                print('content', r3.content)
