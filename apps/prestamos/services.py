"""Carga de cuotas ya convertidas a soles. Base común de los KPI y gráficos de Préstamos.

Convención: una cuota está pagada si los pagos registrados hasta la fecha de corte cubren
su total (con 1 sol de tolerancia). Los importes en dólares se convierten con el tipo de
cambio vigente a la fecha de corte (los archivos actuales usan un único TC; ver F-09).
"""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from django.db.models import DecimalField, Q, Sum, Value
from django.db.models.functions import Coalesce

from apps.core.kpi import Contexto
from apps.core.services import ConversorMoneda

from .models import Cuota


@dataclass
class CuotaCalc:
    prestamo: str
    acreedor: str
    tipo: str
    deudor: str
    es_personal: bool
    en_dolares: bool
    vencimiento: date
    interes: float
    capital: float
    otros: float
    total: float
    pagada: bool

    @property
    def costo_financiero(self) -> float:
        return self.interes + self.otros


def cuotas(ctx: Contexto) -> list[CuotaCalc]:
    qs = Cuota.objects.filter(prestamo__activo=True).select_related(
        "prestamo", "prestamo__deudor"
    )
    if ctx.empresa:
        qs = qs.filter(prestamo__deudor=ctx.empresa)
    if not ctx.incluir_personal:
        qs = qs.filter(prestamo__es_personal=False)
    qs = qs.annotate(
        pagado=Coalesce(
            Sum("pagos__monto_pagado", filter=Q(pagos__fecha_pago__lte=ctx.corte)),
            Value(Decimal("0")),
            output_field=DecimalField(),
        )
    )
    tc = float(ConversorMoneda().tc(ctx.corte))
    resultado = []
    for c in qs:
        k = tc if c.prestamo.moneda == "USD" else 1.0
        resultado.append(
            CuotaCalc(
                prestamo=c.prestamo.codigo,
                acreedor=c.prestamo.acreedor,
                tipo=c.prestamo.tipo,
                deudor=(
                    "Personal (gerente)"
                    if c.prestamo.es_personal
                    else (c.prestamo.deudor.nombre_corto if c.prestamo.deudor else "—")
                ),
                es_personal=c.prestamo.es_personal,
                en_dolares=c.prestamo.moneda == "USD",
                vencimiento=c.fecha_vencimiento,
                interes=float(c.interes) * k,
                capital=float(c.capital) * k,
                otros=float(c.otros_costos) * k,
                total=float(c.total_cuota) * k,
                pagada=float(c.pagado) >= float(c.total_cuota) - 1,
            )
        )
    return resultado
