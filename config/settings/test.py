"""Settings de teste / CI (sem secrets reais)."""

from .base import *  # noqa: F403

DEBUG = False

SECRET_KEY = "ci-test-secret-not-for-production-32b"

# base.py congela SIGNING_KEY no import; alinhar à SECRET_KEY de teste.
SIMPLE_JWT = {  # noqa: F405
    **SIMPLE_JWT,  # noqa: F405
    "SIGNING_KEY": SECRET_KEY,
}

ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]

CORS_ALLOWED_ORIGINS = []

# Unitários usam LocMem mesmo se REDIS_URL estiver presente no runner.
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "organeasy-core-test",
    }
}

# CI define POSTGRES_*; localmente, smoke de testes pode usar sqlite.
# Ver pytest.ini e .github/workflows/ci.yml.

ENABLE_API_DOCS = True
