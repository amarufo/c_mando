"""Pestaña de calidad de datos: qué se cargó, cuándo y con qué errores. Es genérica: no conoce las áreas."""

from django.apps import apps as django_apps

import plotly.graph_objects as go

from .dashboard import ContenidoArea, Grafico, Tabla
from .kpi import Contexto
from .models import CargaArchivo
from .theme import SEMAFORO, a_html, aplicar_tema

APPS_DE_AREA_EXCLUIDAS = {"core"}


def _inventario() -> Tabla:
    """Filas por tabla de cada área (recorre los modelos registrados, sin importar las apps de área)."""
    filas = []
    from .dashboard import AREAS

    for slug in AREAS:
        try:
            config = django_apps.get_app_config(slug)
        except LookupError:
            continue
        for modelo in config.get_models():
            filas.append(
                [
                    config.verbose_name,
                    modelo._meta.verbose_name.capitalize(),
                    f"{modelo.objects.count():,}",
                ]
            )
    return Tabla("Registros cargados por tabla", ["Área", "Tabla", "Filas"], filas, 5)


def _cargas_recientes() -> Tabla:
    filas = []
    for c in CargaArchivo.objects.order_by("-fecha")[:12]:
        estado = {
            "OK": ("Cargado", "ok"),
            "RECHAZADA": ("Rechazado", "critico"),
            "SIMULACION": ("Solo validación", "neutro"),
        }[c.estado]
        filas.append(
            [
                f"{c.fecha:%d/%m %H:%M}",
                c.tabla,
                f"{c.filas_ok}/{c.filas_leidas}",
                estado,
            ]
        )
    return Tabla(
        "Últimas cargas", ["Fecha", "Tabla", "Filas válidas", "Estado"], filas, 7
    )


def _grafico_estados() -> Grafico:
    cuenta = {"Cargado": 0, "Rechazado": 0, "Solo validación": 0}
    for e in CargaArchivo.objects.values_list("estado", flat=True):
        cuenta[
            {
                "OK": "Cargado",
                "RECHAZADA": "Rechazado",
                "SIMULACION": "Solo validación",
            }[e]
        ] += 1
    fig = go.Figure(
        go.Bar(
            x=list(cuenta),
            y=list(cuenta.values()),
            marker_color=[SEMAFORO["ok"], SEMAFORO["critico"], SEMAFORO["neutro"]],
        )
    )
    aplicar_tema(fig, "Cargas por resultado", alto=260)
    return Grafico("Cargas", a_html(fig), 5)


def construir(ctx: Contexto) -> ContenidoArea:
    c = ContenidoArea()
    c.graficos.append(_grafico_estados())
    c.tablas += [_cargas_recientes(), _inventario()]
    c.notas.append(
        "Los archivos se cargan en la sección 'Cargar datos'. Cada carga queda registrada aquí con sus errores."
    )
    return c
