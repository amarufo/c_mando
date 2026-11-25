"""Registro de pantallas por área y control de acceso.

Cada app de área llama a `registrar_area(...)` en su `AppConfig.ready()`. Con eso aparece
sola una pestaña en el menú, una URL `/area/<slug>/` y un permiso por grupo de usuarios.
Para sumar una oficina nueva no hay que tocar `core`.
"""

from dataclasses import dataclass, field
from typing import Callable


@dataclass
class Grafico:
    titulo: str
    html: str
    ancho: int = 6  # columnas Bootstrap (1-12)


@dataclass
class Tabla:
    titulo: str
    columnas: list
    filas: list
    ancho: int = 6


@dataclass
class ContenidoArea:
    graficos: list = field(default_factory=list)
    tablas: list = field(default_factory=list)
    notas: list = field(default_factory=list)


@dataclass
class AreaDashboard:
    slug: str
    titulo: str
    icono: str
    descripcion: str
    construir: Callable  # (Contexto) -> ContenidoArea
    orden: int = 50
    # Opcional: (Contexto) -> list[Grafico] con 1 o 2 gráficos para la pestaña de resumen.
    grafico_resumen: Callable = None


AREAS: dict[str, AreaDashboard] = {}

# Quién puede ver cada área: superusuario, grupo "gerencia" o grupo con el nombre del área.
GRUPO_TOTAL = "gerencia"


def registrar_area(area: AreaDashboard):
    AREAS[area.slug] = area


def areas_ordenadas():
    return sorted(AREAS.values(), key=lambda a: a.orden)


def areas_visibles(usuario) -> list[AreaDashboard]:
    if not usuario.is_authenticated:
        return []
    if usuario.is_superuser:
        return areas_ordenadas()
    grupos = set(usuario.groups.values_list("name", flat=True))
    if GRUPO_TOTAL in grupos:
        return areas_ordenadas()
    return [a for a in areas_ordenadas() if a.slug in grupos]


def puede_ver(usuario, slug: str) -> bool:
    return any(a.slug == slug for a in areas_visibles(usuario))
