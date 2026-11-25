"""Pantalla de Préstamos y deuda."""

from collections import defaultdict
from datetime import timedelta

import plotly.graph_objects as go

from apps.core.dashboard import ContenidoArea, Grafico, Tabla
from apps.core.kpi import Contexto
from apps.core.services import fin_de_mes, primer_dia, rango_meses, sumar_meses
from apps.core.theme import PALETA, SEMAFORO, SERIE, a_html, aplicar_tema

from .models import Prestamo
from .services import cuotas


def _vencimientos(ctx: Contexto, todas) -> Grafico:
    """Cuotas por mes (6 meses atrás, 14 adelante), separando lo pagado de lo pendiente."""
    meses = rango_meses(sumar_meses(ctx.mes, -5), sumar_meses(ctx.mes, 14))
    pagado, pendiente, mora = defaultdict(float), defaultdict(float), defaultdict(float)
    for c in todas:
        m = primer_dia(c.vencimiento)
        if c.pagada:
            pagado[m] += c.total
        elif c.vencimiento < ctx.corte:
            mora[m] += c.total
        else:
            pendiente[m] += c.total
    fig = go.Figure()
    fig.add_bar(
        x=meses,
        y=[pagado[m] for m in meses],
        name="Pagado",
        marker_color=SEMAFORO["ok"],
    )
    fig.add_bar(
        x=meses,
        y=[mora[m] for m in meses],
        name="Vencido sin pago",
        marker_color=SEMAFORO["critico"],
    )
    fig.add_bar(
        x=meses,
        y=[pendiente[m] for m in meses],
        name="Por pagar",
        marker_color=PALETA["primario"],
    )
    fig.update_layout(barmode="stack")
    aplicar_tema(fig, "Cuotas por mes de vencimiento (S/ equivalente)")
    fig.update_yaxes(tickformat=",.0f")
    return Grafico("Vencimientos", a_html(fig), 12)


def _composicion(ctx: Contexto, todas) -> Grafico:
    """Capital, interés y otros costos de las cuotas aún no pagadas, por mes."""
    meses = rango_meses(ctx.mes, sumar_meses(ctx.mes, 14))
    cap, inte, otr = defaultdict(float), defaultdict(float), defaultdict(float)
    for c in todas:
        if not c.pagada and primer_dia(c.vencimiento) in meses:
            m = primer_dia(c.vencimiento)
            cap[m] += c.capital
            inte[m] += c.interes
            otr[m] += c.otros
    fig = go.Figure()
    fig.add_bar(
        x=meses,
        y=[cap[m] for m in meses],
        name="Capital",
        marker_color=PALETA["primario"],
    )
    fig.add_bar(
        x=meses,
        y=[inte[m] for m in meses],
        name="Interés",
        marker_color=PALETA["acento"],
    )
    fig.add_bar(
        x=meses,
        y=[otr[m] for m in meses],
        name="Otros costos",
        marker_color=PALETA["gris"],
    )
    fig.update_layout(barmode="stack")
    aplicar_tema(fig, "Qué se paga: capital e interés por mes (solo pendiente)")
    fig.update_yaxes(tickformat=",.0f")
    return Grafico("Composición", a_html(fig), 6)


def _por_acreedor(todas) -> Grafico:
    por = defaultdict(float)
    for c in todas:
        if not c.pagada:
            por[c.acreedor] += c.capital
    top = sorted(por.items(), key=lambda kv: kv[1])[-10:]
    fig = go.Figure(
        go.Bar(
            x=[v for _, v in top],
            y=[k[:28] for k, _ in top],
            orientation="h",
            marker_color=PALETA["secundario"],
        )
    )
    aplicar_tema(fig, "Capital por pagar según acreedor (S/)")
    fig.update_xaxes(tickformat=",.0f")
    fig.update_layout(hovermode="closest")
    return Grafico("Acreedores", a_html(fig), 6)


def _donut(titulo, datos: dict) -> Grafico:
    fig = go.Figure(
        go.Pie(
            labels=list(datos),
            values=list(datos.values()),
            hole=0.55,
            marker=dict(colors=SERIE),
        )
    )
    aplicar_tema(fig, titulo)
    fig.update_layout(hovermode="closest")
    return Grafico(titulo, a_html(fig), 6)


def _tabla_mes(ctx: Contexto, todas) -> Tabla:
    """Equivalente a la hoja CRONOGRAMA_MES: cuotas del mes con la fecha límite para programar el pago."""
    from django.conf import settings

    anticipacion = timedelta(days=settings.CUADRO_MANDO["DIAS_ANTICIPACION_PAGO"])
    fin = fin_de_mes(ctx.corte)
    mes = sorted(
        (c for c in todas if ctx.mes <= c.vencimiento <= fin),
        key=lambda c: c.vencimiento,
    )
    filas = []
    for c in mes[:25]:
        limite = c.vencimiento - anticipacion
        estado = (
            ("Pagada", "ok")
            if c.pagada
            else (
                ("Vencida", "critico")
                if c.vencimiento < ctx.corte
                else (
                    ("Programar ya", "alerta")
                    if limite <= ctx.corte
                    else ("Pendiente", "neutro")
                )
            )
        )
        filas.append(
            [
                f"{c.vencimiento:%d/%m}",
                f"{limite:%d/%m}",
                c.acreedor,
                c.deudor,
                f"{c.total:,.0f}",
                estado,
            ]
        )
    return Tabla(
        f"Cuotas de {ctx.mes:%m/%Y} (fecha límite = vencimiento menos {anticipacion.days} días)",
        ["Vence", "Fecha límite", "Acreedor", "Deudor", "Total S/", "Estado"],
        filas,
        12,
    )


def construir(ctx: Contexto) -> ContenidoArea:
    todas = cuotas(ctx)
    c = ContenidoArea()
    c.graficos += [
        _vencimientos(ctx, todas),
        _composicion(ctx, todas),
        _por_acreedor(todas),
    ]
    por_deudor, por_tipo = defaultdict(float), defaultdict(float)
    etiquetas = dict(Prestamo.Tipo.choices)
    for x in todas:
        if not x.pagada:
            por_deudor[x.deudor] += x.capital
            por_tipo[etiquetas[x.tipo]] += x.capital
    c.graficos += [
        _donut("Capital por pagar según deudor", por_deudor),
        _donut("Capital por pagar según tipo de acreedor", por_tipo),
    ]
    c.tablas.append(_tabla_mes(ctx, todas))
    c.notas.append(
        "Una cuota se considera pagada solo si existe pago registrado. Dólares convertidos con el tipo de cambio del corte."
    )
    return c


def para_resumen(ctx: Contexto):
    return [_vencimientos(ctx, cuotas(ctx))]
