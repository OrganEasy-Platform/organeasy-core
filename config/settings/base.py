"""Settings base compartilhadas entre ambientes."""

import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "")

DEBUG = False

ALLOWED_HOSTS: list[str] = [
    host.strip()
    for host in os.getenv("DJANGO_ALLOWED_HOSTS", "").split(",")
    if host.strip()
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "drf_spectacular",
    "core.apps.CoreConfig",
    "users",
    "organizations",
]

AUTH_USER_MODEL = "users.User"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


def _database_config() -> dict:
    """PostgreSQL via env; SQLite só quando DJANGO_DB_ENGINE=sqlite (smoke local)."""
    # Compose/CI definem postgresql; sqlite fica para smoke local sem containers.
    engine = os.getenv("DJANGO_DB_ENGINE", "sqlite").lower()
    if engine in ("sqlite", "sqlite3"):
        return {
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": BASE_DIR / "db.sqlite3",
            }
        }
    return {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("POSTGRES_DB", "organeasy"),
            "USER": os.getenv("POSTGRES_USER", "organeasy"),
            "PASSWORD": os.getenv("POSTGRES_PASSWORD", ""),
            "HOST": os.getenv("POSTGRES_HOST", "localhost"),
            "PORT": os.getenv("POSTGRES_PORT", "5432"),
            "CONN_MAX_AGE": int(os.getenv("POSTGRES_CONN_MAX_AGE", "60")),
        }
    }


DATABASES = _database_config()

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

LANGUAGE_CODE = "pt-br"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

STATIC_URL = "static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "core.authentication.SessionAuthentication401",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "EXCEPTION_HANDLER": "core.exceptions.unified_exception_handler",
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "OrganEasy Core API",
    "DESCRIPTION": "API de identidade do OrganEasy (usuários, organizações, autenticação).",
    "VERSION": "0.1.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

# SimpleJWT — claims e lifetimes via env (ADR 0003 / Fase 3).
_JWT_ACCESS_SECONDS = int(os.getenv("JWT_ACCESS_LIFETIME_SECONDS", "900"))
_JWT_REFRESH_SECONDS = int(os.getenv("JWT_REFRESH_LIFETIME_SECONDS", "604800"))
_JWT_SIGNING_KEY = os.getenv("JWT_SIGNING_KEY", "").strip() or SECRET_KEY
_JWT_ISSUER = os.getenv("JWT_ISSUER", "organeasy-auth").strip() or "organeasy-auth"
_JWT_AUDIENCE = os.getenv("JWT_AUDIENCE", "organeasy-services").strip() or "organeasy-services"

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(seconds=_JWT_ACCESS_SECONDS),
    "REFRESH_TOKEN_LIFETIME": timedelta(seconds=_JWT_REFRESH_SECONDS),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": _JWT_SIGNING_KEY,
    "ISSUER": _JWT_ISSUER,
    "AUDIENCE": _JWT_AUDIENCE,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "sub",
    "TOKEN_TYPE_CLAIM": "token_type",
    "JTI_CLAIM": "jti",
    "AUTH_TOKEN_CLASSES": ("core.tokens.OrganEasyAccessToken",),
}

# Schema/Swagger: desligado por padrão; development/test ligam. Produção exige env explícito.
ENABLE_API_DOCS = os.getenv("DJANGO_ENABLE_API_DOCS", "false").strip().lower() in (
    "1",
    "true",
    "yes",
    "on",
)

# CORS: origens explícitas via env (nunca CORS_ALLOW_ALL_ORIGINS em produção).
CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")
    if origin.strip()
]
CORS_ALLOW_CREDENTIALS = True

REDIS_URL = os.getenv("REDIS_URL", "").strip()
if REDIS_URL:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": REDIS_URL,
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "organeasy-core-local",
        }
    }
