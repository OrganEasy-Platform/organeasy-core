"""Settings de desenvolvimento local."""

from .base import *  # noqa: F403

DEBUG = True

SECRET_KEY = SECRET_KEY or "django-insecure-dev-only-change-me"  # noqa: F405

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]", "testserver"]
