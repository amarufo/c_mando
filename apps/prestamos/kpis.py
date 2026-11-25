"""KPI de Préstamos y deuda (F1 a F11 de docs/parte1/06_propuesta_kpi.md)."""

from collections import defaultdict
from datetime import timedelta

from apps.core.kpi import Contexto, Valor, kpi
from apps.core.services import fin_de_mes, porcentaje

from .services import cuotas

AREA = "prestamos"


def _pendientes(ctx):
    return [c for c in cuotas(ctx) if not c.pagada]


@kpi(
    codigo="F1",
    area=AREA,
    nombre="Deuda vigente (capital por pagar)",
    unidad="pen",
    direccion="ninguna",
    resumen=True,
    formula="Suma del capital de las cuotas no pagadas",
    fuente="Cuota.capital, PagoCuota",
    descripcion="Equivalente en soles; los préstamos en dólares usan el TC vigente al corte.",
)
def deuda_vigente(ctx: Contexto) -> Valor:
    p = _pendientes(ctx)
    return Valor(
        sum(c.capital for c in p), f"{len({c.prestamo for c in p})} préstamos con saldo"
    )


@kpi(
    codigo="F2",
    area=AREA,
    nombre="Servicio de deuda del mes",
    unidad="pen",
    direccion="ninguna",
    frecuencia="S",
    formula="Cuotas (capital + interés + otros) con vencimiento en el mes del corte",
    fuente="Cuota.total_cuota",
)
def servicio_mes(ctx: Contexto) -> Valor:
    fin = fin_de_mes(ctx.corte)
    mes = [c for c in cuotas(ctx) if ctx.mes <= c.vencimiento <= fin]
    return Valor(
        sum(c.total for c in mes),
        f"{len(mes)} cuotas, {sum(1 for c in mes if c.pagada)} ya pagadas",
    )


@kpi(
    codigo="F3",
    area=AREA,
    nombre="Vencimientos a 90 días",
    unidad="pen",
    direccion="ninguna",
    resumen=True,
    frecuencia="S",
    formula="Cuotas no pagadas con vencimiento entre el corte y +90 días",
    fuente="Cuota",
)
def vencimientos_90(ctx: Contexto) -> Valor:
    p = [
        c
        for c in _pendientes(ctx)
        if ctx.corte <= c.vencimiento <= ctx.corte + timedelta(days=90)
    ]
    return Valor(sum(c.total for c in p), f"{len(p)} cuotas")


@kpi(
    codigo="F4",
    area=AREA,
    nombre="Costo financiero total",
    unidad="pen",
    direccion="ninguna",
    prioridad="A",
    formula="Intereses + otros costos de todas las cuotas programadas",
    fuente="Cuota.interes, Cuota.otros_costos",
)
def costo_financiero(ctx: Contexto) -> Valor:
    todas = cuotas(ctx)
    total = sum(c.costo_financiero for c in todas)
    real = sum(c.costo_financiero for c in todas if c.pagada)
    return Valor(
        total, f"Realizado {porcentaje(real, total) or 0:.0f} % (S/ {real:,.0f})"
    )


@kpi(
    codigo="F6",
    area=AREA,
    nombre="Concentración en 3 acreedores",
    unidad="pct",
    direccion="menor",
    umbral_alerta=50,
    umbral_critico=70,
    resumen=True,
    formula="Capital por pagar de los 3 mayores acreedores / capital por pagar total",
    fuente="Cuota, Prestamo.acreedor",
)
def concentracion_acreedores(ctx: Contexto) -> Valor:
    por = defaultdict(float)
    for c in _pendientes(ctx):
        por[c.acreedor] += c.capital
    valores = sorted(por.values(), reverse=True)
    return Valor(
        porcentaje(sum(valores[:3]), sum(valores)),
        f"{len(valores)} acreedores con saldo",
    )


@kpi(
    codigo="F7",
    area=AREA,
    nombre="Concentración en un mes",
    unidad="pct",
    direccion="menor",
    umbral_alerta=30,
    umbral_critico=45,
    formula="Mayor vencimiento mensual / total por pagar",
    fuente="Cuota.fecha_vencimiento",
    descripcion="Un valor alto indica riesgo de caja en un mes puntual.",
)
def concentracion_mes(ctx: Contexto) -> Valor:
    por = defaultdict(float)
    for c in _pendientes(ctx):
        por[c.vencimiento.replace(day=1)] += c.total
    if not por:
        return Valor(None)
    mes, monto = max(por.items(), key=lambda kv: kv[1])
    return Valor(
        porcentaje(monto, sum(por.values())),
        f"Mes de mayor vencimiento: {mes:%m/%Y} (S/ {monto:,.0f})",
    )


@kpi(
    codigo="F8",
    area=AREA,
    nombre="Cuotas vencidas sin pago",
    unidad="pen",
    direccion="menor",
    umbral_alerta=0,
    umbral_critico=100_000,
    resumen=True,
    frecuencia="S",
    formula="Cuotas con vencimiento anterior al corte y sin pago registrado",
    fuente="Cuota, PagoCuota",
    descripcion="Requiere el registro real de pagos (tabla PagoCuota). El archivo actual la reemplaza por TODAY().",
)
def mora(ctx: Contexto) -> Valor:
    v = [c for c in _pendientes(ctx) if c.vencimiento < ctx.corte]
    return Valor(sum(c.total for c in v), f"{len(v)} cuotas vencidas")


@kpi(
    codigo="F10",
    area=AREA,
    nombre="Deuda personal del gerente",
    unidad="pct",
    direccion="menor",
    umbral_alerta=5,
    umbral_critico=15,
    prioridad="B",
    formula="Capital por pagar personal / capital por pagar total",
    fuente="Prestamo.es_personal",
    descripcion="Pregunta G-03 pendiente: ¿se muestra junto a la deuda de las empresas?",
)
def deuda_personal(ctx: Contexto) -> Valor:
    p = _pendientes(ctx)
    return Valor(
        porcentaje(
            sum(c.capital for c in p if c.es_personal), sum(c.capital for c in p)
        )
    )


@kpi(
    codigo="F11",
    area=AREA,
    nombre="Deuda en dólares",
    unidad="pct",
    direccion="ninguna",
    prioridad="B",
    formula="Capital por pagar en US$ (en soles) / capital por pagar total",
    fuente="Prestamo.moneda",
)
def deuda_usd(ctx: Contexto) -> Valor:
    p = _pendientes(ctx)
    return Valor(
        porcentaje(sum(c.capital for c in p if c.en_dolares), sum(c.capital for c in p))
    )
