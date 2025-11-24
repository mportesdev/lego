import os
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("LEGO_SECRET_KEY")

DEBUG = os.getenv("LEGO_DEBUG") in ("1", "true")

ALLOWED_HOSTS = os.getenv("LEGO_ALLOWED_HOSTS", "").split(",")
INTERNAL_IPS = ["127.0.0.1"]


# Application definition

INSTALLED_APPS = [
    "lego.apps.LegoAdminConfig",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "lego.apps.LegoConfig",
    "django_tasks",
    "django_tasks.backends.database",
    "debug_toolbar",
]

MIDDLEWARE = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "project.urls"

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
                "lego.context_processors.common_context",
            ],
        },
    },
]

WSGI_APPLICATION = "project.wsgi.application"


# Database

DATABASES = {
    "default": dj_database_url.config(
        conn_max_age=600,
        conn_health_checks=True,
    ),
}


# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Europe/Prague"

USE_I18N = False

USE_TZ = True


# Static files

STATIC_URL = "/static/"

STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}


# Background tasks

TASKS = {
    "default": {
        "BACKEND": "django_tasks.backends.database.DatabaseBackend",
    },
}


# Default primary key field type

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Logging

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "loggers": {
        "lego": {
            "level": "DEBUG",
            "handlers": ["console", "lego-logfile"],
        },
        "django": {
            "level": "INFO",
            "handlers": ["console", "mail_admins", "django-logfile"],
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG" if DEBUG else "INFO",
            "formatter": "brief",
        },
        "lego-logfile": {
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "lego.log",
            "level": "INFO",
            "formatter": "detailed",
        },
        "django-logfile": {
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "django.log",
            "level": "ERROR",
            "formatter": "detailed",
        },
        "mail_admins": {    # copied from django.utils.log.DEFAULT_LOGGING
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
    },
    "filters": {    # copied from django.utils.log.DEFAULT_LOGGING
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
    },
    "formatters": {
        "brief": {
            "format": "{levelname} | {message}",
            "style": "{",
        },
        "detailed": {
            "format": "{asctime} | {name} | {levelname} | {message}",
            "style": "{",
        },
    },
}


# Error reporting

ADMINS = [
    (os.getenv("LEGO_ADMIN_NAME"), os.getenv("LEGO_ADMIN_EMAIL")),
]

EMAIL_HOST = os.getenv("LEGO_EMAIL_HOST")
EMAIL_PORT = 587
EMAIL_HOST_USER = os.getenv("LEGO_EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("LEGO_EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = True

SERVER_EMAIL = os.getenv("LEGO_SERVER_EMAIL")
