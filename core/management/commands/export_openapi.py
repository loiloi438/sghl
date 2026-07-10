import json
from pathlib import Path

from django.core.management.base import BaseCommand

from api.v1.router import api


class Command(BaseCommand):
    help = 'Exporte le schéma OpenAPI de /api/v1/ vers docs/openapi.json'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            default='docs/openapi.json',
            help='Chemin du fichier JSON (défaut: docs/openapi.json)',
        )

    def handle(self, *args, **options):
        out = Path(options['output'])
        out.parent.mkdir(parents=True, exist_ok=True)
        schema = api.get_openapi_schema()
        out.write_text(
            json.dumps(schema, indent=2, ensure_ascii=False),
            encoding='utf-8',
        )
        paths = len(schema.get('paths', {}))
        self.stdout.write(self.style.SUCCESS(f'OpenAPI exporté : {out} ({paths} chemins)'))
