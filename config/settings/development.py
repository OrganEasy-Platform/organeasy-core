"""Settings de desenvolvimento local."""

import os

from .base import *  # noqa: F403

DEBUG = True

SECRET_KEY = SECRET_KEY or "django-insecure-dev-only-change-me-32chars"  # noqa: F405

# Alinhar signing key se SECRET_KEY foi ajustada após o import de base.
SIMPLE_JWT = {  # noqa: F405
    **SIMPLE_JWT,  # noqa: F405
    "SIGNING_KEY": os.getenv("JWT_SIGNING_KEY", "").strip() or SECRET_KEY,
}

if not ALLOWED_HOSTS:  # noqa: F405
    ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]", "testserver", "web"]

if not CORS_ALLOWED_ORIGINS:  # noqa: F405
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

# Docs abertas em local, salvo override explícito no .env.
if os.getenv("DJANGO_ENABLE_API_DOCS") is None:
    ENABLE_API_DOCS = True
