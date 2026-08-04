#!/bin/sh
set -e

echo "Waiting for database..."
python <<'PY'
import os
import time

engine = os.getenv("DJANGO_DB_ENGINE", "sqlite").lower()
if engine in ("sqlite", "sqlite3"):
    raise SystemExit(0)

import psycopg

host = os.getenv("POSTGRES_HOST", "db")
port = int(os.getenv("POSTGRES_PORT", "5432"))
dbname = os.getenv("POSTGRES_DB", "organeasy")
user = os.getenv("POSTGRES_USER", "organeasy")
password = os.getenv("POSTGRES_PASSWORD", "")

for attempt in range(30):
    try:
        with psycopg.connect(
            host=host,
            port=port,
            dbname=dbname,
            user=user,
            password=password,
            connect_timeout=3,
        ):
            print("Database is ready.")
            break
    except Exception as exc:  # noqa: BLE001
        print(f"Database not ready ({attempt + 1}/30): {exc}")
        time.sleep(2)
else:
    raise SystemExit("Database did not become ready in time.")
PY

python manage.py migrate --noinput
exec "$@"
