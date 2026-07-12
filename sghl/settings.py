"""
Django settings for sghl project.
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / '.env')

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-dev-only-change-in-production')
DEBUG = os.getenv('DEBUG', 'True').lower() in ('1', 'true', 'yes')
if os.getenv('ALLOWED_HOSTS'):
    ALLOWED_HOSTS = [h.strip() for h in os.getenv('ALLOWED_HOSTS', '').split(',') if h.strip()]
elif DEBUG:
    # Dev local : autorise l'accès depuis le téléphone (IP LAN) sans config manuelle.
    ALLOWED_HOSTS = ['*']
else:
    ALLOWED_HOSTS = ['localhost', '127.0.0.1']

_render_host = os.getenv('RENDER_EXTERNAL_HOSTNAME', '').strip()
if _render_host and _render_host not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(_render_host)

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'core',
    'accounts',
    'audit',
    'patients',
    'logistics',
    'hospitalisation',
    'soins',
    'prescriptions',
    'laboratoire',
    'pharmacie',
    'facturation',
    'documents',
    'rendezvous',
    'notifications',
    'payments',
    'rh',
    'messagerie',
    'assurance',
    'inventaire',
    'urgences',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'core.middleware.ApiRateLimitMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'sghl.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'sghl.wsgi.application'

def _postgres_database():
    database_url = os.getenv('DATABASE_URL', '').strip()
    if database_url:
        from urllib.parse import unquote, urlparse

        parsed = urlparse(database_url)
        return {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': unquote(parsed.path.lstrip('/')),
            'USER': unquote(parsed.username or ''),
            'PASSWORD': unquote(parsed.password or ''),
            'HOST': parsed.hostname or '',
            'PORT': str(parsed.port or '5432'),
        }

    return {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'sghl'),
        'USER': os.getenv('DB_USER', 'sghl'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'sghl'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }


DB_ENGINE = os.getenv('DB_ENGINE', 'sqlite')

if os.getenv('DATABASE_URL', '').strip() or DB_ENGINE == 'postgresql':
    DATABASES = {'default': _postgres_database()}
else:
    _sqlite_name = os.getenv('SQLITE_NAME', 'db.sqlite3')
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / _sqlite_name,
        }
    }

AUTH_USER_MODEL = 'accounts.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 10}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = os.getenv('LANGUAGE_CODE', 'fr-fr')
TIME_ZONE = os.getenv('TIME_ZONE', 'UTC')
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
SGHL_ETABLISSEMENT = os.getenv('SGHL_ETABLISSEMENT', 'SGHL — Centre Hospitalier')
SGHL_FRONTEND_URL = os.getenv('SGHL_FRONTEND_URL', 'http://localhost:5173')
SGHL_JITSI_DOMAIN = os.getenv('SGHL_JITSI_DOMAIN', 'meet.jit.si')
SGHL_JITSI_ROOM_PREFIX = os.getenv('SGHL_JITSI_ROOM_PREFIX', 'sghl-visio')
SGHL_VISIO_EARLY_MINUTES = int(os.getenv('SGHL_VISIO_EARLY_MINUTES', '15'))
SGHL_VISIO_LATE_MINUTES = int(os.getenv('SGHL_VISIO_LATE_MINUTES', '15'))
SGHL_SUPPORT_EMAIL = os.getenv('SGHL_SUPPORT_EMAIL', 'support@sghl.local')
PDF_SIGNING_KEY = os.getenv('PDF_SIGNING_KEY', SECRET_KEY)
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

JWT_SECRET = os.getenv('JWT_SECRET', SECRET_KEY)
JWT_ACCESS_TOKEN_LIFETIME_MINUTES = int(os.getenv('JWT_ACCESS_TOKEN_LIFETIME_MINUTES', '15'))
JWT_REFRESH_TOKEN_LIFETIME_DAYS = int(os.getenv('JWT_REFRESH_TOKEN_LIFETIME_DAYS', '7'))

CORS_ALLOW_ALL_ORIGINS = DEBUG
CORS_ALLOW_CREDENTIALS = True
_cors_origins = os.getenv('CORS_ALLOWED_ORIGINS', '')
if _cors_origins:
    CORS_ALLOWED_ORIGINS = [o.strip() for o in _cors_origins.split(',') if o.strip()]
elif not DEBUG:
    CORS_ALLOWED_ORIGINS = []

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'sghl-default',
    }
}

LOGIN_RATE_LIMIT_ENABLED = os.getenv('LOGIN_RATE_LIMIT_ENABLED', 'True').lower() in (
    '1',
    'true',
    'yes',
)
LOGIN_RATE_LIMIT_MAX_ATTEMPTS = int(os.getenv('LOGIN_RATE_LIMIT_MAX_ATTEMPTS', '5'))
LOGIN_RATE_LIMIT_WINDOW_SECONDS = int(os.getenv('LOGIN_RATE_LIMIT_WINDOW_SECONDS', '900'))

API_RATE_LIMIT_ENABLED = (
    os.getenv('API_RATE_LIMIT_ENABLED', 'True').lower() in ('1', 'true', 'yes')
    and 'test' not in sys.argv
)
API_RATE_LIMIT_MAX_REQUESTS = int(os.getenv('API_RATE_LIMIT_MAX_REQUESTS', '120'))
API_RATE_LIMIT_WINDOW_SECONDS = int(os.getenv('API_RATE_LIMIT_WINDOW_SECONDS', '60'))

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
]

# Notifications e-mail (rendez-vous, etc.)
EMAIL_NOTIFICATIONS_ENABLED = os.getenv('EMAIL_NOTIFICATIONS_ENABLED', 'True').lower() in (
    '1',
    'true',
    'yes',
)
OTP_MODE = os.getenv(
    'OTP_MODE',
    'development' if DEBUG else 'production',
).strip().lower()
if OTP_MODE not in {'development', 'production'}:
    OTP_MODE = 'production'
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@sghl.local')
SERVER_EMAIL = os.getenv('SERVER_EMAIL', DEFAULT_FROM_EMAIL)
EMAIL_BACKEND = os.getenv(
    'EMAIL_BACKEND',
    'django.core.mail.backends.console.EmailBackend',
)
EMAIL_HOST = os.getenv('EMAIL_HOST', 'localhost')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() in ('1', 'true', 'yes')
EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL', 'False').lower() in ('1', 'true', 'yes')
EMAIL_TIMEOUT = int(os.getenv('EMAIL_TIMEOUT', '15'))
MFA_EMAIL_ASYNC = os.getenv(
    'MFA_EMAIL_ASYNC',
    'False' if DEBUG else 'True',
).lower() in ('1', 'true', 'yes')

# Notifications push (FCM + boîte in-app patient)
PUSH_NOTIFICATIONS_ENABLED = os.getenv('PUSH_NOTIFICATIONS_ENABLED', 'True').lower() in (
    '1',
    'true',
    'yes',
)
FCM_SERVER_KEY = os.getenv('FCM_SERVER_KEY', '')

# Paiements en ligne (Stripe, Mobile Money)
PAYMENTS_STRIPE_SECRET_KEY = os.getenv('PAYMENTS_STRIPE_SECRET_KEY', '')
PAYMENTS_STRIPE_WEBHOOK_SECRET = os.getenv('PAYMENTS_STRIPE_WEBHOOK_SECRET', '')
PAYMENTS_MTN_AGGREGATOR_URL = os.getenv('PAYMENTS_MTN_AGGREGATOR_URL', '')
PAYMENTS_MTN_AGGREGATOR_KEY = os.getenv('PAYMENTS_MTN_AGGREGATOR_KEY', '')
PAYMENTS_MTN_FLUTTERWAVE_URL = os.getenv('PAYMENTS_MTN_FLUTTERWAVE_URL', '')
PAYMENTS_MTN_FLUTTERWAVE_KEY = os.getenv('PAYMENTS_MTN_FLUTTERWAVE_KEY', '')
PAYMENTS_MTN_WEBHOOK_SECRET = os.getenv('PAYMENTS_MTN_WEBHOOK_SECRET', '')
PAYMENTS_AIRTEL_AGGREGATOR_URL = os.getenv('PAYMENTS_AIRTEL_AGGREGATOR_URL', '')
PAYMENTS_AIRTEL_AGGREGATOR_KEY = os.getenv('PAYMENTS_AIRTEL_AGGREGATOR_KEY', '')
PAYMENTS_AIRTEL_WEBHOOK_SECRET = os.getenv('PAYMENTS_AIRTEL_WEBHOOK_SECRET', '')

if not DEBUG:
    SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'True').lower() in ('1', 'true', 'yes')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = int(os.getenv('SECURE_HSTS_SECONDS', '31536000'))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

_INSECURE_SECRET_KEYS = frozenset({
    '',
    'django-insecure-dev-only-change-in-production',
    'change-me-en-production',
    'docker-dev-secret-change-in-production',
    'ci-test-secret-key',
    'ci-e2e-secret-key',
    'e2e-test-secret-key',
})


def _assert_production_security():
    if DEBUG:
        return

    from django.core.exceptions import ImproperlyConfigured

    errors = []

    if SECRET_KEY in _INSECURE_SECRET_KEYS:
        errors.append('SECRET_KEY doit être une valeur forte et unique lorsque DEBUG=False.')

    if not os.getenv('JWT_SECRET', '').strip():
        errors.append('JWT_SECRET doit être défini explicitement lorsque DEBUG=False.')

    if JWT_SECRET in _INSECURE_SECRET_KEYS or JWT_SECRET == SECRET_KEY:
        errors.append('JWT_SECRET doit être fort et distinct de SECRET_KEY lorsque DEBUG=False.')

    if not PDF_SIGNING_KEY or PDF_SIGNING_KEY == SECRET_KEY:
        errors.append('PDF_SIGNING_KEY doit être défini et distinct de SECRET_KEY lorsque DEBUG=False.')

    if not ALLOWED_HOSTS:
        errors.append('ALLOWED_HOSTS ne peut pas être vide lorsque DEBUG=False.')

    if not _cors_origins.strip():
        errors.append('CORS_ALLOWED_ORIGINS doit être renseigné lorsque DEBUG=False.')

    if errors:
        raise ImproperlyConfigured('Configuration production invalide:\n- ' + '\n- '.join(errors))


_assert_production_security()
