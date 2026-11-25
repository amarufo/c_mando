"""
Pantalla del área de Proyectos: gráficos y tablas (los KPI los pinta la plantilla desde el registro).
"""

from collections import defaultdict

import plotly.graph_objects as go
from django.conf import settings
from django.db.models import Sum

from apps.core.dashboard import ContenidoArea, Grafico, Tabla
from apps.core.kpi import Contexto, evaluar, REGISTRO
from apps.core.services import igv, primer_dia, rango_meses
from apps.core.theme import PALETA, SEMAFORO, a_html, aplicar_tema

from .models import Gasto, Valorizacion
from .services import evm_cartera, gastos_en_alcance, proyectos_en_alcance


def _serie_curva_s(ctx: Contexto):
    """Series mensuales acumuladas de PV, EV y AC (en soles sin IGV, base de costo meta)."""
    evms = evm_cartera(ctx)
    if not evms:
        return None
    bac_total = sum(e.bac for e in evms)
    proyectos = [e.proyecto for e in evms]
    por_mes_plan, por_mes_real = defaultdict(float), defaultdict(float)
    bac_por = {e.proyecto.pk: e.bac for e in evms}
    contrato_por = {e.proyecto.pk: float(e.proyecto.monto_contrato) for e in evms}
    cierre = primer_dia(ctx.corte)
    for v in Valorizacion.objects.filter(proyecto__in=proyectos):
        factor = bac_por[v.proyecto_id] / contrato_por[v.proyecto_id]
        por_mes_plan[v.periodo] += float(v.monto_planificado) * factor
        if v.monto_real is not None and v.periodo < cierre:
            por_mes_real[v.periodo] += float(v.monto_real) * factor
    ac_mes = defaultdict(float)
    qs = Gasto.objects.filter(
        proyecto__in=proyectos,
        naturaleza="REAL",
        estado="PAGADO",
        fecha__lte=ctx.corte,
        categoria__componente__in=settings.CUADRO_MANDO["COMPONENTES_OBRA"],
    )
    for fecha, monto in qs.values_list("fecha", "monto_pen_sin_igv"):
        ac_mes[primer_dia(fecha)] += float(monto)
    meses = rango_meses(min(por_mes_plan), max(por_mes_plan))
    pv, ev, ac, acum_pv, acum_ev, acum_ac = [], [], [], 0, 0, 0
    for m in meses:
        acum_pv += por_mes_plan.get(m, 0)
        pv.append(acum_pv)
        if m < cierre:
            acum_ev += por_mes_real.get(m, 0)
            ev.append(acum_ev)
        else:
            ev.append(None)
        if m <= ctx.corte:
            acum_ac += ac_mes.get(m, 0)
            ac.append(acum_ac)
        else:
            ac.append(None)
    return meses, pv, ev, ac, bac_total


def grafico_curva_s(ctx: Contexto) -> Grafico | None:
    datos = _serie_curva_s(ctx)
    if not datos:
        return None
    meses, pv, ev, ac, bac = datos
    fig = go.Figure()
    fig.add_scatter(
        x=meses,
        y=pv,
        name="Planificado (PV)",
        line=dict(color=PALETA["gris"], dash="dash"),
    )
    fig.add_scatter(
        x=meses, y=ev, name="Ganado (EV)", line=dict(color=PALETA["primario"], width=3)
    )
    fig.add_scatter(
        x=meses,
        y=ac,
        name="Costo real (AC)",
        line=dict(color=PALETA["acento"], width=3),
    )
    fig.add_hline(
        y=bac,
        line_dash="dot",
        line_color=SEMAFORO["critico"],
        annotation_text="BAC de costo",
    )
    aplicar_tema(fig, "Curva S: planificado, ganado y costo real (S/ sin IGV)")
    fig.update_yaxes(tickformat=",.0f")
    return Grafico("Curva S", a_html(fig), 12)


def _grafico_componentes(ctx: Contexto) -> Grafico:
    nombres = {
        "00": "Precontractual",
        "01": "Ejecución de obra",
        "02": "Gastos generales",
        "03": "Expediente técnico",
        "04": "Supervisión ET",
        "05": "Supervisión obra",
        "06": "Gestión",
        "07": "Liquidación",
        "3101": "Administrativos",
    }
    filas = (
        gastos_en_alcance(ctx)
        .filter(fecha__lte=ctx.corte)
        .values("categoria__componente", "estado", "naturaleza")
        .annotate(t=Sum("monto_pen_sin_igv"))
    )
    acum = defaultdict(lambda: defaultdict(float))
    for f in filas:
        clase = (
            "Proyectado"
            if f["naturaleza"] == "PROYECTADO"
            else ("Pagado" if f["estado"] == "PAGADO" else "Pendiente")
        )
        acum[f["categoria__componente"]][clase] += float(f["t"])
    comp = sorted(acum)
    fig = go.Figure()
    for clase, color in (
        ("Pagado", PALETA["primario"]),
        ("Pendiente", PALETA["acento"]),
        ("Proyectado", "#B8C0CC"),
    ):
        fig.add_bar(
            x=[nombres.get(c, c) for c in comp],
            y=[acum[c].get(clase, 0) for c in comp],
            name=clase,
            marker_color=color,
        )
    fig.update_layout(barmode="stack")
    aplicar_tema(fig, "Gasto por componente (S/ sin IGV)")
    fig.update_yaxes(tickformat=",.0f")
    return Grafico("Gasto por componente", a_html(fig), 6)


def _grafico_flujo(ctx: Contexto) -> Grafico:
    cobros, pagos = defaultdict(float), defaultdict(float)
    ps = proyectos_en_alcance(ctx)
    for fecha, monto in Valorizacion.objects.filter(
        proyecto__in=ps, fecha_cobro__lte=ctx.corte
    ).values_list("fecha_cobro", "monto_cobrado"):
        cobros[primer_dia(fecha)] += float(monto or 0) / (1 + igv())
    for fecha, monto in (
        gastos_en_alcance(ctx)
        .filter(naturaleza="REAL", estado="PAGADO", fecha__lte=ctx.corte)
        .values_list("fecha", "monto_pen_sin_igv")
    ):
        pagos[primer_dia(fecha)] += float(monto)
    meses = sorted(set(cobros) | set(pagos))
    if not meses:
        return Grafico("Flujo de caja", "<p class='text-muted'>Sin movimientos.</p>", 6)
    meses = rango_meses(meses[0], meses[-1])
    neto, acum = [], 0.0
    for m in meses:
        acum += cobros.get(m, 0) - pagos.get(m, 0)
        neto.append(acum)
    fig = go.Figure()
    fig.add_bar(
        x=meses,
        y=[cobros.get(m, 0) for m in meses],
        name="Cobros",
        marker_color=SEMAFORO["ok"],
    )
    fig.add_bar(
        x=meses,
        y=[-pagos.get(m, 0) for m in meses],
        name="Pagos",
        marker_color=PALETA["secundario"],
    )
    fig.add_scatter(
        x=meses,
        y=neto,
        name="Neto acumulado",
        line=dict(color=PALETA["acento"], width=3),
    )
    fig.update_layout(barmode="relative")
    aplicar_tema(fig, "Flujo de caja mensual (S/ sin IGV)")
    fig.update_yaxes(tickformat=",.0f")
    return Grafico("Flujo de caja", a_html(fig), 6)


def _tabla_cartera(ctx: Contexto) -> Tabla:
    """Una fila por proyecto con semáforo. Las celdas (texto, estado) se pintan con el color del estado."""

    def celda(codigo, valor, formato):
        return (
            formato(valor) if valor is not None else "—",
            evaluar(REGISTRO[codigo], valor),
        )

    filas = []
    for e in evm_cartera(ctx):
        filas.append(
            [
                e.proyecto.nombre,
                f"{e.real_pct * 100:.1f} %",
                f"{e.plan_pct * 100:.1f} %",
                celda("P3", e.spi, lambda v: f"{v:.2f}"),
                celda("P5", e.cpi, lambda v: f"{v:.2f}"),
                celda("P6", e.margen_pct, lambda v: f"{v:.1f} %"),
                f"S/ {e.ac:,.0f}",
            ]
        )
    return Tabla(
        "Cartera de proyectos en ejecución",
        [
            "Proyecto",
            "Avance real",
            "Avance plan",
            "SPI",
            "CPI",
            "Margen esperado",
            "Costo real (AC)",
        ],
        filas,
        12,
    )


def _grafico_cpi_por_proyecto(ctx: Contexto) -> Grafico | None:
    lista = [e for e in evm_cartera(ctx) if e.cpi and e.spi]
    if not lista:
        return None
    fig = go.Figure()
    fig.add_bar(
        x=[e.proyecto.nombre[:28] for e in lista],
        y=[e.spi for e in lista],
        name="SPI",
        marker_color=PALETA["secundario"],
    )
    fig.add_bar(
        x=[e.proyecto.nombre[:28] for e in lista],
        y=[e.cpi for e in lista],
        name="CPI",
        marker_color=PALETA["acento"],
    )
    fig.add_hline(y=1, line_dash="dot", line_color=PALETA["gris"])
    fig.update_layout(barmode="group")
    aplicar_tema(fig, "SPI y CPI por proyecto (1.0 = según lo previsto)")
    return Grafico("SPI y CPI", a_html(fig), 12)


def construir(ctx: Contexto) -> ContenidoArea:
    c = ContenidoArea()
    c.tablas.append(_tabla_cartera(ctx))
    for g in (grafico_curva_s(ctx), _grafico_cpi_por_proyecto(ctx)):
        if g:
            c.graficos.append(g)
    c.graficos += [_grafico_componentes(ctx), _grafico_flujo(ctx)]
    c.notas.append(
        "Valor ganado sin IGV, con base de costo meta (70 %). Alcance de costo: componentes 01, 02 y 05. Supuestos a validar: ver diccionario de KPI."
    )
    return c


def para_resumen(ctx: Contexto):
    g = _grafico_cpi_por_proyecto(ctx)
    return [g] if g else []
