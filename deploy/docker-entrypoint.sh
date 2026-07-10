#!/bin/sh
set -e

echo "Attente de PostgreSQL…"
python - <<'PY'
import os, sys, time
import psycopg2
host = os.getenv("DB_HOST", "db")
for i in range(30):
    try:
        psycopg2.connect(
            dbname=os.getenv("DB_NAME", "sghl"),
            user=os.getenv("DB_USER", "sghl"),
            password=os.getenv("DB_PASSWORD", "sghl"),
            host=host,
            port=os.getenv("DB_PORT", "5432"),
        ).close()
        sys.exit(0)
    except Exception:
        time.sleep(2)
print("PostgreSQL indisponible", file=sys.stderr)
sys.exit(1)
PY

python manage.py migrate --noinput
python manage.py seed_admin 2>/dev/null || true
python manage.py seed_demo 2>/dev/null || true

exec "$@"
