"""Filtros globales de las pantallas (fecha de corte, empresa, proyecto) y su lectura desde la URL."""

from datetime import date, datetime

from .kpi import Contexto
from .models import CentroCosto, Empresa


def contexto_desde_request(request) -> Contexto:
    """Lee ?corte=AAAA-MM-DD&empresa=<ruc>&proyecto=<cc2>&personal=0|1; los valores inválidos se ignoran."""
    q = request.GET
    corte = ultima_fecha_corte()
    if q.get("corte"):
        try:
            corte = datetime.strptime(q["corte"], "%Y-%m-%d").date()
        except ValueError:
            pass
    empresa = (
        Empresa.objects.filter(ruc=q["empresa"]).first() if q.get("empresa") else None
    )
    proyecto = (
        CentroCosto.objects.filter(cc2=q["proyecto"]).first()
        if q.get("proyecto")
        else None
    )
    return Contexto(
        corte=corte,
        empresa=empresa,
        proyecto=proyecto,
        incluir_personal=q.get("personal", "1") != "0",
    )


def ultima_fecha_corte() -> date:
    """Fecha de corte por defecto: la del último cálculo guardado (última actualización); si no hay, hoy."""
    from .models import KPISnapshot

    ultimo = (
        KPISnapshot.objects.order_by("-fecha_corte")
        .values_list("fecha_corte", flat=True)
        .first()
    )
    return ultimo or date.today()


def parametros_url(ctx: Contexto) -> str:
    partes = [f"corte={ctx.corte:%Y-%m-%d}"]
    if ctx.empresa:
        partes.append(f"empresa={ctx.empresa.ruc}")
    if ctx.proyecto:
        partes.append(f"proyecto={ctx.proyecto.cc2}")
    if not ctx.incluir_personal:
        partes.append("personal=0")
    return "&".join(partes)
