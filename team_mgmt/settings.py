import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# ===========================
# BASIC SETTINGS
# ===========================
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-gna55k_3_8v#&-x_0)_oaa!f1vgf0wu56zy)rmlwru))%jp(9f')
DEBUG = os.getenv('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', '127.0.0.1,localhost,192.168.43.122').split(',')

# ===========================
# DATABASE CONFIGURATION (Supabase Pooler)
# ===========================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'postgres'),
        'USER': os.getenv('DB_USER', 'postgres.optirptpfjpyddemxpsg'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'schoolsportsteammanagement'),
        'HOST': os.getenv('DB_HOST', 'aws-1-ap-southeast-1.pooler.supabase.com'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'OPTIONS': {
            'sslmode': 'require',
        },
    }
}

# ===========================
# APPLICATIONS
# ===========================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'team_mgmt',
    'coach',
]

# ===========================
# MIDDLEWARE
# ===========================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add this for static files in production
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ===========================
# URL & WSGI
# ===========================
ROOT_URLCONF = 'team_mgmt.urls'
WSGI_APPLICATION = 'team_mgmt.wsgi.application'

# ===========================
# TEMPLATES
# ===========================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "coach" / "templates"],
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

# ===========================
# PASSWORD VALIDATION
# ===========================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ===========================
# INTERNATIONALIZATION
# ===========================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ===========================
# STATIC FILES
# ===========================
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "coach" / "static",
]
STATIC_ROOT = BASE_DIR / "staticfiles"

# WhiteNoise configuration for serving static files in production
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ===========================
# DEFAULT AUTO FIELD
# ===========================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ===========================
# CSRF TRUSTED ORIGINS (for production)
# ===========================
CSRF_TRUSTED_ORIGINS = os.getenv('DJANGO_CSRF_TRUSTED_ORIGINS', 'http://127.0.0.1:8000,http://localhost:8000').split(',')