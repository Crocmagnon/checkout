"""
Django settings for checkout project.

Generated by 'django-admin startproject' using Django 3.1.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""
import os
from pathlib import Path

import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
from django.contrib import messages

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

env = environ.Env(
    DEBUG=(bool, False),
    SECRET_KEY=(str, "s#!83!8e$3s89m)r$1ghsgxbndf8=#^qt(_*o%xbq0j2t8#db5"),
    ADMINS=(list, []),
    MAILGUN_API_KEY=(str, ""),
    MAILGUN_SENDER_DOMAIN=(str, ""),
    HOSTS=(list, []),
    DB_BASE_DIR=(Path, BASE_DIR),
    TIME_ZONE=(str, "Europe/Paris"),
    LANGUAGE_CODE=(str, "fr-fr"),
)

env_file = os.getenv("ENV_FILE", None)

if env_file:
    environ.Env.read_env(env_file)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

admins = env("ADMINS")
if admins:
    ADMINS = [tuple(admin.split("|")) for admin in admins]

DEFAULT_FROM_EMAIL = "Checkout <checkout@mg.augendre.info>"
SERVER_EMAIL = "Checkout <checkout@mg.augendre.info>"
EMAIL_SUBJECT_PREFIX = "[Checkout] "
EMAIL_TIMEOUT = 30

ANYMAIL = {
    "MAILGUN_API_KEY": env("MAILGUN_API_KEY"),
    "MAILGUN_SENDER_DOMAIN": env("MAILGUN_SENDER_DOMAIN"),
    "MAILGUN_API_URL": "https://api.eu.mailgun.net/v3",
}
EMAIL_BACKEND = "anymail.backends.mailgun.EmailBackend"


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG")
ALLOWED_HOSTS = ["localhost"]  # Required for healthcheck
if DEBUG:
    ALLOWED_HOSTS.append("127.0.0.1")

ALLOWED_HOSTS.extend(env("HOSTS"))

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG


# Application definition

INSTALLED_APPS = [
    "whitenoise.runserver_nostatic",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "anymail",
    "django_cleanup.apps.CleanupConfig",
    "common",
    "purchase",
    "crispy_forms",
    "crispy_bootstrap5",
    "django_extensions",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.gzip.GZipMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "csp.middleware.CSPMiddleware",
]

ROOT_URLCONF = "checkout.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "checkout.wsgi.application"

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "cache",
    }
}

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DB_BASE_DIR = env("DB_BASE_DIR")
if not DB_BASE_DIR:
    # Protect against empty strings
    DB_BASE_DIR = BASE_DIR
else:
    DB_BASE_DIR = DB_BASE_DIR.resolve(strict=True)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": DB_BASE_DIR / "db.sqlite3",
    }
}

INTERNAL_IPS = [
    "127.0.0.1",
    "localhost",
]

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = env("LANGUAGE_CODE")

TIME_ZONE = env("TIME_ZONE")

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR.parent / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR.parent / "media"

AUTH_USER_MODEL = "common.User"

LOGIN_URL = "admin:login"

SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_HSTS_SECONDS = 63072000

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# CSP
CSP_DEFAULT_SRC = ("'none'",)
CSP_IMG_SRC = ("'self'", "data:")
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'")
CSP_CONNECT_SRC = ("'self'",)
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")
CSP_MANIFEST_SRC = ("'self'",)
CSP_FONT_SRC = ("'self'",)
CSP_BASE_URI = ("'none'",)
CSP_FORM_ACTION = ("'self'",)

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

MESSAGE_TAGS = {messages.ERROR: "danger"}
