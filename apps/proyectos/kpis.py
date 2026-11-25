"""KPI del área de Proyectos (P1 a P13 de docs/parte1/06_propuesta_kpi.md).

La lógica de valor ganado está en `services.py`; aquí cada función solo arma el indicador.
"""

from django.conf import settings
from django.db.models import Sum

from apps.core.kpi import Contexto, Valor, kpi
from apps.core.services import igv, porcentaje

from .models import Gasto, Valorizacion
from .services import evm_cartera, evm_total, gastos_en_alcance, proyectos_en_alcance

AREA = "proyectos"


def _total(ctx):
    lista = evm_cartera(ctx)
    return lista, evm_total(lista)


def _suma(qs, campo="monto_pen_sin_igv"):
    return float(qs.aggregate(s=Sum(campo))["s"] or 0)


@kpi(
    codigo="P123",
    area=AREA,
    nombre="Ejemplo123",
    unidad="pct",
    direccion="ninguna",
    formula="Valorización real acumulada / monto contratado (meses cerrados)",
    fuente="Valorizacion.monto_real",
    frecuencia="M",
    prioridad="A",
)
def funcion_ejemplo(ctx: Contexto) -> Valor:
    return Valor(0.2)


@kpi(
    codigo="P1",
    area=AREA,
    nombre="Avance valorizado",
    unidad="pct",
    direccion="ninguna",
    formula="Valorización real acumulada / monto contratado (meses cerrados)",
    fuente="Valorizacion.monto_real",
    frecuencia="M",
    prioridad="A",
)
def avance_real(ctx: Contexto) -> Valor:
    _, t = _total(ctx)
    return Valor(
        t.real_pct * 100 if t.bac else None,
        f"{len(evm_cartera(ctx))} proyectos en ejecución",
    )


@kpi(
    codigo="P2",
    area=AREA,
    nombre="Avance planificado",
    unidad="pct",
    direccion="ninguna",
    formula="Valorización planificada acumulada / monto contratado (meses cerrados)",
    fuente="Valorizacion.monto_planificado",
    frecuencia="M",
    prioridad="A",
)
def avance_plan(ctx: Contexto) -> Valor:
    _, t = _total(ctx)
    return Valor(t.plan_pct * 100 if t.bac else None)


@kpi(
    codigo="P3",
    area=AREA,
    nombre="SPI (cronograma)",
    unidad="ratio",
    direccion="mayor",
    umbral_alerta=0.90,
    umbral_critico=0.75,
    resumen=True,
    formula="EV / PV = avance real / avance planificado",
    fuente="Valorizacion",
    descripcion="Mayor o igual a 1: la obra va a tiempo o adelantada. Menor a 0.75: atraso importante.",
)
def spi(ctx: Contexto) -> Valor:
    _, t = _total(ctx)
    return Valor(
        t.spi, f"EV {t.ev:,.0f} / PV {t.pv:,.0f}" if t.pv else "Sin avance planificado"
    )


@kpi(
    codigo="P4",
    area=AREA,
    nombre="Costo real de obra (AC)",
    unidad="pen",
    direccion="ninguna",
    formula="Gastos reales y pagados de los componentes de obra, sin IGV",
    fuente="Gasto",
    descripcion="Componentes incluidos: "
    + ", ".join(settings.CUADRO_MANDO["COMPONENTES_OBRA"]),
)
def costo_real(ctx: Contexto) -> Valor:
    _, t = _total(ctx)
    return Valor(t.ac if t.bac else None)


@kpi(
    codigo="P5",
    area=AREA,
    nombre="CPI (costo)",
    unidad="ratio",
    direccion="mayor",
    umbral_alerta=0.95,
    umbral_critico=0.85,
    resumen=True,
    formula="EV / AC. EV = avance real x BAC de costo (meta 70 %, sin IGV)",
    fuente="Valorizacion, Gasto, PresupuestoEscenario",
    descripcion="Mayor a 1: se gasta menos de lo que corresponde al avance logrado.",
)
def cpi(ctx: Contexto) -> Valor:
    _, t = _total(ctx)
    return Valor(
        t.cpi, f"EV {t.ev:,.0f} / AC {t.ac:,.0f}" if t.ac else "Sin gasto real"
    )


@kpi(
    codigo="P6",
    area=AREA,
    nombre="Margen esperado al cierre",
    unidad="pct",
    direccion="mayor",
    umbral_alerta=20,
    umbral_critico=10,
    resumen=True,
    formula="(Contrato sin IGV - EAC) / Contrato sin IGV; EAC = BAC / CPI",
    fuente="PresupuestoEscenario, Gasto, Valorizacion",
    descripcion="Proyección del margen de obra si se mantiene el CPI actual. No incluye expediente técnico ni precontractual.",
)
def margen(ctx: Contexto) -> Valor:
    lista, _ = _total(ctx)
    validos = [e for e in lista if e.eac]
    if not validos:
        return Valor(None, "Sin datos suficientes")
    contrato = sum(e.contrato_sin_igv for e in validos)
    eac = sum(e.eac for e in validos)
    return Valor((contrato - eac) / contrato * 100, f"{len(validos)} proyectos con CPI")


@kpi(
    codigo="P7",
    area=AREA,
    nombre="Desviación frente a la meta de costo",
    unidad="pct",
    direccion="menor",
    umbral_alerta=5,
    umbral_critico=15,
    formula="(AC / EV - 1) x 100",
    fuente="Valorizacion, Gasto",
    descripcion="Cuánto se gastó de más (positivo) o de menos (negativo) respecto al costo meta del avance logrado.",
)
def desviacion(ctx: Contexto) -> Valor:
    _, t = _total(ctx)
    return Valor((t.ac / t.ev - 1) * 100 if t.ev and t.ac else None)


@kpi(
    codigo="P8",
    area=AREA,
    nombre="Gasto pagado total",
    unidad="pen",
    direccion="ninguna",
    formula="Gastos REALES pagados de todos los componentes, sin IGV",
    fuente="Gasto",
    frecuencia="S",
)
def gasto_pagado(ctx: Contexto) -> Valor:
    qs = gastos_en_alcance(ctx).filter(
        naturaleza="REAL", estado="PAGADO", fecha__lte=ctx.corte
    )
    return Valor(_suma(qs))


@kpi(
    codigo="P9",
    area=AREA,
    nombre="Pendiente de pago",
    unidad="pen",
    direccion="ninguna",
    frecuencia="S",
    formula="Gastos REALES en estado PENDIENTE (los proyectados se muestran aparte)",
    fuente="Gasto",
)
def pendiente(ctx: Contexto) -> Valor:
    qs = gastos_en_alcance(ctx).filter(
        naturaleza="REAL", estado="PENDIENTE", fecha__lte=ctx.corte
    )
    proyectado = _suma(gastos_en_alcance(ctx).filter(naturaleza="PROYECTADO"))
    return Valor(_suma(qs), f"Proyectado aparte: S/ {proyectado:,.0f}")


@kpi(
    codigo="P10",
    area=AREA,
    nombre="Flujo neto acumulado",
    unidad="pen",
    direccion="mayor",
    umbral_alerta=0,
    umbral_critico=-500_000,
    prioridad="B",
    formula="Cobros de valorizaciones - pagos reales (sin IGV)",
    fuente="Valorizacion.monto_cobrado, Gasto",
    descripcion="Negativo: el proyecto se financia con caja de la empresa.",
)
def flujo_neto(ctx: Contexto) -> Valor:
    cobros = Valorizacion.objects.filter(
        proyecto__in=proyectos_en_alcance(ctx), fecha_cobro__lte=ctx.corte
    )
    cobrado = float(cobros.aggregate(s=Sum("monto_cobrado"))["s"] or 0) / (1 + igv())
    pagado = _suma(
        gastos_en_alcance(ctx).filter(
            naturaleza="REAL", estado="PAGADO", fecha__lte=ctx.corte
        )
    )
    return Valor(cobrado - pagado, f"Cobrado {cobrado:,.0f} - pagado {pagado:,.0f}")


@kpi(
    codigo="P11",
    area=AREA,
    nombre="Costos no operativos",
    unidad="pct",
    direccion="menor",
    umbral_alerta=5,
    umbral_critico=10,
    prioridad="B",
    formula="(Préstamos + reembolsos) / gasto pagado total",
    fuente="Gasto.tipo_gasto",
    descripcion="Pagos de préstamos y reembolsos cargados al proyecto; inflan el costo real.",
)
def no_operativos(ctx: Contexto) -> Valor:
    base = gastos_en_alcance(ctx).filter(
        naturaleza="REAL", estado="PAGADO", fecha__lte=ctx.corte
    )
    total = _suma(base)
    return Valor(
        porcentaje(_suma(base.filter(tipo_gasto__in=["PRESTAMO", "REEMBOLSO"])), total)
    )


@kpi(
    codigo="P12",
    area=AREA,
    nombre="Brecha plazo vs avance",
    unidad="pct",
    direccion="menor",
    umbral_alerta=5,
    umbral_critico=15,
    prioridad="B",
    formula="% de plazo de obra transcurrido - % de avance real (puntos porcentuales)",
    fuente="Proyecto, Valorizacion",
    descripcion="Positivo: se consumió más plazo que avance.",
)
def brecha_plazo(ctx: Contexto) -> Valor:
    lista = evm_cartera(ctx)
    pesos, brechas = 0.0, 0.0
    for e in lista:
        p = e.proyecto
        if not p.plazo_eo_dias:
            continue
        transcurrido = (
            min((ctx.corte - p.fecha_acta_eo).days / p.plazo_eo_dias, 1.0) * 100
        )
        brechas += (transcurrido - e.real_pct * 100) * float(p.monto_contrato)
        pesos += float(p.monto_contrato)
    return Valor(
        brechas / pesos if pesos else None, "Promedio ponderado por monto de contrato"
    )


@kpi(
    codigo="P13",
    area=AREA,
    nombre="Gasto precontractual / contrato",
    unidad="pct",
    direccion="menor",
    umbral_alerta=8,
    umbral_critico=12,
    prioridad="B",
    formula="Gasto componente 00 / contrato sin IGV",
    fuente="Gasto, Proyecto",
)
def precontractual(ctx: Contexto) -> Valor:
    gasto = _suma(
        gastos_en_alcance(ctx).filter(
            categoria__componente="00", naturaleza="REAL", fecha__lte=ctx.corte
        )
    )
    contrato = sum(float(p.monto_contrato) for p in proyectos_en_alcance(ctx)) / (
        1 + igv()
    )
    return Valor(porcentaje(gasto, contrato))


@kpi(
    codigo="Q3",
    area="calidad",
    nombre="Gastos de proyecto con N.º de orden",
    unidad="pct",
    direccion="mayor",
    umbral_alerta=80,
    umbral_critico=50,
    prioridad="A",
    formula="Gastos operativos con nro_orden / gastos operativos",
    fuente="Gasto.nro_orden",
    descripcion="Mide el vínculo Proyectos-Logística; en el libro actual la columna RQ está vacía.",
)
def gastos_con_orden(ctx: Contexto) -> Valor:
    base = gastos_en_alcance(ctx).filter(
        tipo_gasto="OPERATIVO", categoria__componente__in=["01", "02", "05"]
    )
    return Valor(
        porcentaje(base.exclude(nro_orden="").count(), base.count()),
        f"{base.count()} gastos operativos de obra",
    )
