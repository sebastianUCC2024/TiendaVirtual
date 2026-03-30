from .base import *
import dj_database_url
from decouple import config

DEBUG = True

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL', default='sqlite:///db.sqlite3')
    )
}

CORS_ALLOW_ALL_ORIGINS = True

# Emails en consola durante desarrollo
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
