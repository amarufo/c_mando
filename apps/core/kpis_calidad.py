"""KPI transversales de calidad de datos (Q1 y Q2). Q3 a Q5 viven en cada área porque dependen de sus tablas."""

from datetime import timedelta

from django.utils import timezone

from .kpi import Contexto, Valor, kpi
from .models import CargaArchivo
from .services import porcentaje


@kpi(
    codigo="Q1",
    area="calidad",
    nombre="Días desde la última carga",
    unidad="dias",
    direccion="menor",
    umbral_alerta=7,
    umbral_critico=14,
    resumen=True,
    frecuencia="S",
    formula="Días entre hoy y la carga aceptada más reciente",
    fuente="CargaArchivo",
    descripcion="Si nadie carga datos, el cuadro de mando muestra información vieja sin avisar.",
)
def dias_desde_carga(ctx: Contexto) -> Valor:
    ultima = CargaArchivo.objects.filter(estado="OK").order_by("-fecha").first()
    if not ultima:
        return Valor(None, "Aún no hay cargas registradas")
    return Valor(
        (timezone.now() - ultima.fecha).total_seconds() / 86400,
        f"Última carga: {ultima.tabla} ({timezone.localtime(ultima.fecha):%d/%m/%Y})",
    )


@kpi(
    codigo="Q2",
    area="calidad",
    nombre="Cargas rechazadas (30 días)",
    unidad="pct",
    direccion="menor",
    umbral_alerta=10,
    umbral_critico=25,
    formula="Cargas rechazadas por errores de validación / cargas intentadas",
    fuente="CargaArchivo.estado",
)
def cargas_rechazadas(ctx: Contexto) -> Valor:
    qs = CargaArchivo.objects.filter(
        fecha__gte=timezone.now() - timedelta(days=30)
    ).exclude(estado="SIMULACION")
    return Valor(
        porcentaje(qs.filter(estado="RECHAZADA").count(), qs.count()),
        f"{qs.count()} cargas en 30 días",
    )
