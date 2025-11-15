import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ===========================
# BASIC SETTINGS
# ===========================
SECRET_KEY = 'django-insecure-gna55k_3_8v#&-x_0)_oaa!f1vgf0wu56zy)rmlwru))%jp(9f'
DEBUG = True
ALLOWED_HOSTS = ["127.0.0.1", "localhost", "192.168.43.122"]

# ===========================
# DATABASE CONFIGURATION (Supabase Pooler – Fixed Username)
# ===========================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres.optirptpfjpyddemxpsg',  # ← Pooler format: postgres.[project-ref]
        'PASSWORD': 'schoolsportsteammanagement',  # ← Your DB password (reset if needed)
        'HOST': 'aws-1-ap-southeast-1.pooler.supabase.com',  # ← Region-specific pooler host
        'PORT': '5432',  # Session mode for local dev
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

# ===========================
# DEFAULT AUTO FIELD
# ===========================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'