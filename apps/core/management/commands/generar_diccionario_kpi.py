"""Genera docs/parte2/diccionario_kpi.md a partir del registro de KPI (así la documentación no se desactualiza)."""

from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.core import kpi
from apps.core.dashboard import AREAS

UNIDADES = {"pen": "S/", "pct": "%", "ratio": "índice", "dias": "días", "n": "cantidad"}
MEJOR = {"mayor": "más alto", "menor": "más bajo", "ninguna": "informativo"}


class Command(BaseCommand):
    help = "Escribe el diccionario de KPI en markdown."

    def handle(self, *args, **opciones):
        lineas = [
            "# Diccionario de KPI",
            "",
            "Documento **generado automáticamente** con `python manage.py generar_diccionario_kpi` desde el registro de KPI "
            "(`apps/*/kpis.py`). No se edita a mano: para cambiar una definición se cambia el código y se vuelve a generar.",
            "",
            "Semáforo: **ok** si se cumple el umbral de atención, **atención** entre ambos umbrales, **crítico** más allá del umbral crítico. "
            "Los umbrales pueden ajustarse en el administrador (Configuración de KPI) sin tocar el código.",
            "",
        ]
        for slug, area in sorted(AREAS.items(), key=lambda kv: kv[1].orden):
            definiciones = sorted(
                (d for d in kpi.REGISTRO.values() if d.area == slug),
                key=lambda d: kpi._orden(d.codigo),
            )
            if not definiciones:
                continue
            lineas += [
                f"## {area.titulo}",
                "",
                area.descripcion,
                "",
                "| Código | Indicador | Unidad | Mejor | Atención | Crítico | Frec. | Prior. |",
                "|---|---|---|---|---|---|---|---|",
            ]
            for d in definiciones:
                a = "—" if d.umbral_alerta is None else f"{d.umbral_alerta:g}"
                c = "—" if d.umbral_critico is None else f"{d.umbral_critico:g}"
                lineas.append(
                    f"| {d.codigo} | {d.nombre} | {UNIDADES[d.unidad]} | {MEJOR[d.direccion]} | {a} | {c} | {d.frecuencia} | {d.prioridad} |"
                )
            lineas.append("")
            for d in definiciones:
                lineas += [
                    f"### {d.codigo} · {d.nombre}",
                    "",
                    f"- **Fórmula:** {d.formula}",
                    f"- **Fuente:** {d.fuente}",
                ]
                if d.descripcion:
                    lineas.append(f"- **Lectura:** {d.descripcion}")
                lineas.append("")
        destino = Path(settings.BASE_DIR) / "docs" / "parte2" / "diccionario_kpi.md"
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text("\n".join(lineas), encoding="utf-8")
        self.stdout.write(self.style.SUCCESS(f"Escrito {destino}"))
