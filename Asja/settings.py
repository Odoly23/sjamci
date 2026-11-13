"""
Django settings for Asja project.
Variabel sensitif dibaca dari file .env menggunakan python-decouple.
Install: pip install python-decouple
"""

import os
import sys
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

# ── Transporte seguru (HTTPS) ─────────────────────────────────
# Iha produsaun (DEBUG=False) sistema obriga HTTPS. Se servidor seidauk
# iha sertifikadu TLS, define HTTPS_ONLY=False iha .env (la rekomenda).
HTTPS_ONLY = config('HTTPS_ONLY', default=not DEBUG, cast=bool)
if HTTPS_ONLY:
    SECURE_SSL_REDIRECT            = True
    SECURE_PROXY_SSL_HEADER        = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE          = True
    CSRF_COOKIE_SECURE             = True
    SECURE_HSTS_SECONDS            = config('SECURE_HSTS_SECONDS', default=31536000, cast=int)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True

SESSION_COOKIE_HTTPONLY     = True
SESSION_COOKIE_SAMESITE     = 'Lax'
CSRF_COOKIE_SAMESITE        = 'Lax'
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY      = 'same-origin'
X_FRAME_OPTIONS             = 'SAMEORIGIN'   # editor Summernote uza iframe husi orijen hanesan
CSRF_TRUSTED_ORIGINS        = config('CSRF_TRUSTED_ORIGINS', default='', cast=Csv())

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
    'axes',

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
    'axes.middleware.AxesMiddleware',   # tenke ikus liu
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
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
     'OPTIONS': {'min_length': config('PASSWORD_MIN_LENGTH', default=10, cast=int)}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ══════════════════════════════════════════════════════════════
#  PROTESAUN LOGIN (django-axes) — blokeia tentativa barak
# ══════════════════════════════════════════════════════════════
AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',
    'django.contrib.auth.backends.ModelBackend',
]
AXES_FAILURE_LIMIT      = config('LOGIN_FAILURE_LIMIT', default=5, cast=int)
AXES_COOLOFF_TIME       = config('LOGIN_COOLOFF_HOURS', default=0.25, cast=float)  # 15 minutu
AXES_LOCKOUT_PARAMETERS = [['username', 'ip_address']]
AXES_RESET_ON_SUCCESS   = True
AXES_LOCKOUT_TEMPLATE   = 'auth/429.html'
AXES_USERNAME_FORM_FIELD = 'username'


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
# Durante teste automátiku la presiza manifest static (collectstatic)
TESTING = 'test' in sys.argv
STORAGES = {
    'default':     {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage' if TESTING
                    else 'whitenoise.storage.CompressedManifestStaticFilesStorage'},
}

MEDIA_URL  = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Limite upload (10 MB) — evita abuzu memoria/disku
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ══════════════════════════════════════════════════════════════
#  EMAIL
# ══════════════════════════════════════════════════════════════
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_PASS', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='Sistema MCI <info@mci.gov.tl>')
SERVER_EMAIL       = config('SERVER_EMAIL', default=DEFAULT_FROM_EMAIL)
# Simu email bainhira iha erru 500 iha produsaun (ADMIN_EMAIL=a@x.tl,b@x.tl)
ADMINS = [('Admin MCI', e) for e in config('ADMIN_EMAIL', default='', cast=Csv())]


# ══════════════════════════════════════════════════════════════
#  LOGGING
# ══════════════════════════════════════════════════════════════
LOG_DIR = BASE_DIR / 'logs'
LOG_DIR.mkdir(exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{asctime} {levelname} {name} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {'()': 'django.utils.log.RequireDebugFalse'},
    },
    'handlers': {
        'console': {'class': 'logging.StreamHandler', 'formatter': 'verbose'},
        'file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_DIR / 'django.log',
            'maxBytes': 10 * 1024 * 1024,
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'security_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_DIR / 'security.log',
            'maxBytes': 10 * 1024 * 1024,
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
        },
    },
    'loggers': {
        'django': {'handlers': ['console', 'file', 'mail_admins'], 'level': 'INFO'},
        'django.security': {'handlers': ['security_file', 'mail_admins'], 'level': 'INFO', 'propagate': False},
        'axes': {'handlers': ['security_file'], 'level': 'INFO', 'propagate': False},
        'sjamci.security': {'handlers': ['security_file'], 'level': 'INFO', 'propagate': False},
    },
}

# ══════════════════════════════════════════════════════════════
#  API CORS
# ══════════════════════════════════════════════════════════════

# Orijen externu la permite, exetu sira ne'ebé lista iha .env
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS   = config('CORS_ALLOWED_ORIGINS', default='', cast=Csv())

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
SESSION_SAVE_EVERY_REQUEST = True   # sesaun remata oras 1 hafoin atividade ikus
SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin'
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
        'anon':  '60/hour',
        'user': '5000/day',
    },
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
}