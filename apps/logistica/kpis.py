"""KPI de Logística y pagos (L1 a L18 de docs/parte1/06_propuesta_kpi.md).

Convenciones:
- Los KPI de tiempos y porcentajes miden una ventana de 90 días hasta la fecha de corte.
- Los KPI de "stock" (cuentas por pagar, órdenes sin facturar...) reflejan el último estado cargado.
- Importes en soles con el tipo de cambio guardado en cada documento.
"""

from collections import defaultdict
from datetime import timedelta
from decimal import Decimal

from django.db.models import Avg, F, Sum

from apps.core.kpi import Contexto, Valor, kpi
from apps.core.services import porcentaje

from .models import Comprobante, Orden, Requerimiento

AREA = "logistica"
VENTANA_DIAS = 90
TOLERANCIA_DIF = Decimal("1.00")  # soles de diferencia aceptados por redondeo


def _filtrar(qs, ctx, cc="centro_costo"):
    if ctx.empresa:
        qs = qs.filter(empresa=ctx.empresa)
    if ctx.proyecto:
        qs = qs.filter(**{cc: ctx.proyecto})
    return qs


def requerimientos(ctx, ventana=True):
    qs = _filtrar(Requerimiento.objects.filter(fecha_creacion__lte=ctx.corte), ctx)
    if ventana:
        qs = qs.filter(fecha_creacion__gt=ctx.corte - timedelta(days=VENTANA_DIAS))
    return qs


def ordenes(ctx, ventana=True):
    qs = _filtrar(Orden.objects.filter(fecha_emision__lte=ctx.corte), ctx)
    if ventana:
        qs = qs.filter(fecha_emision__gt=ctx.corte - timedelta(days=VENTANA_DIAS))
    return qs


def comprobantes(ctx):
    return _filtrar(Comprobante.objects.filter(fecha_doc__lte=ctx.corte), ctx)


def por_pagar(ctx):
    """Comprobantes no pagados a la fecha de corte (pagados después del corte cuentan como pendientes)."""
    return comprobantes(ctx).exclude(
        estado_pago="PAGADO", fecha_pago_real__lte=ctx.corte
    )


def _f(x):
    return float(x or 0)


@kpi(
    codigo="L1",
    area="logistica",
    nombre="Compras emitidas en el mes",
    unidad="pen",
    direccion="ninguna",
    frecuencia="S",
    formula="Suma del total de órdenes no rechazadas emitidas en el mes del corte",
    fuente="Orden.total_pen",
)
def compras_mes(ctx: Contexto) -> Valor:
    qs = (
        ordenes(ctx, ventana=False)
        .filter(fecha_emision__gte=ctx.mes)
        .exclude(estado="RECHAZADA")
    )
    return Valor(_f(qs.aggregate(s=Sum("total_pen"))["s"]), f"{qs.count()} órdenes")


@kpi(
    codigo="L2",
    area=AREA,
    nombre="RQ rechazados",
    unidad="pct",
    direccion="menor",
    umbral_alerta=20,
    umbral_critico=30,
    formula="RQ rechazados / RQ creados (90 días)",
    fuente="Requerimiento.estado",
)
def rq_rechazados(ctx: Contexto) -> Valor:
    qs = requerimientos(ctx)
    return Valor(
        porcentaje(qs.filter(estado="RECHAZADA").count(), qs.count()),
        f"{qs.count()} RQ en 90 días",
    )


@kpi(
    codigo="L3",
    area=AREA,
    nombre="RQ de emergencia y regularización",
    unidad="pct",
    direccion="menor",
    umbral_alerta=40,
    umbral_critico=60,
    resumen=True,
    formula="(Emergencia + regularización) / RQ creados (90 días)",
    fuente="Requerimiento.tipo",
    descripcion="Indica qué parte de las compras no se planifica. En el archivo de octubre-noviembre llegaba al 85 %.",
)
def rq_emergencia(ctx: Contexto) -> Valor:
    qs = requerimientos(ctx)
    return Valor(
        porcentaje(
            qs.filter(tipo__in=["EMERGENCIA", "REGULARIZACION"]).count(), qs.count()
        )
    )


@kpi(
    codigo="L4",
    area=AREA,
    nombre="Órdenes sin RQ (regularización)",
    unidad="pct",
    direccion="menor",
    umbral_alerta=10,
    umbral_critico=20,
    formula="Órdenes de regularización / órdenes emitidas (90 días)",
    fuente="Orden.es_regularizacion",
)
def ordenes_sin_rq(ctx: Contexto) -> Valor:
    qs = ordenes(ctx)
    return Valor(porcentaje(qs.filter(es_regularizacion=True).count(), qs.count()))


@kpi(
    codigo="L5",
    area=AREA,
    nombre="Tiempo de aprobación de RQ",
    unidad="dias",
    direccion="menor",
    umbral_alerta=2,
    umbral_critico=4,
    frecuencia="S",
    formula="Promedio de (fecha de aprobación - fecha de creación)",
    fuente="Requerimiento",
)
def tiempo_aprobacion_rq(ctx: Contexto) -> Valor:
    qs = (
        requerimientos(ctx)
        .exclude(fecha_aprobacion=None)
        .annotate(d=F("fecha_aprobacion") - F("fecha_creacion"))
    )
    dias = [x.d.days for x in qs]
    return Valor(sum(dias) / len(dias) if dias else None, f"{len(dias)} RQ aprobados")


@kpi(
    codigo="L6",
    area=AREA,
    nombre="Tiempo RQ aprobado a orden emitida",
    unidad="dias",
    direccion="menor",
    umbral_alerta=2,
    umbral_critico=4,
    frecuencia="S",
    formula="Promedio de (fecha de emisión - aprobación del RQ)",
    fuente="Orden",
)
def tiempo_rq_orden(ctx: Contexto) -> Valor:
    qs = (
        ordenes(ctx)
        .exclude(fecha_aprobacion_rq=None)
        .annotate(d=F("fecha_emision") - F("fecha_aprobacion_rq"))
    )
    dias = [x.d.days for x in qs]
    return Valor(sum(dias) / len(dias) if dias else None, f"{len(dias)} órdenes")


@kpi(
    codigo="L8",
    area=AREA,
    nombre="Órdenes aprobadas sin facturar",
    unidad="n",
    direccion="ninguna",
    frecuencia="S",
    formula="Cantidad de órdenes en estado 'Aprobada (sin facturar)'",
    fuente="Orden.estado",
)
def ordenes_sin_facturar(ctx: Contexto) -> Valor:
    qs = ordenes(ctx, ventana=False).filter(estado="SIN_FACTURAR")
    return Valor(
        qs.count(), f"Importe S/ {_f(qs.aggregate(s=Sum('total_pen'))['s']):,.0f}"
    )


@kpi(
    codigo="L9",
    area=AREA,
    nombre="Órdenes pendientes de entrega",
    unidad="n",
    direccion="ninguna",
    frecuencia="S",
    formula="Órdenes aprobadas con entrega pendiente o parcial",
    fuente="Orden.estado_entrega",
)
def ordenes_sin_entrega(ctx: Contexto) -> Valor:
    qs = (
        ordenes(ctx, ventana=False)
        .exclude(estado__in=["RECHAZADA", "POR_APROBAR"])
        .exclude(estado_entrega="ENTREGADO")
    )
    return Valor(
        qs.count(), f"Importe S/ {_f(qs.aggregate(s=Sum('total_pen'))['s']):,.0f}"
    )


@kpi(
    codigo="L10",
    area=AREA,
    nombre="Cuentas por pagar",
    unidad="pen",
    direccion="ninguna",
    resumen=True,
    frecuencia="S",
    formula="Suma de comprobantes no pagados",
    fuente="Comprobante.total_pen",
)
def cuentas_por_pagar(ctx: Contexto) -> Valor:
    qs = por_pagar(ctx)
    return Valor(
        _f(qs.aggregate(s=Sum("total_pen"))["s"]), f"{qs.count()} comprobantes"
    )


@kpi(
    codigo="L11",
    area=AREA,
    nombre="Deuda vencida",
    unidad="pct",
    direccion="menor",
    umbral_alerta=20,
    umbral_critico=40,
    resumen=True,
    frecuencia="S",
    formula="Importe vencido no pagado / importe total por pagar",
    fuente="Comprobante.fecha_venc",
    descripcion="Vencido = fecha de vencimiento anterior a la fecha de corte.",
)
def deuda_vencida(ctx: Contexto) -> Valor:
    qs = por_pagar(ctx)
    vencido = qs.filter(fecha_venc__lt=ctx.corte)
    total, venc = _f(qs.aggregate(s=Sum("total_pen"))["s"]), _f(
        vencido.aggregate(s=Sum("total_pen"))["s"]
    )
    return Valor(
        porcentaje(venc, total),
        f"{vencido.count()} de {qs.count()} comprobantes vencidos (S/ {venc:,.0f})",
    )


@kpi(
    codigo="L12",
    area=AREA,
    nombre="Deuda vencida de más de 30 días",
    unidad="pen",
    direccion="menor",
    umbral_alerta=100_000,
    umbral_critico=500_000,
    frecuencia="S",
    formula="Comprobantes no pagados con más de 30 días de vencidos",
    fuente="Comprobante.fecha_venc",
)
def deuda_mas_30(ctx: Contexto) -> Valor:
    qs = por_pagar(ctx).filter(fecha_venc__lt=ctx.corte - timedelta(days=30))
    return Valor(
        _f(qs.aggregate(s=Sum("total_pen"))["s"]), f"{qs.count()} comprobantes"
    )


@kpi(
    codigo="L13",
    area=AREA,
    nombre="Pagos programados a 30 días",
    unidad="pen",
    direccion="ninguna",
    resumen=True,
    frecuencia="S",
    formula="Comprobantes programados con fecha de pago entre hoy y +30 días",
    fuente="Comprobante.fecha_programada_pago",
)
def pagos_programados(ctx: Contexto) -> Valor:
    qs = por_pagar(ctx).filter(
        fecha_programada_pago__gte=ctx.corte,
        fecha_programada_pago__lte=ctx.corte + timedelta(days=30),
    )
    return Valor(_f(qs.aggregate(s=Sum("total_pen"))["s"]), f"{qs.count()} pagos")


@kpi(
    codigo="L14",
    area=AREA,
    nombre="Órdenes con diferencia vs facturado",
    unidad="pct",
    direccion="menor",
    umbral_alerta=10,
    umbral_critico=20,
    prioridad="A",
    formula="Órdenes cuyo total facturado difiere más de 1 sol del total de la orden / órdenes con comprobante",
    fuente="Orden.total, Comprobante.total",
    descripcion="Incluye anticipos y facturas parciales: revisar caso a caso.",
)
def dif_orden_factura(ctx: Contexto) -> Valor:
    suma = defaultdict(Decimal)
    for nro, total in (
        comprobantes(ctx).exclude(nro_orden="").values_list("nro_orden", "total")
    ):
        suma[nro] += total
    ords = (
        ordenes(ctx, ventana=False)
        .filter(nro__in=suma.keys())
        .exclude(estado="RECHAZADA")
    )
    con_dif = sum(1 for o in ords if abs(o.total - suma[o.nro]) > TOLERANCIA_DIF)
    return Valor(
        porcentaje(con_dif, ords.count()), f"{con_dif} de {ords.count()} órdenes"
    )


@kpi(
    codigo="L15",
    area=AREA,
    nombre="Comprobantes con diferencia Logística vs Contabilidad",
    unidad="pct",
    direccion="menor",
    umbral_alerta=5,
    umbral_critico=10,
    formula="Comprobantes con |total Contabilidad - total Logística| > 1 sol / comprobantes con ambos importes",
    fuente="Comprobante.total, Comprobante.total_logistica",
)
def dif_logistica_contabilidad(ctx: Contexto) -> Valor:
    qs = comprobantes(ctx).exclude(total_logistica=None)
    con_dif = sum(1 for c in qs if abs(c.total - c.total_logistica) > TOLERANCIA_DIF)
    return Valor(
        porcentaje(con_dif, qs.count()), f"{con_dif} de {qs.count()} comprobantes"
    )


@kpi(
    codigo="L16",
    area=AREA,
    nombre="Concentración en 10 proveedores",
    unidad="pct",
    direccion="menor",
    umbral_alerta=60,
    umbral_critico=80,
    prioridad="B",
    formula="Compras de los 10 mayores proveedores / compras totales (90 días)",
    fuente="Orden.proveedor",
)
def concentracion_proveedores(ctx: Contexto) -> Valor:
    filas = (
        ordenes(ctx)
        .exclude(estado="RECHAZADA")
        .values("proveedor")
        .annotate(t=Sum("total_pen"))
        .order_by("-t")
    )
    totales = [_f(f["t"]) for f in filas]
    return Valor(
        porcentaje(sum(totales[:10]), sum(totales)), f"{len(totales)} proveedores"
    )


@kpi(
    codigo="L17",
    area=AREA,
    nombre="Pagos pendientes por detracción o retención",
    unidad="pen",
    direccion="ninguna",
    prioridad="B",
    formula="Comprobantes en estado 'Por detracción/retención'",
    fuente="Comprobante.estado_pago",
)
def por_detraccion(ctx: Contexto) -> Valor:
    qs = comprobantes(ctx).filter(estado_pago="POR_DETRACCION")
    return Valor(
        _f(qs.aggregate(s=Sum("total_pen"))["s"]), f"{qs.count()} comprobantes"
    )


@kpi(
    codigo="L18",
    area=AREA,
    nombre="Comprobantes por validar",
    unidad="n",
    direccion="menor",
    umbral_alerta=15,
    umbral_critico=30,
    frecuencia="S",
    formula="Comprobantes pendientes de conformidad o en revisión",
    fuente="Comprobante.estado_pago",
)
def por_validar(ctx: Contexto) -> Valor:
    return Valor(
        comprobantes(ctx)
        .filter(estado_pago__in=["PEND_CONFORMIDAD", "EN_REVISION"])
        .count()
    )


@kpi(
    codigo="Q4",
    area="calidad",
    nombre="RQ con precio estimado",
    unidad="pct",
    direccion="mayor",
    umbral_alerta=70,
    umbral_critico=40,
    formula="Ítems de RQ con precio / ítems de RQ (90 días)",
    fuente="Requerimiento.n_items_con_precio",
    descripcion="Sin precio en el RQ no se puede medir ahorro (L20). En el archivo actual solo el 19 % tenía precio.",
)
def rq_con_precio(ctx: Contexto) -> Valor:
    s = requerimientos(ctx).aggregate(i=Sum("n_items"), p=Sum("n_items_con_precio"))
    return Valor(porcentaje(s["p"] or 0, s["i"] or 0))
