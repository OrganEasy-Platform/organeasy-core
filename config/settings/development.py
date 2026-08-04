"""Settings de desenvolvimento local."""

from .base import *  # noqa: F403

DEBUG = True

SECRET_KEY = SECRET_KEY or "django-insecure-dev-only-change-me"  # noqa: F405

if not ALLOWED_HOSTS:  # noqa: F405
    ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]", "testserver", "web"]

if not CORS_ALLOWED_ORIGINS:  # noqa: F405
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
