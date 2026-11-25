"""Escribe una plantilla CSV (encabezados + fila de ejemplo) por cada tabla de carga en exports/plantillas/."""

from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.core import importers


class Command(BaseCommand):
    help = (
        "Genera las plantillas de los archivos limpios para entregarlas a cada oficina."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--destino", default=str(Path(settings.BASE_DIR) / "exports" / "plantillas")
        )

    def handle(self, *args, destino, **opciones):
        carpeta = Path(destino)
        carpeta.mkdir(parents=True, exist_ok=True)
        for slug, imp in sorted(importers.descubrir().items()):
            importers.plantilla(imp).to_csv(
                carpeta / f"plantilla_{slug}.csv", index=False, encoding="utf-8-sig"
            )
        self.stdout.write(
            self.style.SUCCESS(f"{len(importers.IMPORTADORES)} plantillas en {carpeta}")
        )
