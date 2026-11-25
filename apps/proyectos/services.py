"""Cálculo del valor ganado (EVM) por proyecto. Lo usan los KPI, los gráficos y los demás módulos.

Definiciones adoptadas (supuestos a validar con el responsable de Proyectos, preguntas
P-01 a P-04 de docs/parte1/08_preguntas_clave.md). Todo en soles y SIN IGV:

    Contrato sin IGV   = monto_contrato / (1 + IGV)
    BAC de costo       = costo de obra del escenario META (70 %) sin IGV
    PV (planificado)   = % planificado acumulado x BAC
    EV (ganado)        = % real valorizado acumulado x BAC
    AC (costo real)    = gastos REALES y PAGADOS de los componentes de obra (01, 02, 05)
    SPI = EV / PV      CPI = EV / AC      EAC = BAC / CPI
    Margen esperado    = (Contrato sin IGV - EAC) / Contrato sin IGV

El % planificado y el % real se miden con las valorizaciones de los meses ya cerrados
(anteriores al mes del corte), igual que en el libro de Collana (corte 06/11, último mes: octubre).
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from django.conf import settings
from django.db.models import Sum

from apps.core.kpi import Contexto
from apps.core.services import igv, primer_dia

from .models import Gasto, Proyecto, Valorizacion


def proyectos_en_alcance(ctx: Contexto):
    qs = Proyecto.objects.select_related("centro_costo")
    if ctx.proyecto:
        qs = qs.filter(centro_costo=ctx.proyecto)
    if ctx.empresa:
        qs = qs.filter(centro_costo__empresa=ctx.empresa)
    return qs


def gastos_en_alcance(ctx: Contexto):
    qs = Gasto.objects.filter(proyecto__in=proyectos_en_alcance(ctx))
    return qs


def _f(x) -> float:
    return float(x or 0)


@dataclass
class Evm:
    proyecto: Optional[Proyecto]
    contrato_sin_igv: float = 0.0
    bac: float = 0.0
    plan_pct: float = 0.0
    real_pct: float = 0.0
    ac: float = 0.0

    @property
    def pv(self):
        return self.plan_pct * self.bac

    @property
    def ev(self):
        return self.real_pct * self.bac

    @property
    def spi(self) -> Optional[float]:
        return self.ev / self.pv if self.pv else None

    @property
    def cpi(self) -> Optional[float]:
        return self.ev / self.ac if self.ac and self.ev else None

    @property
    def eac(self) -> Optional[float]:
        return self.bac / self.cpi if self.cpi else None

    @property
    def margen_pct(self) -> Optional[float]:
        if self.eac is None or not self.contrato_sin_igv:
            return None
        return (self.contrato_sin_igv - self.eac) / self.contrato_sin_igv * 100


def bac_costo(p: Proyecto) -> float:
    """Costo de obra de la meta (sin IGV); si no hay escenario META se deriva del contrato."""
    meta = p.presupuestos.filter(escenario="META").first()
    if meta:
        return _f(meta.costo_obra_sin_igv)
    return _f(p.monto_contrato) / (1 + igv()) * _f(p.factor_meta)


def evm_proyecto(p: Proyecto, corte) -> Evm:
    cierre = primer_dia(corte)  # solo meses cerrados
    vals = Valorizacion.objects.filter(proyecto=p, periodo__lt=cierre)
    plan = _f(vals.aggregate(s=Sum("monto_planificado"))["s"])
    real = _f(vals.aggregate(s=Sum("monto_real"))["s"])
    contrato = _f(p.monto_contrato)
    ac = _f(
        Gasto.objects.filter(
            proyecto=p,
            naturaleza="REAL",
            estado="PAGADO",
            fecha__lte=corte,
            categoria__componente__in=settings.CUADRO_MANDO["COMPONENTES_OBRA"],
        ).aggregate(s=Sum("monto_pen_sin_igv"))["s"]
    )
    return Evm(
        proyecto=p,
        contrato_sin_igv=contrato / (1 + igv()),
        bac=bac_costo(p),
        plan_pct=plan / contrato if contrato else 0.0,
        real_pct=real / contrato if contrato else 0.0,
        ac=ac,
    )


def evm_cartera(ctx: Contexto) -> list[Evm]:
    """EVM de cada proyecto que ya inició la ejecución de obra a la fecha de corte."""
    lista = []
    for p in proyectos_en_alcance(ctx):
        if p.fecha_acta_eo and p.fecha_acta_eo <= ctx.corte:
            lista.append(evm_proyecto(p, ctx.corte))
    return lista


def evm_total(lista: list[Evm]) -> Evm:
    """Agrega varios proyectos sumando montos (no promediando índices)."""
    total = Evm(proyecto=None)
    ev = pv = 0.0
    for e in lista:
        total.contrato_sin_igv += e.contrato_sin_igv
        total.bac += e.bac
        total.ac += e.ac
        ev += e.ev
        pv += e.pv
    if total.bac:
        total.real_pct = ev / total.bac
        total.plan_pct = pv / total.bac
    return total


def valorizacion_real_periodo(ctx: Contexto, periodo) -> float:
    """Valorizado real (sin IGV) de un mes para los proyectos del alcance. Lo usa RR. HH. (H5)."""
    s = Valorizacion.objects.filter(
        proyecto__in=proyectos_en_alcance(ctx), periodo=periodo
    ).aggregate(s=Sum("monto_real"))["s"]
    return _f(s) / (1 + igv())
