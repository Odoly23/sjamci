"""
Django settings for Asja project.
Variabel sensitif dibaca dari file .env menggunakan python-decouple.
Install: pip install python-decouple
"""

import os
from pathlib import Path
from django.contrib.messages import constants as message_constants
from decouple import config, Csv
from django.utils.translation import gettext_lazy as _


# ══════════════════════════════════════════════════════════════
#  PATH
# ══════════════════════════════════════════════════════════════
BASE_DIR = Path(__file__).resolve().parent.parent


# ══════════════════════════════════════════════════════════════
#  KEAMANAN
# ══════════════════════════════════════════════════════════════
SECRET_KEY = config('SECRET_KEY')
DEBUG       = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())
MAPBOX_TOKEN  = config('MAPBOX_TOKEN', default='')
MAPBOX_TOKENS = config('MAPBOX_TOKENS', default='')
GOOGLE_KEY    = config('google_key', default='')

# ══════════════════════════════════════════════════════════════
#  APLIKASAUN
# ══════════════════════════════════════════════════════════════
INSTALLED_APPS = [
    # Django bawaan
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    # Third-party
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'django_cleanup',
    'import_export',
    'crispy_forms',
    'crispy_bootstrap4',
    'django_summernote',
    'widget_tweaks',
    'django_select2',

    # Aplikasi lokal
    'main',
    'custom',
    'benefisiariu',
    'kni.apps.KniConfig',
    'suave',
    'manufatureira',
    'notif',
    'report',
    'users',
    'mpms',
    'monitoring'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',      
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'corsheaders.middleware.CorsMiddleware',            
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'Asja.middleware.SecurityAndCacheMiddleware',
    'Asja.middleware.PreventDuplicatePostMiddleware',
]

ROOT_URLCONF = 'Asja.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'Asja.wsgi.application'

_db_engine = config('DB_ENGINE', default='')

if _db_engine:
    DATABASES = {
        'default': {
            'ENGINE':   _db_engine,
            'NAME':     config('DB_NAME'),
            'USER':     config('DB_USER'),
            'PASSWORD': config('DB_PASSWORD'),
            'HOST':     config('DB_HOST', default='localhost'),
            'PORT':     config('DB_PORT', default='3306'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME':   BASE_DIR / 'db.sqlite3',
        }
    }


# ══════════════════════════════════════════════════════════════
#  PASSWORD VALIDATION
# ══════════════════════════════════════════════════════════════
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ══════════════════════════════════════════════════════════════
#  INTERNASIONALISASI
# ══════════════════════════════════════════════════════════════
LANGUAGE_CODE = 'pt'
TIME_ZONE     = 'Asia/Dili'
USE_I18N      = True
USE_TZ        = True

LANGUAGES = [
    ('tet', _('Tetun (Dili)')),
    ('pt', _('Português')),
    ('en', _('English')),
]

# ══════════════════════════════════════════════════════════════
#  STATIC & MEDIA
# ══════════════════════════════════════════════════════════════
STATIC_URL  = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL  = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ══════════════════════════════════════════════════════════════
#  EMAIL
# ══════════════════════════════════════════════════════════════
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_PASS')
DEFAULT_FROM_EMAIL = f'Sistema MCI <info@mci.gov.tl>'


# ══════════════════════════════════════════════════════════════
#  LOGGING
# ══════════════════════════════════════════════════════════════
LOG_DIR = BASE_DIR / 'logs'
LOG_DIR.mkdir(exist_ok=True)

# ══════════════════════════════════════════════════════════════
#  API CORS
# ══════════════════════════════════════════════════════════════

CORS_ALLOW_ALL_ORIGINS = True

# ══════════════════════════════════════════════════════════════
#  CRISPY FORMS
# ══════════════════════════════════════════════════════════════
CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap4'
CRISPY_TEMPLATE_PACK          = 'bootstrap4'


# ══════════════════════════════════════════════════════════════
#  AUTH & LOGIN
# ══════════════════════════════════════════════════════════════
LOGIN_REDIRECT_URL = 'home'
LOGIN_URL          = 'login'

ABSOLUTE_URL_OVERRIDES = {
    'auth.user': lambda u: '/users/users/',
}
# ══════════════════════════════════════════════════════════════
#  SECURITY SESSIOn
# ══════════════════════════════════════════════════════════════
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 60 * 60  
SECURE_CROSS_ORIGIN_OPENER_POLICY = None
# ══════════════════════════════════════════════════════════════
#  MESSAGE TAGS
# ══════════════════════════════════════════════════════════════
MESSAGE_TAGS = {
    message_constants.DEBUG:   'debug',
    message_constants.INFO:    'info',
    message_constants.SUCCESS: 'success',
    message_constants.WARNING: 'warning',
    message_constants.ERROR:   'danger',
}


# ══════════════════════════════════════════════════════════════
#  REST FRAMEWORK
# ══════════════════════════════════════════════════════════════
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon':  '100/day',
        'user': '1000/day',
    },
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
}