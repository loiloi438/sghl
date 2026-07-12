#!/bin/sh
set -e

echo "Attente de PostgreSQL…"
python - <<'PY'
import os, sys, time
from urllib.parse import unquote, urlparse

import psycopg2


def conn_params():
    url = os.getenv("DATABASE_URL", "").strip()
    if url:
        parsed = urlparse(url)
        return {
            "dbname": unquote(parsed.path.lstrip("/")),
            "user": unquote(parsed.username or ""),
            "password": unquote(parsed.password or ""),
            "host": parsed.hostname or "",
            "port": parsed.port or 5432,
        }
    return {
        "dbname": os.getenv("DB_NAME", "sghl"),
        "user": os.getenv("DB_USER", "sghl"),
        "password": os.getenv("DB_PASSWORD", "sghl"),
        "host": os.getenv("DB_HOST", "db"),
        "port": os.getenv("DB_PORT", "5432"),
    }


params = conn_params()
for _ in range(60):
    try:
        psycopg2.connect(**params).close()
        sys.exit(0)
    except Exception:
        time.sleep(2)
print("PostgreSQL indisponible", file=sys.stderr)
sys.exit(1)
PY

python manage.py migrate --noinput

if [ "${SGHL_SEED_ADMIN:-false}" = "true" ]; then
  echo "Seed administrateur (SGHL_SEED_ADMIN=true)…"
  python manage.py seed_admin
fi

if [ "${SGHL_SEED_DEMO:-false}" = "true" ]; then
  echo "Seed démo (SGHL_SEED_DEMO=true)…"
  python manage.py seed_demo
fi

if [ "${SGHL_TEST_SMTP:-false}" = "true" ]; then
  echo "Test SMTP au boot (SGHL_TEST_SMTP=true) — voir les logs Render…"
  python manage.py test_smtp --to="${SGHL_TEST_SMTP_TO:-mouangatresor673@gmail.com}" || echo "Échec test SMTP (voir trace ci-dessus)"
fi

PORT="${PORT:-8000}"
if [ "$1" = "gunicorn" ]; then
  shift
  exec gunicorn "$@" --bind "0.0.0.0:${PORT}"
fi

exec "$@"
