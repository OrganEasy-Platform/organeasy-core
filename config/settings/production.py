"""Settings de produção."""

import os

from .base import *  # noqa: F403

DEBUG = False

ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv("DJANGO_ALLOWED_HOSTS", "").split(",")
    if host.strip()
]

if not SECRET_KEY:  # noqa: F405
    raise ValueError("DJANGO_SECRET_KEY é obrigatória em produção.")

if not ALLOWED_HOSTS:
    raise ValueError("DJANGO_ALLOWED_HOSTS é obrigatória em produção.")

if DATABASES["default"]["ENGINE"].endswith("sqlite3"):  # noqa: F405
    raise ValueError("SQLite não é permitido em produção; use PostgreSQL.")
