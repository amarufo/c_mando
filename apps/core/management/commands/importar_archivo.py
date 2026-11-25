"""Carga un archivo limpio desde la terminal (misma validación que la pantalla y la API).

python manage.py importar_archivo proyectos_gastos ruta/archivo.csv [--validar]
"""

from django.core.management.base import BaseCommand, CommandError

from apps.core import importers


class Command(BaseCommand):
    help = "Valida y carga un archivo CSV/Excel en una de las tablas registradas."

    def add_arguments(self, parser):
        parser.add_argument("tabla")
        parser.add_argument("archivo")
        parser.add_argument(
            "--validar", action="store_true", help="Solo validar, no guardar"
        )

    def handle(self, *args, tabla, archivo, validar, **opciones):
        disponibles = importers.descubrir()
        if tabla not in disponibles:
            raise CommandError(
                f"Tabla desconocida. Disponibles: {', '.join(sorted(disponibles))}"
            )
        carga = importers.procesar(
            disponibles[tabla],
            importers.leer_archivo(archivo),
            nombre_archivo=archivo,
            guardar=not validar,
        )
        self.stdout.write(
            f"{carga.get_estado_display()}: {carga.filas_leidas} filas, {carga.filas_ok} válidas, {carga.filas_error} con error"
        )
        for e in carga.errores[:30]:
            self.stdout.write(f"  fila {e['fila']} [{e['columna']}]: {e['error']}")
        if carga.estado == "RECHAZADA":
            raise CommandError(
                "Archivo rechazado: corrija los errores y vuelva a cargarlo."
            )
