from pathlib import Path
import os
import environ

# Initialize environment variables
env = environ.Env(
    DEBUG=(bool, False) 
)

BASE_DIR = Path(__file__).resolve().parent.parent

# Security
# Load SECRET_KEY from environment variable
SECRET_KEY = env('SECRET_KEY') 
DEBUG = env('DEBUG')
# Load ALLOWED_HOSTS from environment variable list
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[]) 

# Installed apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'library',
    'widget_tweaks'
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # WhiteNoise must be placed immediately after SecurityMiddleware
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# URLs & WSGI
ROOT_URLCONF = 'library_project.urls'
WSGI_APPLICATION = 'library_project.wsgi.application'

# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'library' / 'templates'],
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

# Database
# Use DATABASE_URL for PostgreSQL in production, default to SQLite locally
DATABASES = {
    'default': env.db_url(
        'DATABASE_URL',
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}'
    )
}

# Password validation (disabled for dev)
AUTH_PASSWORD_VALIDATORS = []

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Dhaka'
USE_I18N = True
USE_TZ = True

# Static files setup
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'library_project/static'), 
]
# Static files collector directory for WhiteNoise
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# WhiteNoise Storage Configuration for Production
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Media files setup
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Authentication redirects
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'

# Default primary key
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'




