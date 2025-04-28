import os
from pathlib import Path

import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("LEGO_SECRET_KEY")

DEBUG = os.getenv("LEGO_DEBUG", "False") in ("1", "True", "true")

ALLOWED_HOSTS = os.getenv("LEGO_ALLOWED_HOSTS", "").split(",")


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
]

MIDDLEWARE = [
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
            "level": "ERROR",
            "handlers": ["django-logfile"],
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "WARNING",
            "formatter": "brief",
        },
        "lego-logfile": {
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "lego.log",
            "level": "DEBUG" if DEBUG else "INFO",
            "formatter": "detailed",
        },
        "django-logfile": {
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "django.log",
            "level": "ERROR",
            "formatter": "detailed",
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
