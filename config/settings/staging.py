"""Settings de homologação."""

import os

from .base import *  # noqa: F403

DEBUG = False

ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv("DJANGO_ALLOWED_HOSTS", "").split(",")
    if host.strip()
]

if not SECRET_KEY:  # noqa: F405
    raise ValueError("DJANGO_SECRET_KEY é obrigatória em staging.")
