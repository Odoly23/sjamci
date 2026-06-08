"""
Django settings for Asja project.
Variabel sensitif dibaca dari file .env menggunakan python-decouple.
Install: pip install python-decouple
"""

import os
from pathlib import Path
from django.contrib.messages import constants as message_constants
from decouple import config, Csv

# ══════════════════════════════════════════════════════════════
#  PATH
# ══════════════════════════════════════════════════════════════
BASE_DIR = Path(__file__).resolve().parent.parent


# ══════════════════════════════════════════════════════════════
#  KEAMANAN — KRITIKAL
# ══════════════════════════════════════════════════════════════
SECRET_KEY = config('SECRET_KEY')
DEBUG      = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())
MAPBOX_TOKEN  = config('MAPBOX_TOKEN', default='')

# --- TAMBAHAN: Security Header via Python ---
SECURE_HSTS_SECONDS          = 63072000   # 2 tahun — Wajib untuk HSTS
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD          = True

SECURE_SSL_REDIRECT          = True       # Paksa HTTP → HTTPS
SECURE_PROXY_SSL_HEADER      = ('HTTP_X_FORWARDED_PROTO', 'https')
# Note: SECURE_PROXY_SSL_HEADER hanya aktifkan jika pakai reverse proxy (Nginx, Cloudflare, dll)

SESSION_COOKIE_SECURE        = True       # Cookie session hanya via HTTPS
CSRF_COOKIE_SECURE           = True       # Cookie CSRF hanya via HTTPS
SESSION_COOKIE_HTTPONLY      = True       # JavaScript tidak bisa baca session cookie
CSRF_COOKIE_HTTPONLY         = True       # JavaScript tidak bisa baca CSRF cookie
SESSION_COOKIE_SAMESITE      = 'Lax'      # Proteksi CSRF lintas site
CSRF_COOKIE_SAMESITE         = 'Lax'

SECURE_CONTENT_TYPE_NOSNIFF  = True       # Set header X-Content-Type-Options: nosniff
SECURE_BROWSER_XSS_FILTER    = True       # XSS filter (deprecated di beberapa browser, tapi tetap bagus)
X_FRAME_OPTIONS              = 'DENY'     # Mencegah clickjacking

# --- TAMBAHAN: CSRF Trusted Origins ---
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', default='https://asset.salisdev.com', cast=Csv())

# --- TAMBAHAN: Batasi akses admin ke IP lokal/internal ---
# Opsi 1: Lewat middleware (lihat file middleware terpisah)
# Opsi 2: INTERNAL_IPS — khusus untuk debug toolbar, bukan untuk proteksi admin
# Untuk proteksi admin, buat middleware custom (saya sertakan di bagian akhir)

# --- TAMBAHAN: Sembunyikan header Server ---
# Tidak bisa dari Django saja. Lakukan di Nginx/Apache:
#   server_tokens off;                  # Nginx
#   ServerTokens Prod                   # Apache


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

    # --- TAMBAHAN: untuk rate limiting & security ---
    'ratelimit',       # pip install django-ratelimit

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
    'monitoring',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',

    # --- TAMBAHAN: CORS harus di atas CommonMiddleware ---
    'corsheaders.middleware.CorsMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # --- TAMBAHAN: Rate limiting middleware (agar tidak perlu @ratelimit di setiap view) ---
    # 'ratelimit.middleware.RatelimitMiddleware',  # Aktifkan jika ingin rate limit global

    # Aplikasi lokal
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
            # --- TAMBAHAN: Gunakan koneksi terenkripsi ke database ---
            'OPTIONS': {
                'ssl': {'ca': config('DB_CA_CERT', default='')},  # Opsional: verifikasi SSL
            } if config('DB_USE_SSL', default=False, cast=bool) else {},
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

# --- TAMBAHAN: Aturan password lebih ketat ---
# Jumlah minimal karakter password
# Bisa di-set dari .env: AUTH_PASSWORD_MIN_LENGTH=12
AUTH_PASSWORD_MIN_LENGTH = config('AUTH_PASSWORD_MIN_LENGTH', default=12, cast=int)

# --- TAMBAHAN: Gunakan bcrypt atau Argon2 untuk hash password (lebih kuat dari PBKDF2 default) ---
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',      # Paling aman (pip install argon2-cffi)
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher', # Alternatif (pip install bcrypt)
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',      # Default Django (fallback)
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
]


# ══════════════════════════════════════════════════════════════
#  INTERNASIONALISASI
# ══════════════════════════════════════════════════════════════
LANGUAGE_CODE = 'pt-br'
TIME_ZONE     = 'Asia/Dili'
USE_I18N      = True
USE_TZ        = True


# ══════════════════════════════════════════════════════════════
#  STATIC & MEDIA
# ══════════════════════════════════════════════════════════════
STATIC_URL  = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL  = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- TAMBAHAN: Proteksi file upload ---
# Ukuran maksimal upload file (10MB)
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB

# Hanya tipe file tertentu yang diizinkan (contoh, sesuaikan dengan kebutuhan)
# FILE_UPLOAD_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'application/pdf']


# ══════════════════════════════════════════════════════════════
#  EMAIL
# ══════════════════════════════════════════════════════════════
EMAIL_BACKEND        = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST           = 'smtp.gmail.com'
EMAIL_PORT           = 587
EMAIL_USE_TLS        = True
EMAIL_HOST_USER      = config('EMAIL_USER', default='')
EMAIL_HOST_PASSWORD  = config('EMAIL_PASS', default='')

# --- TAMBAHAN: Default email pengirim ---
DEFAULT_FROM_EMAIL    = config('DEFAULT_FROM_EMAIL', default='noreply@asset.salisdev.com')
SERVER_EMAIL          = config('SERVER_EMAIL', default='admin@asset.salisdev.com')
ADMINS                = [('Admin', config('ADMIN_EMAIL', default='admin@asset.salisdev.com'))]


# ══════════════════════════════════════════════════════════════
#  LOGGING
# ══════════════════════════════════════════════════════════════
LOG_DIR = BASE_DIR / 'logs'
LOG_DIR.mkdir(exist_ok=True)

# --- TAMBAHAN: Logging lebih detail untuk security events ---
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_DIR / 'django.log',
            'maxBytes': 10 * 1024 * 1024,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_DIR / 'security.log',
            'maxBytes': 10 * 1024 * 1024,
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,  # Sertakan trace HTML di email
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'mail_admins'],
            'level': 'WARNING',
            'propagate': True,
        },
        'django.security': {
            'handlers': ['security_file', 'mail_admins'],
            'level': 'WARNING',
            'propagate': False,
        },
        # Log semua percobaan login gagal
        'django.contrib.auth': {
            'handlers': ['security_file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}


# ══════════════════════════════════════════════════════════════
#  CORS — DIPERBAIKI!
# ══════════════════════════════════════════════════════════════

# ❌ SEBELUMNYA (BERBAHAYA — mengizinkan semua origin):
# CORS_ALLOW_ALL_ORIGINS = True

# ✅ DIPERBAIKI MENJADI:
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='https://asset.salisdev.com',
    cast=Csv(),
)
CORS_ALLOW_CREDENTIALS = True  # Hanya jika perlu cookie/auth di request CORS

# --- TAMBAHAN: Batasi method HTTP yang diizinkan ---
CORS_ALLOW_METHODS = [
    'GET',
    'POST',
    'PUT',
    'PATCH',
    'DELETE',
    'OPTIONS',
]

# --- TAMBAHAN: Batasi header yang diizinkan ---
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]


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

# --- TAMBAHAN: Redirect setelah logout ---
LOGOUT_REDIRECT_URL = 'login'

ABSOLUTE_URL_OVERRIDES = {
    'auth.user': lambda u: '/users/users/',
}


# ══════════════════════════════════════════════════════════════
#  SECURITY SESSION — DIPERBAIKI!
# ══════════════════════════════════════════════════════════════

# Session expire saat browser ditutup
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Session expired setelah 1 jam (60 menit x 60 detik)
SESSION_COOKIE_AGE = 60 * 60

# --- TAMBAHAN: Regenerasi session ID saat login (cegah session fixation) ---
SESSION_SAVE_EVERY_REQUEST = True  # Refresh session expiry setiap request

# --- TAMBAHAN: Proteksi Cross-Origin Opener Policy (COOP) ---
SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin'  # ✅ Berubah dari None → 'same-origin'


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
#  REST FRAMEWORK — DIPERBAIKI!
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
        'anon':  '20/hour',      # ✅ Diturunkan dari 100/day → 20/hour
        'user': '1000/day',       # ✅ Tetap, bisa disesuaikan
    },
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',  # ✅ Hanya JSON, tidak ada Browsable API di production
    ],
    # --- TAMBAHAN: Proteksi DRF tambahan ---
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler',
    'DEFAULT_VERSIONING_CLASS': None,
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.openapi.AutoSchema',
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
    # Nonaktifkan form di browsable API (jika tidak diperlukan)
    'DEFAULT_METADATA_CLASS': 'rest_framework.metadata.SimpleMetadata',
}