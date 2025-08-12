import os
from pathlib import Path
from decouple import config, UndefinedValueError
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# -------------------------------------------------
# SECURITY SETTINGS
# -------------------------------------------------
SECRET_KEY = 'django-insecure-change-this-in-production-1234567890'
DEBUG = True
ALLOWED_HOSTS = ["*"]

# -------------------------------------------------
# DATABASE CONFIG
# -------------------------------------------------
try:
    DATABASE_URL = config('DATABASE_URL')
except UndefinedValueError:
    DATABASE_URL = ''

if DATABASE_URL.strip():
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# -------------------------------------------------
# STATIC & MEDIA FILES
# -------------------------------------------------
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# -------------------------------------------------
# MIDDLEWARE
# -------------------------------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# -------------------------------------------------
# INSTALLED APPS
# -------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'booking',
    'accounts',
]

# -------------------------------------------------
# DEFAULT PRIMARY KEY FIELD TYPE
# -------------------------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# -------------------------------------------------
# TIME ZONE CONFIGURATION
# -------------------------------------------------
TIME_ZONE = 'Asia/Kolkata'
USE_TZ = True

# -------------------------------------------------
# URLS / TEMPLATES / WSGI
# -------------------------------------------------
ROOT_URLCONF = 'tatkal_auto_booker.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # ✅ Now you can use /templates folder
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'tatkal_auto_booker.wsgi.application'

# -------------------------------------------------
# LOGIN / LOGOUT REDIRECTS
# -------------------------------------------------
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'

# -------------------------------------------------
# CELERY CONFIGURATION
# -------------------------------------------------
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'

# Celery Beat settings
CELERY_BEAT_SCHEDULE = {
    'update-scheduled-bookings-every-minute': {
        'task': 'booking.tasks.update_scheduled_bookings',
        'schedule': 60.0,  # every 60 seconds
    },
    'auto-delete-old-bookings-daily': {
        'task': 'booking.tasks.auto_delete_old_bookings',
        'schedule': 86400.0,  # every 24 hours
    },
    'cleanup-orphaned-files-weekly': {
        'task': 'booking.tasks.cleanup_orphaned_files',
        'schedule': 604800.0,  # every 7 days
    },
}

# Auto-deletion settings
AUTO_DELETE_RETENTION_DAYS = config('AUTO_DELETE_RETENTION_DAYS', default=30, cast=int)
AUTO_DELETE_ENABLED = config('AUTO_DELETE_ENABLED', default=True, cast=bool)
