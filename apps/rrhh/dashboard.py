"""Pantalla de Recursos Humanos. Solo agregados: nunca se muestran nombres, DNI ni sueldos individuales."""

from collections import Counter, defaultdict
from datetime import datetime, time, timedelta

import plotly.graph_objects as go
from django.conf import settings
from django.db.models import Sum
from django.utils import timezone

from apps.core.dashboard import ContenidoArea, Grafico, Tabla
from apps.core.kpi import Contexto
from apps.core.services import rango_meses, sumar_meses
from apps.core.theme import PALETA, SERIE, a_html, aplicar_tema

from .kpis import VENTANA_ASISTENCIA, costos_periodo, personas_activas
from .models import CostoProyectoMes, Marcacion, Obligacion, Persona

ETIQ_CATEGORIA = dict(Persona.Categoria.choices)


def _dotacion(ctx: Contexto) -> Grafico:
    cuenta = Counter(personas_activas(ctx).values_list("categoria", "condicion"))
    categorias = list(ETIQ_CATEGORIA)
    fig = go.Figure()
    for cond, color in (("PLANILLA", PALETA["primario"]), ("RXH", PALETA["acento"])):
        fig.add_bar(
            x=[ETIQ_CATEGORIA[c] for c in categorias],
            y=[cuenta[(c, cond)] for c in categorias],
            name="Planilla" if cond == "PLANILLA" else "Recibo por honorarios",
            marker_color=color,
        )
    fig.update_layout(barmode="group")
    aplicar_tema(fig, "Dotación por categoría y condición")
    return Grafico("Dotación", a_html(fig), 6)


def _costo_por_proyecto(ctx: Contexto) -> Grafico:
    qs, periodo = costos_periodo(ctx)
    filas = qs.values("centro_costo__nombre", "categoria").annotate(
        t=Sum("sueldo_bruto")
    )
    por = defaultdict(lambda: defaultdict(float))
    for f in filas:
        por[f["centro_costo__nombre"]][f["categoria"]] += float(f["t"])
    orden = sorted(por, key=lambda k: sum(por[k].values()))[-10:]
    fig = go.Figure()
    for i, cat in enumerate(ETIQ_CATEGORIA):
        fig.add_bar(
            y=[n[:28] for n in orden],
            x=[por[n].get(cat, 0) for n in orden],
            name=ETIQ_CATEGORIA[cat],
            orientation="h",
            marker_color=SERIE[i],
        )
    fig.update_layout(barmode="stack", hovermode="closest")
    aplicar_tema(
        fig,
        (
            f"Costo bruto por centro de costo y categoría, {periodo:%m/%Y}"
            if periodo
            else "Costo bruto por centro de costo"
        ),
    )
    fig.update_xaxes(tickformat=",.0f")
    return Grafico("Costo por proyecto", a_html(fig), 6)


def _tendencia_costo(ctx: Contexto) -> Grafico:
    desde = sumar_meses(ctx.mes, -8)
    qs = CostoProyectoMes.objects.filter(periodo__gte=desde, periodo__lte=ctx.mes)
    if ctx.empresa:
        qs = qs.filter(empresa=ctx.empresa)
    if ctx.proyecto:
        qs = qs.filter(centro_costo=ctx.proyecto)
    acum = defaultdict(lambda: defaultdict(float))
    for f in qs.values("periodo", "condicion").annotate(t=Sum("sueldo_bruto")):
        acum[f["periodo"]][f["condicion"]] += float(f["t"])
    meses = rango_meses(desde, ctx.mes)
    fig = go.Figure()
    fig.add_bar(
        x=meses,
        y=[acum[m]["PLANILLA"] for m in meses],
        name="Planilla",
        marker_color=PALETA["primario"],
    )
    fig.add_bar(
        x=meses,
        y=[acum[m]["RXH"] for m in meses],
        name="Recibos por honorarios",
        marker_color=PALETA["acento"],
    )
    fig.update_layout(barmode="stack")
    aplicar_tema(fig, "Costo bruto mensual de personal (S/)")
    fig.update_yaxes(tickformat=",.0f")
    return Grafico("Tendencia", a_html(fig), 6)


def _tardanzas_dia(ctx: Contexto) -> Grafico:
    desde = ctx.corte - timedelta(days=VENTANA_ASISTENCIA)
    marcas = Marcacion.objects.filter(
        fecha_hora__range=(
            timezone.make_aware(datetime.combine(desde, time.min)),
            timezone.make_aware(datetime.combine(ctx.corte, time.max)),
        )
    ).exclude(persona=None)
    if ctx.empresa:
        marcas = marcas.filter(persona__empresa=ctx.empresa)
    if ctx.proyecto:
        marcas = marcas.filter(persona__centro_costo=ctx.proyecto)
    primera = {}
    for pid, fh in marcas.values_list("persona_id", "fecha_hora"):
        loc = timezone.localtime(fh)
        k = (pid, loc.date())
        primera[k] = min(primera.get(k, loc), loc)
    h, m = map(int, settings.CUADRO_MANDO["HORA_ENTRADA"].split(":"))
    tol = timedelta(minutes=settings.CUADRO_MANDO["TOLERANCIA_MINUTOS"])
    total, tarde = Counter(), Counter()
    for (_, d), t in primera.items():
        total[d] += 1
        if t > timezone.make_aware(datetime.combine(d, time(h, m))) + tol:
            tarde[d] += 1
    dias = sorted(total)
    fig = go.Figure(
        go.Bar(
            x=dias,
            y=[tarde[d] / total[d] * 100 for d in dias],
            marker_color=PALETA["acento"],
        )
    )
    aplicar_tema(fig, "Tardanzas por día (% del personal con marca)")
    fig.update_yaxes(ticksuffix=" %")
    return Grafico("Tardanzas", a_html(fig), 6)


def _tabla_obligaciones(ctx: Contexto) -> Tabla:
    filas = []
    for o in Obligacion.objects.filter(
        fecha_limite__lte=ctx.corte + timedelta(days=15)
    ).order_by("-fecha_limite")[:9]:
        if o.fecha_entrega is None:
            estado = (
                "Pendiente",
                "critico" if o.fecha_limite < ctx.corte else "alerta",
            )
        else:
            estado = (
                ("A tiempo", "ok")
                if o.fecha_entrega <= o.fecha_limite
                else ("Con retraso", "alerta")
            )
        filas.append(
            [
                f"{o.periodo:%m/%Y}",
                o.get_tipo_display(),
                f"{o.fecha_limite:%d/%m/%Y}",
                estado,
            ]
        )
    return Tabla(
        "Obligaciones mensuales",
        ["Periodo", "Obligación", "Fecha límite", "Estado"],
        filas,
        6,
    )


def _tabla_contratos(ctx: Contexto) -> Tabla:
    """Sin nombres: cargo, proyecto y fecha, para que RR. HH. identifique el caso en su archivo."""
    qs = personas_activas(ctx).select_related("centro_costo")
    filas = []
    for p in qs.filter(estado_contrato="ELABORAR").order_by("fecha_ingreso")[:6]:
        filas.append(
            [
                p.cargo,
                p.centro_costo.nombre[:26] if p.centro_costo else "—",
                "—",
                ("Por elaborar", "alerta"),
            ]
        )
    for p in qs.filter(
        fecha_fin_contrato__gte=ctx.corte,
        fecha_fin_contrato__lte=ctx.corte + timedelta(days=30),
    ).order_by("fecha_fin_contrato")[:6]:
        filas.append(
            [
                p.cargo,
                p.centro_costo.nombre[:26] if p.centro_costo else "—",
                f"{p.fecha_fin_contrato:%d/%m/%Y}",
                ("Por vencer", "critico"),
            ]
        )
    return Tabla(
        "Contratos por firmar o vencer",
        ["Cargo", "Centro de costo", "Fin de contrato", "Estado"],
        filas,
        6,
    )


def construir(ctx: Contexto) -> ContenidoArea:
    c = ContenidoArea()
    c.graficos += [
        _dotacion(ctx),
        _costo_por_proyecto(ctx),
        _tendencia_costo(ctx),
        _tardanzas_dia(ctx),
    ]
    c.tablas += [_tabla_obligaciones(ctx), _tabla_contratos(ctx)]
    c.notas.append(
        "Pantalla agregada: no muestra nombres, DNI ni remuneraciones individuales. Los datos del ejemplo son simulados."
    )
    return c


def para_resumen(ctx: Contexto):
    return [_tendencia_costo(ctx)]
