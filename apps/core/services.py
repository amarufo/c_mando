"""Utilidades numéricas y de fechas compartidas por los cálculos de todas las áreas."""

from bisect import bisect_right
from datetime import date, timedelta
from decimal import Decimal

from django.conf import settings

TC_POR_DEFECTO = Decimal("3.5")


def igv() -> float:
    return settings.CUADRO_MANDO["IGV"]


def a_soles(monto, moneda: str, tc) -> Decimal:
    """Convierte un importe a soles. `tc` es el tipo de cambio aplicado al movimiento."""
    monto = Decimal(monto or 0)
    return (
        monto
        if moneda == "PEN"
        else (monto * Decimal(tc or TC_POR_DEFECTO)).quantize(Decimal("0.01"))
    )


def sin_igv(monto, con_igv: bool) -> Decimal:
    monto = Decimal(monto or 0)
    return (monto / Decimal(1 + igv())).quantize(Decimal("0.01")) if con_igv else monto


def primer_dia(d: date) -> date:
    return d.replace(day=1)


def sumar_meses(d: date, n: int) -> date:
    """Primer día del mes `n` meses después de `d` (n puede ser negativo)."""
    indice = d.year * 12 + (d.month - 1) + n
    return date(indice // 12, indice % 12 + 1, 1)


def fin_de_mes(d: date) -> date:
    return sumar_meses(d, 1) - timedelta(days=1)


def rango_meses(desde: date, hasta: date) -> list[date]:
    """Lista de primeros días de mes desde `desde` hasta `hasta` (ambos incluidos)."""
    meses, actual = [], primer_dia(desde)
    while actual <= hasta:
        meses.append(actual)
        actual = sumar_meses(actual, 1)
    return meses


class ConversorMoneda:
    """Tipo de cambio de venta vigente a una fecha (el último registrado hasta ese día)."""

    def __init__(self):
        from .models import TipoCambio

        filas = list(TipoCambio.objects.order_by("fecha").values_list("fecha", "venta"))
        self._fechas = [f for f, _ in filas]
        self._tc = [v for _, v in filas]

    def tc(self, fecha: date) -> Decimal:
        if not self._fechas:
            return TC_POR_DEFECTO
        i = bisect_right(self._fechas, fecha) - 1
        return self._tc[max(i, 0)]

    def a_soles(self, monto, moneda: str, fecha: date) -> Decimal:
        return a_soles(monto, moneda, self.tc(fecha))


def tc_efectivo(moneda: str, tc, fecha: date) -> Decimal:
    """TC a aplicar a un movimiento: el informado, o el de la tabla TipoCambio si es en dólares y no se informó."""
    if moneda == "USD" and (not tc or Decimal(tc) == 1):
        return ConversorMoneda().tc(fecha)
    return Decimal(tc or 1)


def porcentaje(parte, total):
    """parte/total en 0-100; `None` si el total es 0 (así el KPI se muestra 'sin datos')."""
    return None if not total else float(parte) / float(total) * 100.0
