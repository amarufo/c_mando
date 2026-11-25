"""KPI de Recursos Humanos (H1 a H11 de docs/parte1/06_propuesta_kpi.md).

Supuestos de asistencia (ajustables en settings.CUADRO_MANDO): entrada 08:00 con 10 minutos
de tolerancia; la primera marca del día es la entrada. Los KPI de asistencia usan los
últimos 15 días hasta el corte, como el archivo de marcaciones actual.
"""

from datetime import datetime, time, timedelta

from django.conf import settings
from django.db.models import Q, Sum
from django.utils import timezone

from apps.core.kpi import Contexto, Valor, kpi
from apps.core.services import porcentaje, primer_dia
from apps.proyectos.services import valorizacion_real_periodo

from .models import CostoProyectoMes, Marcacion, Obligacion, Persona, PlanillaMes

AREA = "rrhh"
VENTANA_ASISTENCIA = 15


def personas_activas(ctx: Contexto):
    """Personas con contrato vigente a la fecha de corte, según empresa y centro de costo del alcance."""
    qs = Persona.objects.filter(fecha_ingreso__lte=ctx.corte).filter(
        Q(fecha_cese__isnull=True) | Q(fecha_cese__gt=ctx.corte)
    )
    if ctx.empresa:
        qs = qs.filter(empresa=ctx.empresa)
    if ctx.proyecto:
        qs = qs.filter(centro_costo=ctx.proyecto)
    return qs


def costos_periodo(ctx: Contexto):
    """Costos del último mes con datos hasta el mes del corte. Devuelve (queryset, periodo)."""
    base = CostoProyectoMes.objects.filter(periodo__lte=ctx.mes)
    if ctx.empresa:
        base = base.filter(empresa=ctx.empresa)
    if ctx.proyecto:
        base = base.filter(centro_costo=ctx.proyecto)
    ultimo = base.order_by("-periodo").values_list("periodo", flat=True).first()
    return (base.filter(periodo=ultimo), ultimo) if ultimo else (base.none(), None)


def _f(x):
    return float(x or 0)


def tardanzas(ctx: Contexto) -> tuple[int, int]:
    """(días-persona con tardanza, días-persona con marca) en los últimos 15 días."""
    desde = ctx.corte - timedelta(days=VENTANA_ASISTENCIA)
    inicio = timezone.make_aware(datetime.combine(desde, time.min))
    fin = timezone.make_aware(datetime.combine(ctx.corte, time.max))
    marcas = Marcacion.objects.filter(fecha_hora__range=(inicio, fin)).exclude(
        persona=None
    )
    if ctx.empresa:
        marcas = marcas.filter(persona__empresa=ctx.empresa)
    if ctx.proyecto:
        marcas = marcas.filter(persona__centro_costo=ctx.proyecto)
    primera = {}
    for persona_id, fh in marcas.values_list("persona_id", "fecha_hora"):
        local = timezone.localtime(fh)
        clave = (persona_id, local.date())
        if clave not in primera or local < primera[clave]:
            primera[clave] = local
    h, m = map(int, settings.CUADRO_MANDO["HORA_ENTRADA"].split(":"))
    limite = time(h, m)
    tol = timedelta(minutes=settings.CUADRO_MANDO["TOLERANCIA_MINUTOS"])
    tarde = sum(
        1
        for (_, d), t in primera.items()
        if t > timezone.make_aware(datetime.combine(d, limite)) + tol
    )
    return tarde, len(primera)


@kpi(
    codigo="H1",
    area=AREA,
    nombre="Dotación activa",
    unidad="n",
    direccion="ninguna",
    resumen=True,
    formula="Personas con contrato vigente a la fecha de corte",
    fuente="Persona",
)
def dotacion(ctx: Contexto) -> Valor:
    qs = personas_activas(ctx)
    return Valor(
        qs.count(),
        f"Planilla {qs.filter(condicion='PLANILLA').count()} / RxH {qs.filter(condicion='RXH').count()}",
    )


@kpi(
    codigo="H2",
    area=AREA,
    nombre="Costo bruto de personal del mes",
    unidad="pen",
    direccion="ninguna",
    resumen=True,
    formula="Suma del sueldo bruto del último mes cargado, por proyecto y categoría",
    fuente="CostoProyectoMes.sueldo_bruto",
    descripcion="Es costo bruto: no incluye cargas sociales ni provisiones (pregunta H-10 pendiente).",
)
def costo_mes(ctx: Contexto) -> Valor:
    qs, periodo = costos_periodo(ctx)
    return Valor(
        _f(qs.aggregate(s=Sum("sueldo_bruto"))["s"]) if periodo else None,
        f"Periodo {periodo:%m/%Y}" if periodo else "Sin datos",
    )


@kpi(
    codigo="H3",
    area=AREA,
    nombre="Costo promedio por persona",
    unidad="pen",
    direccion="ninguna",
    prioridad="B",
    formula="Costo bruto del mes / personas con costo en el mes",
    fuente="CostoProyectoMes",
)
def costo_promedio(ctx: Contexto) -> Valor:
    qs, periodo = costos_periodo(ctx)
    n = qs.values("persona").distinct().count()
    return Valor(_f(qs.aggregate(s=Sum("sueldo_bruto"))["s"]) / n if n else None)


@kpi(
    codigo="H4",
    area=AREA,
    nombre="Personal bajo recibo por honorarios",
    unidad="pct",
    direccion="ninguna",
    formula="Personas RxH / dotación activa",
    fuente="Persona.condicion",
)
def pct_rxh(ctx: Contexto) -> Valor:
    qs = personas_activas(ctx)
    return Valor(porcentaje(qs.filter(condicion="RXH").count(), qs.count()))


@kpi(
    codigo="H5",
    area=AREA,
    nombre="Costo de personal / valorización",
    unidad="pct",
    direccion="menor",
    umbral_alerta=25,
    umbral_critico=35,
    resumen=True,
    formula="Costo bruto de personal del mes / valorización real del mismo mes (sin IGV)",
    fuente="CostoProyectoMes, Valorizacion",
    descripcion="Cruza RR. HH. con Proyectos mediante el código de centro de costo.",
)
def personal_vs_valorizacion(ctx: Contexto) -> Valor:
    qs, periodo = costos_periodo(ctx)
    if not periodo:
        return Valor(None)
    # Solo el personal imputado a proyectos con valorización; el administrativo de áreas queda fuera.
    costo_proy = _f(
        qs.filter(centro_costo__tipo="PROYECTO").aggregate(s=Sum("sueldo_bruto"))["s"]
    )
    valorizado = valorizacion_real_periodo(ctx, periodo)
    return Valor(
        porcentaje(costo_proy, valorizado),
        f"Personal de proyectos {costo_proy:,.0f} / valorizado {valorizado:,.0f}",
    )


@kpi(
    codigo="H6",
    area=AREA,
    nombre="Tardanzas",
    unidad="pct",
    direccion="menor",
    umbral_alerta=10,
    umbral_critico=20,
    frecuencia="S",
    formula="Días-persona con tardanza / días-persona con marcación (últimos 15 días)",
    fuente="Marcacion",
    descripcion="Entrada 08:00 con 10 minutos de tolerancia (supuesto; pregunta H-06).",
)
def pct_tardanzas(ctx: Contexto) -> Valor:
    tarde, total = tardanzas(ctx)
    return Valor(porcentaje(tarde, total), f"{tarde} tardanzas en {total} días-persona")


@kpi(
    codigo="H8",
    area=AREA,
    nombre="Contratos por firmar o por vencer",
    unidad="n",
    direccion="menor",
    umbral_alerta=3,
    umbral_critico=8,
    resumen=True,
    frecuencia="S",
    formula="Contratos 'por elaborar' + contratos que vencen en los próximos 30 días",
    fuente="Persona.estado_contrato, fecha_fin_contrato",
)
def contratos(ctx: Contexto) -> Valor:
    qs = personas_activas(ctx)
    por_elaborar = qs.filter(estado_contrato="ELABORAR").count()
    por_vencer = qs.filter(
        fecha_fin_contrato__gte=ctx.corte,
        fecha_fin_contrato__lte=ctx.corte + timedelta(days=30),
    ).count()
    return Valor(
        por_elaborar + por_vencer,
        f"{por_elaborar} por elaborar, {por_vencer} por vencer",
    )


@kpi(
    codigo="H10",
    area=AREA,
    nombre="Cumplimiento de obligaciones (AFP, SCTR, PLAME)",
    unidad="pct",
    direccion="mayor",
    umbral_alerta=95,
    umbral_critico=80,
    resumen=True,
    prioridad="B",
    formula="Obligaciones entregadas a tiempo / obligaciones con fecha límite cumplida (6 meses)",
    fuente="Obligacion",
    descripcion="Fechas límite: AFP día 25, SCTR y seguro de vida día 28; PLAME por confirmar.",
)
def cumplimiento(ctx: Contexto) -> Valor:
    qs = Obligacion.objects.filter(
        fecha_limite__lte=ctx.corte, fecha_limite__gt=ctx.corte - timedelta(days=183)
    )
    a_tiempo = sum(
        1 for o in qs if o.fecha_entrega and o.fecha_entrega <= o.fecha_limite
    )
    return Valor(
        porcentaje(a_tiempo, qs.count()), f"{a_tiempo} de {qs.count()} a tiempo"
    )


@kpi(
    codigo="H11",
    area=AREA,
    nombre="Recibos por honorarios pendientes",
    unidad="n",
    direccion="menor",
    umbral_alerta=2,
    umbral_critico=6,
    frecuencia="S",
    formula="Personas RxH del último periodo con 'recibo emitido = NO'",
    fuente="PlanillaMes.recibo_emitido",
    descripcion="Si no entregan el recibo no se les paga.",
)
def rxh_pendientes(ctx: Contexto) -> Valor:
    qs = PlanillaMes.objects.filter(periodo__lte=ctx.mes)
    if ctx.empresa:
        qs = qs.filter(persona__empresa=ctx.empresa)
    if ctx.proyecto:
        qs = qs.filter(persona__centro_costo=ctx.proyecto)
    ultimo = qs.order_by("-periodo").values_list("periodo", flat=True).first()
    if not ultimo:
        return Valor(None)
    return Valor(
        qs.filter(periodo=ultimo, condicion="RXH", recibo_emitido=False).count(),
        f"Periodo {ultimo:%m/%Y}",
    )


@kpi(
    codigo="Q5",
    area="calidad",
    nombre="Marcaciones sin persona identificada",
    unidad="pct",
    direccion="menor",
    umbral_alerta=2,
    umbral_critico=10,
    formula="Marcaciones cuyo código del reloj no coincide con ninguna persona / marcaciones totales",
    fuente="Marcacion.persona",
    descripcion="Mide el cruce código del reloj - DNI (pregunta H-05).",
)
def marcaciones_huerfanas(ctx: Contexto) -> Valor:
    qs = Marcacion.objects.filter(
        fecha_hora__date__lte=ctx.corte,
        fecha_hora__date__gt=ctx.corte - timedelta(days=VENTANA_ASISTENCIA),
    )
    return Valor(porcentaje(qs.filter(persona=None).count(), qs.count()))
