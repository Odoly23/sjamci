"""
Konfigurasaun produsaun ba SJAMCI.

Uza ho:  DJANGO_SETTINGS_MODULE=Asja.settings_prod

Herda hotu husi ``Asja.settings`` no obriga valór seguru ne'ebé la bele
hamamuk husi .env: DEBUG sempre False no HTTPS sempre obrigatóriu.
"""
from decouple import config, Csv
from django.core.exceptions import ImproperlyConfigured

from .settings import *  # noqa: F401,F403

DEBUG = False

# ── HTTPS obrigatóriu ─────────────────────────────────────────
HTTPS_ONLY                     = True
SECURE_SSL_REDIRECT            = True
SECURE_PROXY_SSL_HEADER        = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE          = True
CSRF_COOKIE_SECURE             = True
SECURE_HSTS_SECONDS            = config('SECURE_HSTS_SECONDS', default=63072000, cast=int)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD            = True

# ── Verifikasaun konfigurasaun molok hahú ─────────────────────
if '*' in ALLOWED_HOSTS or not ALLOWED_HOSTS:
    raise ImproperlyConfigured("ALLOWED_HOSTS tenke lista domíniu loloos iha produsaun (la bele '*').")
if len(SECRET_KEY) < 50:
    raise ImproperlyConfigured('SECRET_KEY badak liu; uza pelumenus karakter 50 aleatóriu.')
if DATABASES['default']['ENGINE'].endswith('sqlite3'):
    raise ImproperlyConfigured('Produsaun tenke uza baze-dadus servidór (DB_ENGINE), la\'ós SQLite.')

# Ligasaun baze-dadus ho TLS (opsionál)
if config('DB_USE_SSL', default=False, cast=bool):
    DATABASES['default']['OPTIONS'] = {'ssl': {'ca': config('DB_CA_CERT', default='')}}
DATABASES['default']['CONN_MAX_AGE'] = 60
