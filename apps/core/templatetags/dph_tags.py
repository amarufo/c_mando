"""Filtros y componentes de plantilla para mostrar KPI con la paleta del cuadro de mando."""

from django import template

from apps.core.kpi import formatear

register = template.Library()

ETIQUETAS = {
    "ok": "En meta",
    "alerta": "Atención",
    "critico": "Crítico",
    "neutro": "Informativo",
    "sin_datos": "Sin datos",
    "error": "Error",
}


@register.filter
def valor_kpi(resultado):
    return formatear(resultado.valor, resultado.definicion.unidad)


@register.filter
def etiqueta_estado(estado):
    return ETIQUETAS.get(estado, estado)


@register.filter
def formato_umbral(valor, unidad):
    return "—" if valor is None else formatear(valor, unidad)


@register.filter
def celda_texto(celda):
    return celda[0] if isinstance(celda, tuple) else celda


@register.filter
def celda_estado(celda):
    return celda[1] if isinstance(celda, tuple) else ""


@register.inclusion_tag("dashboard/_kpi_card.html")
def kpi_card(resultado, qs=""):
    return {"r": resultado, "qs": qs}


@register.simple_tag
def url_con_filtros(nombre_url, qs, *args):
    """Construye una URL conservando los filtros globales (?corte=...&empresa=...)."""
    from django.urls import reverse

    base = reverse(nombre_url, args=args)
    return f"{base}?{qs}" if qs else base
