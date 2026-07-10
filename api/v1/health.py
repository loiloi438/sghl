import os
from datetime import datetime, timezone
from pathlib import Path

from django.conf import settings
from django.core.mail import get_connection
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from ninja import Router

router = Router(tags=['Santé'])


@router.get('/sante/')
def health_check(request):
    checks = {}
    db_ok = True
    try:
        connection.ensure_connection()
        checks['database'] = 'connected'
    except Exception as exc:
        db_ok = False
        checks['database'] = f'error: {exc.__class__.__name__}'

    migrations_ok = True
    try:
        executor = MigrationExecutor(connection)
        plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
        checks['migrations'] = 'applied' if not plan else f'pending:{len(plan)}'
        if plan:
            migrations_ok = False
    except Exception:
        checks['migrations'] = 'unknown'
        migrations_ok = False

    media_ok = True
    media_root = Path(settings.MEDIA_ROOT)
    try:
        media_root.mkdir(parents=True, exist_ok=True)
        test_file = media_root / '.health_check'
        test_file.write_text('ok', encoding='utf-8')
        test_file.unlink(missing_ok=True)
        checks['media'] = 'writable'
    except Exception:
        media_ok = False
        checks['media'] = 'not_writable'

    email_ok = True
    try:
        conn = get_connection()
        conn.open()
        conn.close()
        checks['email'] = 'reachable'
    except Exception:
        email_ok = False
        checks['email'] = 'unreachable'

    all_ok = db_ok and migrations_ok and media_ok
    status = 'ok' if all_ok else 'degraded'
    return {
        'status': status,
        'service': 'SGHL API',
        'version': 'v1',
        'build': os.getenv('SGHL_BUILD', 'dev'),
        'database': checks.get('database', 'unknown'),
        'checks': checks,
        'timestamp': datetime.now(timezone.utc).isoformat(),
    }
