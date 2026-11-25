"""Pantallas web: resumen, una pestaña por área, diccionario de KPI y carga manual de archivos."""

import io

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import connection
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render

import plotly.graph_objects as go

from . import importers, kpi
from .dashboard import AREAS, areas_visibles, puede_ver
from .filtros import contexto_desde_request, parametros_url
from .models import CargaArchivo, CentroCosto, Empresa, KPIConfig, KPISnapshot
from .theme import PALETA, a_html, aplicar_tema


def _base(request, ctx, activa=""):
    """Datos comunes de todas las pantallas: filtros globales y menú."""
    return {
        "ctx": ctx,
        "activa": activa,
        "qs": parametros_url(ctx),
        "empresas": Empresa.objects.filter(activa=True),
        "proyectos": CentroCosto.objects.filter(tipo="PROYECTO", activo=True),
        "mostrar_filtros": True,
    }


@login_required
def resumen(request):
    ctx = contexto_desde_request(request)
    visibles = {a.slug: a for a in areas_visibles(request.user)}
    configs = kpi._configuraciones()
    todos = [
        kpi.calcular(c, ctx, configs)
        for c, d in kpi.REGISTRO.items()
        if d.area in visibles
    ]
    destacados = sorted(
        [r for r in todos if r.definicion.resumen],
        key=lambda r: (r.definicion.area, r.definicion.codigo),
    )
    por_area = {}
    for r in destacados:
        por_area.setdefault(r.definicion.area, []).append(r)
    alertas = sorted(
        [r for r in todos if r.estado in ("alerta", "critico", "error")],
        key=lambda r: (r.estado != "critico", r.definicion.area, r.definicion.codigo),
    )
    graficos = []
    for slug, area in visibles.items():
        if area.grafico_resumen:
            graficos += area.grafico_resumen(ctx)
    conteo = {
        e: sum(1 for r in todos if r.estado == e)
        for e in ("ok", "alerta", "critico", "sin_datos")
    }
    contexto = _base(request, ctx, "resumen") | {
        "grupos": [(a, por_area[s]) for s, a in visibles.items() if s in por_area],
        "alertas": alertas[:10],
        "total_alertas": len(alertas),
        "graficos": graficos,
        "conteo": conteo,
        "total_kpi": len(todos),
    }
    return render(request, "dashboard/resumen.html", contexto)


@login_required
def area(request, slug):
    if slug not in AREAS:
        raise Http404
    if not puede_ver(request.user, slug):
        raise PermissionDenied
    ctx = contexto_desde_request(request)
    definicion = AREAS[slug]
    contenido = definicion.construir(ctx)
    contexto = _base(request, ctx, slug) | {
        "area": definicion,
        "resultados": kpi.calcular_area(slug, ctx),
        "contenido": contenido,
    }
    return render(request, "dashboard/area.html", contexto)


@login_required
def diccionario(request):
    """Todos los KPI con definición, fórmula, fuente y umbrales vigentes (se genera desde el registro)."""
    ctx = contexto_desde_request(request)
    configs = kpi._configuraciones()
    visibles = {a.slug: a for a in areas_visibles(request.user)}
    grupos = []
    for slug, a in visibles.items():
        filas = []
        for d in sorted(
            (d for d in kpi.REGISTRO.values() if d.area == slug),
            key=lambda d: kpi._orden(d.codigo),
        ):
            cfg = configs.get(d.codigo)
            filas.append(
                {
                    "d": d,
                    "alerta": (
                        cfg.umbral_alerta
                        if cfg and cfg.umbral_alerta is not None
                        else d.umbral_alerta
                    ),
                    "critico": (
                        cfg.umbral_critico
                        if cfg and cfg.umbral_critico is not None
                        else d.umbral_critico
                    ),
                }
            )
        grupos.append((a, filas))
    return render(
        request,
        "dashboard/diccionario.html",
        _base(request, ctx, "diccionario")
        | {"grupos": grupos, "mostrar_filtros": False},
    )


@login_required
def kpi_detalle(request, codigo):
    if codigo not in kpi.REGISTRO:
        raise Http404
    d = kpi.REGISTRO[codigo]
    if not puede_ver(request.user, d.area):
        raise PermissionDenied
    ctx = contexto_desde_request(request)
    resultado = kpi.calcular(codigo, ctx)
    serie = KPISnapshot.objects.filter(
        codigo=codigo, empresa=None, centro_costo=None
    ).order_by("fecha_corte")
    grafico = None
    if serie.count() >= 2:
        fig = go.Figure(
            go.Scatter(
                x=[s.fecha_corte for s in serie],
                y=[s.valor for s in serie],
                mode="lines+markers",
                line=dict(color=PALETA["primario"], width=3),
            )
        )
        aplicar_tema(fig, f"Evolución de {d.codigo} - {d.nombre}", alto=320)
        grafico = a_html(fig)
    return render(
        request,
        "dashboard/kpi_detalle.html",
        _base(request, ctx, d.area) | {"r": resultado, "d": d, "grafico": grafico},
    )


def _importadores_permitidos(usuario):
    importers.descubrir()
    visibles = {a.slug for a in areas_visibles(usuario)}
    total = usuario.is_superuser or usuario.groups.filter(name="gerencia").exists()
    return {
        s: i for s, i in importers.IMPORTADORES.items() if total or i.area in visibles
    }


@login_required
def cargas(request):
    """Carga manual: se elige la tabla, se sube el archivo y se valida antes de guardar."""
    ctx = contexto_desde_request(request)
    permitidos = _importadores_permitidos(request.user)
    resultado = None
    if request.method == "POST":
        imp = permitidos.get(request.POST.get("tabla"))
        archivo = request.FILES.get("archivo")
        if not imp or not archivo:
            resultado = {"error": "Elija una tabla y un archivo."}
        else:
            try:
                df = importers.leer_archivo(archivo, archivo.name)
                resultado = {
                    "carga": importers.procesar(
                        imp,
                        df,
                        request.user,
                        archivo.name,
                        guardar=not request.POST.get("solo_validar"),
                    )
                }
            except (
                Exception
            ) as e:  # noqa: BLE001 - archivo ilegible: se informa al usuario
                resultado = {"error": f"No se pudo leer el archivo: {e}"}
    historial = CargaArchivo.objects.filter(tabla__in=permitidos.keys())[:10]
    return render(
        request,
        "dashboard/cargas.html",
        _base(request, ctx, "cargas")
        | {
            "importadores": sorted(permitidos.values(), key=lambda i: (i.area, i.slug)),
            "resultado": resultado,
            "historial": historial,
            "mostrar_filtros": False,
        },
    )


@login_required
def plantilla_csv(request, slug):
    imp = _importadores_permitidos(request.user).get(slug)
    if not imp:
        raise Http404
    salida = io.StringIO()
    importers.plantilla(imp).to_csv(salida, index=False)
    respuesta = HttpResponse(
        "\ufeff" + salida.getvalue(), content_type="text/csv; charset=utf-8"
    )
    respuesta["Content-Disposition"] = f'attachment; filename="plantilla_{slug}.csv"'
    return respuesta


def salud(request):
    """Punto de verificación para Railway: responde 200 si la aplicación y la base de datos funcionan."""
    with connection.cursor() as c:
        c.execute("select 1")
    return JsonResponse({"estado": "ok"})
