import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sghl.settings')
django.setup()

from django.core.mail import EmailMessage

try:
    msg = EmailMessage('Test SMTP SGHL', 'Ceci est un test SMTP depuis SGHL', to=['mouangatresor673@gmail.com'])
    r = msg.send(fail_silently=False)
    print('send result', r)
except Exception as e:
    print('send error', e)
