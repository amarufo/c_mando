"""Guarda el valor de todos los KPI en una fecha de corte (y en los cierres de meses anteriores) para ver tendencias.

Pensado para programarse (cron / Railway cron job) después de cada carga de datos:
    python manage.py calcular_kpis --corte 2026-11-12 --historial 6
"""

from datetime import date, datetime, timedelta

from django.core.management.base import BaseCommand

from apps.core import kpi
from apps.core.models import KPISnapshot
from apps.core.services import primer_dia


class Command(BaseCommand):
    help = "Calcula y guarda los KPI (alcance global) para la fecha de corte y los cierres mensuales anteriores."

    def add_arguments(self, parser):
        parser.add_argument("--corte", help="AAAA-MM-DD (por defecto, hoy)")
        parser.add_argument(
            "--historial",
            type=int,
            default=0,
            help="Cantidad de cierres mensuales anteriores a recalcular",
        )

    def handle(self, *args, corte=None, historial=0, **opciones):
        corte = datetime.strptime(corte, "%Y-%m-%d").date() if corte else date.today()
        fechas, mes = [corte], primer_dia(corte)
        for _ in range(historial):
            mes_anterior_fin = mes - timedelta(days=1)  # último día del mes previo
            fechas.append(mes_anterior_fin)
            mes = primer_dia(mes_anterior_fin)
        configs = kpi._configuraciones()
        n = 0
        for f in sorted(fechas):
            ctx = kpi.Contexto(corte=f)
            for codigo in kpi.REGISTRO:
                r = kpi.calcular(codigo, ctx, configs)
                KPISnapshot.objects.update_or_create(
                    codigo=codigo,
                    fecha_corte=f,
                    empresa=None,
                    centro_costo=None,
                    defaults={"valor": r.valor, "estado": r.estado},
                )
                n += 1
        self.stdout.write(
            self.style.SUCCESS(
                f"{n} valores de KPI guardados para {len(fechas)} fechas de corte."
            )
        )
