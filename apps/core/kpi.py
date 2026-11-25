"""
Motor de KPI: cómo se define, registra, calcula y evalúa un indicador.

Para añadir un KPI basta con escribir una función y decorarla con `@kpi(...)`:

    @kpi(codigo="X1", area="logistica", nombre="Mi indicador", unidad="pct",
         direccion="menor", umbral_alerta=10, umbral_critico=20,
         formula="a / b", fuente="tabla x", frecuencia="S", prioridad="A")
    def mi_indicador(ctx: Contexto) -> Valor:
        return Valor(12.5, nota="3 de 24 casos")

El decorador lo deja en `REGISTRO`; las pantallas, la API y el diccionario de KPI
(`docs/parte2/diccionario_kpi.md`) se construyen leyendo ese registro, sin código extra.

Convenciones de unidades (campo `unidad`):
    pen   soles (S/)          pct  porcentaje 0-100        ratio  número sin unidad (p. ej. CPI)
    dias  días                n    conteo
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date
from typing import Callable, Optional

log = logging.getLogger(__name__)

ESTADOS = ("ok", "alerta", "critico", "neutro", "sin_datos", "error")


@dataclass(frozen=True)
class Contexto:
    """Alcance del cálculo: hasta qué fecha, y para qué empresa / centro de costo (o todos)."""

    corte: date
    empresa: Optional[object] = None  # core.Empresa
    proyecto: Optional[object] = None  # core.CentroCosto
    incluir_personal: bool = (
        True  # préstamos personales del gerente (pregunta G-03 pendiente)
    )

    @property
    def mes(self) -> date:
        return self.corte.replace(day=1)


@dataclass
class Valor:
    """Lo que devuelve la función de un KPI. `valor=None` significa 'sin datos'."""

    valor: Optional[float]
    nota: str = ""


@dataclass(frozen=True)
class DefinicionKPI:
    codigo: str
    area: str
    nombre: str
    unidad: str
    direccion: str  # "mayor" (más es mejor), "menor" (menos es mejor) o "ninguna"
    umbral_alerta: Optional[float]
    umbral_critico: Optional[float]
    formula: str
    fuente: str
    frecuencia: str  # S semanal, M mensual
    prioridad: str  # A, B, C (ver docs/parte1/06_propuesta_kpi.md)
    descripcion: str
    resumen: bool
    funcion: Callable[[Contexto], Valor]


@dataclass
class Resultado:
    definicion: DefinicionKPI
    valor: Optional[float]
    nota: str
    estado: str
    meta: Optional[float] = None


REGISTRO: dict[str, DefinicionKPI] = {}


def kpi(
    *,
    codigo,
    area,
    nombre,
    unidad,
    direccion="ninguna",
    umbral_alerta=None,
    umbral_critico=None,
    formula="",
    fuente="",
    frecuencia="M",
    prioridad="A",
    descripcion="",
    resumen=False,
):
    """Decorador que registra una función como KPI."""

    def registrar(funcion):
        if codigo in REGISTRO:
            raise ValueError(f"KPI duplicado: {codigo}")
        REGISTRO[codigo] = DefinicionKPI(
            codigo,
            area,
            nombre,
            unidad,
            direccion,
            umbral_alerta,
            umbral_critico,
            formula,
            fuente,
            frecuencia,
            prioridad,
            descripcion or (funcion.__doc__ or "").strip(),
            resumen,
            funcion,
        )
        return funcion

    return registrar


def evaluar(
    definicion: DefinicionKPI, valor: Optional[float], alerta=None, critico=None
) -> str:
    """Convierte un valor en semáforo según la dirección y los umbrales."""
    if valor is None:
        return "sin_datos"
    alerta = definicion.umbral_alerta if alerta is None else alerta
    critico = definicion.umbral_critico if critico is None else critico
    if definicion.direccion == "ninguna" or alerta is None or critico is None:
        return "neutro"
    if definicion.direccion == "mayor":
        return "ok" if valor >= alerta else "alerta" if valor >= critico else "critico"
    return "ok" if valor <= alerta else "alerta" if valor <= critico else "critico"


def _configuraciones() -> dict:
    from .models import KPIConfig

    return {c.codigo: c for c in KPIConfig.objects.filter(activo=True)}


def calcular(codigo: str, ctx: Contexto, configs: Optional[dict] = None) -> Resultado:
    """Calcula un KPI. Un fallo en un KPI no tumba la pantalla: se informa como estado 'error'."""
    definicion = REGISTRO[codigo]
    configs = _configuraciones() if configs is None else configs
    cfg = configs.get(codigo)
    try:
        resultado = definicion.funcion(ctx)
    except (
        Exception
    ):  # noqa: BLE001 - se registra y se muestra como error en la tarjeta
        log.exception("Error calculando KPI %s", codigo)
        return Resultado(definicion, None, "Error de cálculo (ver registro)", "error")
    estado = evaluar(
        definicion,
        resultado.valor,
        cfg.umbral_alerta if cfg else None,
        cfg.umbral_critico if cfg else None,
    )
    return Resultado(
        definicion, resultado.valor, resultado.nota, estado, cfg.meta if cfg else None
    )


def calcular_area(
    area: str, ctx: Contexto, solo_resumen: bool = False
) -> list[Resultado]:
    configs = _configuraciones()
    codigos = [
        c
        for c, d in REGISTRO.items()
        if d.area == area and (d.resumen or not solo_resumen)
    ]
    return [calcular(c, ctx, configs) for c in sorted(codigos, key=_orden)]


def calcular_resumen(ctx: Contexto) -> list[Resultado]:
    """KPI marcados con `resumen=True`, de todas las áreas."""
    configs = _configuraciones()
    codigos = [c for c, d in REGISTRO.items() if d.resumen]
    return [calcular(c, ctx, configs) for c in sorted(codigos, key=_orden)]


def _orden(codigo: str):
    d = REGISTRO[codigo]
    return (
        d.area,
        d.codigo[0],
        int("".join(ch for ch in d.codigo if ch.isdigit()) or 0),
    )


def formatear(valor: Optional[float], unidad: str) -> str:
    """Texto para mostrar en pantalla (formato peruano: coma de miles, punto decimal)."""
    if valor is None:
        return "—"
    if unidad == "pen":
        if abs(valor) >= 1_000_000:
            return f"S/ {valor / 1_000_000:,.2f} M"
        return f"S/ {valor:,.0f}"
    if unidad == "pct":
        return f"{valor:,.1f} %"
    if unidad == "ratio":
        return f"{valor:,.2f}"
    if unidad == "dias":
        return f"{valor:,.1f} d"
    if unidad == "n":
        return f"{valor:,.0f}"
    return f"{valor:,.2f}"
