"""API REST v1: consulta de KPI y carga automática de archivos limpios.

Es la puerta para escalar: cuando una oficina tenga su archivo o sistema listo, un script
programado hace `POST /api/v1/cargas/<tabla>/` con el mismo archivo que hoy se sube a mano.
Autenticación: cabecera `Authorization: Token <token>` (ver comando `crear_token`).
"""

import pandas as pd
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.response import Response

from . import importers, kpi
from .dashboard import areas_visibles
from .filtros import contexto_desde_request
from .models import KPISnapshot


@api_view(["GET"])
def lista_kpi(request):
    """KPI de las áreas a las que el usuario tiene acceso. Filtros: ?corte=&empresa=&proyecto="""
    ctx = contexto_desde_request(request)
    visibles = {a.slug for a in areas_visibles(request.user)}
    configs = kpi._configuraciones()
    datos = []
    for codigo, d in sorted(
        kpi.REGISTRO.items(), key=lambda kv: (kv[1].area, kpi._orden(kv[0]))
    ):
        if d.area not in visibles:
            continue
        r = kpi.calcular(codigo, ctx, configs)
        datos.append(
            {
                "codigo": codigo,
                "area": d.area,
                "nombre": d.nombre,
                "unidad": d.unidad,
                "valor": r.valor,
                "estado": r.estado,
                "nota": r.nota,
                "formula": d.formula,
            }
        )
    return Response({"corte": ctx.corte, "kpi": datos})


@api_view(["GET"])
def historial_kpi(request, codigo):
    if codigo not in kpi.REGISTRO or kpi.REGISTRO[codigo].area not in {
        a.slug for a in areas_visibles(request.user)
    }:
        return Response(
            {"detalle": "KPI no encontrado."}, status=status.HTTP_404_NOT_FOUND
        )
    serie = KPISnapshot.objects.filter(
        codigo=codigo, empresa=None, centro_costo=None
    ).order_by("fecha_corte")
    return Response(
        {
            "codigo": codigo,
            "serie": [
                {"corte": s.fecha_corte, "valor": s.valor, "estado": s.estado}
                for s in serie
            ],
        }
    )


@api_view(["POST"])
@parser_classes([MultiPartParser, JSONParser])
def cargar(request, tabla):
    """Carga un archivo (campo `archivo`, CSV o Excel) o filas JSON (`{"filas": [...]}`). `?validar=1` solo valida."""
    importers.descubrir()
    imp = importers.IMPORTADORES.get(tabla)
    if imp is None:
        return Response(
            {"detalle": f"Tabla desconocida: {tabla}"}, status=status.HTTP_404_NOT_FOUND
        )
    permitidos = {a.slug for a in areas_visibles(request.user)}
    if not (
        request.user.is_superuser
        or request.user.groups.filter(name="gerencia").exists()
        or imp.area in permitidos
    ):
        return Response(
            {"detalle": "Sin permiso para cargar esta tabla."},
            status=status.HTTP_403_FORBIDDEN,
        )
    try:
        if "archivo" in request.FILES:
            nombre = request.FILES["archivo"].name
            df = importers.leer_archivo(request.FILES["archivo"], nombre)
        else:
            nombre = "api.json"
            df = pd.DataFrame(request.data.get("filas", []))
    except Exception as e:  # noqa: BLE001
        return Response(
            {"detalle": f"No se pudo leer el archivo: {e}"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    carga = importers.procesar(
        imp,
        df,
        request.user,
        nombre,
        guardar=request.query_params.get("validar") != "1",
    )
    cuerpo = {
        "estado": carga.estado,
        "filas_leidas": carga.filas_leidas,
        "filas_ok": carga.filas_ok,
        "filas_error": carga.filas_error,
        "errores": carga.errores,
    }
    return Response(
        cuerpo,
        status=(
            status.HTTP_422_UNPROCESSABLE_ENTITY
            if carga.estado == "RECHAZADA"
            else status.HTTP_201_CREATED
        ),
    )
