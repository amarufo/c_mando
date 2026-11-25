"""Pantalla de Logística y pagos."""

from collections import Counter, defaultdict
from datetime import timedelta

import plotly.graph_objects as go
from django.db.models import Sum

from apps.core.dashboard import ContenidoArea, Grafico, Tabla
from apps.core.kpi import Contexto
from apps.core.services import primer_dia, rango_meses, sumar_meses
from apps.core.theme import PALETA, SEMAFORO, SERIE, a_html, aplicar_tema

from .kpis import comprobantes, ordenes, por_pagar, requerimientos
from .models import Orden, Requerimiento


def _embudo(ctx: Contexto) -> Grafico:
    rq = requerimientos(ctx)
    ords = ordenes(ctx).exclude(estado="RECHAZADA")
    nros = list(ords.values_list("nro", flat=True))
    comp = comprobantes(ctx).filter(nro_orden__in=nros)
    pagados = comp.filter(estado_pago="PAGADO", fecha_pago_real__lte=ctx.corte)
    etapas = [
        "RQ creados",
        "RQ aprobados",
        "Órdenes emitidas",
        "Comprobantes recibidos",
        "Comprobantes pagados",
    ]
    valores = [
        rq.count(),
        rq.exclude(estado__in=["RECHAZADA", "PENDIENTE"]).count(),
        ords.count(),
        comp.count(),
        pagados.count(),
    ]
    fig = go.Figure(
        go.Funnel(
            y=etapas,
            x=valores,
            marker=dict(
                color=[
                    PALETA["primario"],
                    PALETA["secundario"],
                    "#5BC0BE",
                    PALETA["acento"],
                    SEMAFORO["ok"],
                ]
            ),
            textinfo="value+percent initial",
        )
    )
    aplicar_tema(fig, "Embudo de compras (90 días)")
    return Grafico("Embudo", a_html(fig), 6)


def _antiguedad(ctx: Contexto) -> Grafico:
    tramos = [
        ("Por vencer", None, None),
        ("Vencida 1-7 d", 1, 7),
        ("8-15 d", 8, 15),
        ("16-30 d", 16, 30),
        ("Más de 30 d", 31, 9999),
    ]
    montos = {t[0]: 0.0 for t in tramos}
    for fv, total in por_pagar(ctx).values_list("fecha_venc", "total_pen"):
        d = (ctx.corte - fv).days
        for nombre, lo, hi in tramos:
            if (lo is None and d < 1) or (lo is not None and lo <= d <= hi):
                montos[nombre] += float(total)
                break
    colores = [
        SEMAFORO["ok"],
        "#F7C948",
        PALETA["acento"],
        "#E07A5F",
        SEMAFORO["critico"],
    ]
    fig = go.Figure(
        go.Bar(x=list(montos), y=list(montos.values()), marker_color=colores)
    )
    aplicar_tema(fig, "Cuentas por pagar según antigüedad (S/)")
    fig.update_yaxes(tickformat=",.0f")
    return Grafico("Antigüedad de deuda", a_html(fig), 6)


def _compras_proyecto(ctx: Contexto) -> Grafico:
    filas = (
        ordenes(ctx)
        .exclude(estado="RECHAZADA")
        .values("centro_costo__nombre")
        .annotate(t=Sum("total_pen"))
        .order_by("-t")[:10]
    )
    filas = list(reversed(list(filas)))
    fig = go.Figure(
        go.Bar(
            x=[float(f["t"]) for f in filas],
            y=[f["centro_costo__nombre"][:30] for f in filas],
            orientation="h",
            marker_color=PALETA["secundario"],
        )
    )
    aplicar_tema(fig, "Compras por centro de costo, 90 días (S/)")
    fig.update_xaxes(tickformat=",.0f")
    fig.update_layout(hovermode="closest")
    return Grafico("Compras por proyecto", a_html(fig), 6)


def _estados_orden(ctx: Contexto) -> Grafico:
    cuenta = Counter(ordenes(ctx, ventana=False).values_list("estado", flat=True))
    etiquetas = dict(Orden.Estado.choices)
    fig = go.Figure(
        go.Pie(
            labels=[etiquetas[k] for k in cuenta],
            values=list(cuenta.values()),
            hole=0.55,
            marker=dict(colors=SERIE),
        )
    )
    aplicar_tema(fig, "Órdenes por estado")
    fig.update_layout(hovermode="closest")
    return Grafico("Estados", a_html(fig), 6)


def _tipos_rq(ctx: Contexto) -> Grafico:
    desde = sumar_meses(ctx.mes, -5)
    qs = Requerimiento.objects.filter(
        fecha_creacion__gte=desde, fecha_creacion__lte=ctx.corte
    )
    if ctx.empresa:
        qs = qs.filter(empresa=ctx.empresa)
    if ctx.proyecto:
        qs = qs.filter(centro_costo=ctx.proyecto)
    cuenta = defaultdict(Counter)
    for f, t in qs.values_list("fecha_creacion", "tipo"):
        cuenta[primer_dia(f)][t] += 1
    meses = rango_meses(desde, ctx.mes)
    fig = go.Figure()
    colores = {
        "RUTINARIO": SEMAFORO["ok"],
        "LOGISTICO": PALETA["secundario"],
        "REGULARIZACION": PALETA["acento"],
        "EMERGENCIA": SEMAFORO["critico"],
    }
    for tipo, etiqueta in Requerimiento.Tipo.choices:
        fig.add_bar(
            x=meses,
            y=[cuenta[m][tipo] for m in meses],
            name=etiqueta,
            marker_color=colores[tipo],
        )
    fig.update_layout(barmode="stack")
    aplicar_tema(fig, "RQ por tipo y mes")
    return Grafico("RQ por tipo", a_html(fig), 6)


def _calendario_pagos(ctx: Contexto) -> Grafico:
    semanas = [0.0] * 5
    for fp, total in (
        por_pagar(ctx)
        .filter(
            fecha_programada_pago__gte=ctx.corte,
            fecha_programada_pago__lte=ctx.corte + timedelta(days=34),
        )
        .values_list("fecha_programada_pago", "total_pen")
    ):
        semanas[min((fp - ctx.corte).days // 7, 4)] += float(total)
    etiquetas = [f"Sem {i + 1}" for i in range(5)]
    fig = go.Figure(go.Bar(x=etiquetas, y=semanas, marker_color=PALETA["primario"]))
    aplicar_tema(fig, "Pagos programados por semana (próximos 35 días, S/)")
    fig.update_yaxes(tickformat=",.0f")
    return Grafico("Calendario", a_html(fig), 6)


def _top_proveedores(ctx: Contexto) -> Tabla:
    filas = (
        por_pagar(ctx)
        .values("proveedor__razon_social")
        .annotate(t=Sum("total_pen"))
        .order_by("-t")[:8]
    )
    return Tabla(
        "Mayores deudas por proveedor",
        ["Proveedor", "Por pagar (S/)"],
        [[f["proveedor__razon_social"], f"{float(f['t']):,.0f}"] for f in filas],
        6,
    )


def construir(ctx: Contexto) -> ContenidoArea:
    c = ContenidoArea()
    c.graficos += [
        _embudo(ctx),
        _antiguedad(ctx),
        _compras_proyecto(ctx),
        _estados_orden(ctx),
        _tipos_rq(ctx),
        _calendario_pagos(ctx),
    ]
    c.tablas.append(_top_proveedores(ctx))
    c.notas.append(
        "Los KPI de tiempos y porcentajes usan los últimos 90 días; los de cuentas por pagar reflejan el último estado cargado."
    )
    return c


def para_resumen(ctx: Contexto):
    return [_antiguedad(ctx)]
