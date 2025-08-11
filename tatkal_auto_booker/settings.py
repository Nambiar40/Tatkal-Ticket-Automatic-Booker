import os
from pathlib import Path
from decouple import config
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_URL = config('DATABASE_URL', default='')

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
