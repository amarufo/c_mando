"""Carga manual (y, a futuro, automática) de archivos limpios.

Cada oficina entrega un archivo con la estructura de docs/parte1/07_archivos_limpios.md.
Un `Importador` declara las columnas esperadas y a qué tabla van; este módulo hace el resto:

    1. lee el archivo (CSV o Excel),
    2. valida **todas** las filas (tipos, listas cerradas, claves foráneas por código),
    3. si hay errores no guarda nada y devuelve el detalle por fila,
    4. si todo está bien, guarda de forma atómica (inserta o actualiza por la clave natural).

La misma función `procesar()` la usan la pantalla de carga, el comando `importar_archivo`
y la API `/api/v1/cargas/<tabla>/`. Así, cuando los datos lleguen automáticamente, solo
cambia quién llama a `procesar()`.
"""

from __future__ import annotations

import io
import re
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any, Optional

import pandas as pd
from django.db import models, transaction

from .models import CargaArchivo

MAX_ERRORES = 200


@dataclass
class Columna:
    nombre: str  # encabezado en el archivo
    tipo: str  # texto, fecha, numero, entero, bool
    obligatorio: bool = True
    campo: Optional[str] = None  # campo del modelo (por defecto, igual a `nombre`)
    buscar: Optional[tuple] = (
        None  # (Modelo, "campo__de__busqueda") para claves foráneas
    )
    valores: Optional[tuple] = None  # lista cerrada de valores permitidos
    ejemplo: str = ""
    extraer: Any = (
        None  # callable(obj) para exportar columnas virtuales (campo que empieza con "_")
    )

    @property
    def destino(self) -> str:
        return self.campo or self.nombre


@dataclass
class Importador:
    slug: str
    area: str
    descripcion: str
    modelo: type
    columnas: list
    clave: tuple  # campos del modelo que identifican una fila (para actualizar en vez de duplicar)
    queryset: Any = None  # callable opcional: () -> queryset a exportar
    # Opcional: (datos, cache) -> dict con campos adicionales (p. ej. resolver una clave compuesta). Puede lanzar ValueError.
    armar: Any = None


IMPORTADORES: dict[str, Importador] = {}


def registrar(imp: Importador) -> Importador:
    IMPORTADORES[imp.slug] = imp
    return imp


# --- lectura y conversión de valores -----------------------------------------------------


def leer_archivo(archivo, nombre: str = "") -> pd.DataFrame:
    """Lee CSV o Excel como texto (así el DNI conserva sus ceros). `archivo` es una ruta o un objeto de archivo."""
    nombre = (nombre or getattr(archivo, "name", str(archivo))).lower()
    if nombre.endswith((".xlsx", ".xlsm")):
        df = pd.read_excel(archivo, dtype=object)
    elif nombre.endswith(".csv"):
        if hasattr(
            archivo, "read"
        ):  # archivo subido: se decodifica a texto antes de leerlo
            texto = archivo.read()
            texto = texto.decode("utf-8-sig") if isinstance(texto, bytes) else texto
            archivo = io.StringIO(texto)
        df = pd.read_csv(
            archivo, dtype=str, sep=None, engine="python", encoding="utf-8-sig"
        )
    else:
        raise ValueError("Formato no soportado: use .csv o .xlsx")
    df.columns = [str(c).strip() for c in df.columns]
    return df


def _vacio(x) -> bool:
    return (
        x is None
        or (isinstance(x, float) and pd.isna(x))
        or (isinstance(x, str) and not x.strip())
        or x is pd.NaT
    )


def convertir(col: Columna, bruto):
    """Devuelve el valor convertido. Lanza ValueError con un mensaje claro si no es válido."""
    if _vacio(bruto):
        if col.obligatorio:
            raise ValueError("campo obligatorio vacío")
        return "" if col.tipo == "texto" else None
    t = col.tipo
    if t == "texto":
        if isinstance(bruto, float) and bruto.is_integer():
            bruto = int(bruto)
        valor = str(bruto).strip()
    elif t == "fecha":
        valor = _fecha(bruto)
    elif t == "fechahora":
        valor = _fecha_hora(bruto)
    elif t in ("numero", "entero"):
        try:
            valor = Decimal(str(bruto).replace(",", "").replace("S/", "").strip())
        except InvalidOperation:
            raise ValueError(f"'{bruto}' no es un número")
        if t == "entero":
            if valor != valor.to_integral_value():
                raise ValueError(f"'{bruto}' no es un entero")
            valor = int(valor)
    elif t == "bool":
        s = str(bruto).strip().upper()
        if s in {"SI", "SÍ", "S", "TRUE", "1", "VERDADERO"}:
            valor = True
        elif s in {"NO", "N", "FALSE", "0", "FALSO"}:
            valor = False
        else:
            raise ValueError(f"'{bruto}' no es SI/NO")
    else:
        raise ValueError(f"tipo desconocido {t}")
    if col.valores:
        coincide = {v.upper(): v for v in col.valores}.get(str(valor).upper())
        if coincide is None:
            raise ValueError(f"'{valor}' no está en {list(col.valores)}")
        valor = coincide
    return valor


def _fecha(bruto) -> date:
    if isinstance(bruto, (datetime, pd.Timestamp)):
        return bruto.date()
    if isinstance(bruto, date):
        return bruto
    s = str(bruto).strip()[:10]
    for formato in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(s, formato).date()
        except ValueError:
            continue
    raise ValueError(f"'{bruto}' no es una fecha (use AAAA-MM-DD)")


def _fecha_hora(bruto):
    """Fecha y hora con zona horaria del proyecto. Acepta AAAA-MM-DD HH:MM o dd/mm/aaaa HH:MM."""
    from django.utils import timezone

    if isinstance(bruto, (datetime, pd.Timestamp)):
        valor = bruto.to_pydatetime() if isinstance(bruto, pd.Timestamp) else bruto
    else:
        s = str(bruto).strip()
        for formato in (
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%d/%m/%Y %H:%M:%S",
            "%d/%m/%Y %H:%M",
        ):
            try:
                valor = datetime.strptime(s, formato)
                break
            except ValueError:
                continue
        else:
            raise ValueError(f"'{bruto}' no es fecha y hora (use AAAA-MM-DD HH:MM)")
    return timezone.make_aware(valor) if timezone.is_naive(valor) else valor


class _CacheFK:
    """Resuelve claves foráneas por código con una sola consulta por modelo."""

    def __init__(self):
        self._cache: dict = {}

    def resolver(self, col: Columna, codigo):
        return self.obtener(col.buscar[0], col.buscar[1], codigo)

    def obtener(self, modelo, campo: str, codigo):
        clave = (modelo, campo)
        if clave not in self._cache:
            self._cache[clave] = {
                str(_cadena(o, campo)): o for o in modelo.objects.all()
            }
        obj = self._cache[clave].get(str(codigo))
        if obj is None:
            raise ValueError(
                f"código '{codigo}' no existe en el catálogo ({modelo.__name__}.{campo})"
            )
        return obj


def _cadena(obj, ruta: str):
    for parte in ruta.split("__"):
        obj = getattr(obj, parte)
    return obj


# --- proceso principal ------------------------------------------------------------------


def procesar(
    imp: Importador,
    df: pd.DataFrame,
    usuario=None,
    nombre_archivo: str = "",
    guardar: bool = True,
) -> CargaArchivo:
    """Valida el DataFrame y, si no hay errores y `guardar=True`, lo guarda. Siempre deja un CargaArchivo."""
    errores: list[dict] = []
    filas_validas: list[dict] = []
    faltan = [
        c.nombre for c in imp.columnas if c.obligatorio and c.nombre not in df.columns
    ]
    if faltan:
        errores.append(
            {
                "fila": 1,
                "columna": ", ".join(faltan),
                "error": "faltan columnas obligatorias en el encabezado",
            }
        )
    else:
        cache = _CacheFK()
        vistas: set = set()
        for i, (_, fila) in enumerate(
            df.iterrows(), start=2
        ):  # la fila 1 del archivo es el encabezado
            datos, ok = {}, True
            for col in imp.columnas:
                if col.nombre not in df.columns:
                    continue
                try:
                    valor = convertir(col, fila[col.nombre])
                    if valor is not None and col.buscar:
                        valor = cache.resolver(col, valor)
                    campo = col.destino
                    # Un campo opcional vacío en una columna que no admite NULL usa el valor por defecto del modelo.
                    if (
                        valor is None
                        and not campo.startswith("_")
                        and not imp.modelo._meta.get_field(campo).null
                    ):
                        continue
                    datos[campo] = valor
                except ValueError as e:
                    ok = False
                    if len(errores) < MAX_ERRORES:
                        errores.append(
                            {"fila": i, "columna": col.nombre, "error": str(e)}
                        )
            if ok and imp.armar:
                try:
                    datos.update(imp.armar(datos, cache))
                except ValueError as e:
                    ok = False
                    errores.append({"fila": i, "columna": "(varias)", "error": str(e)})
            if ok:
                datos = {
                    k: v for k, v in datos.items() if not k.startswith("_")
                }  # campos virtuales
                llave = tuple(
                    getattr(datos.get(k), "pk", datos.get(k)) for k in imp.clave
                )
                if llave in vistas:
                    ok = False
                    errores.append(
                        {
                            "fila": i,
                            "columna": ", ".join(imp.clave),
                            "error": f"clave repetida en el archivo: {llave}",
                        }
                    )
                vistas.add(llave)
            if ok:
                filas_validas.append(datos)

    n_error = len({e["fila"] for e in errores}) if errores else 0
    estado = (
        CargaArchivo.Estado.RECHAZADA
        if errores
        else (CargaArchivo.Estado.OK if guardar else CargaArchivo.Estado.SIMULACION)
    )
    if not errores and guardar:
        with transaction.atomic():
            for datos in filas_validas:
                llave = {k: datos[k] for k in imp.clave}
                resto = {k: v for k, v in datos.items() if k not in imp.clave}
                # save() completo (no update_or_create): los modelos recalculan campos derivados al guardar.
                obj = imp.modelo.objects.filter(**llave).first() or imp.modelo(**llave)
                for campo, valor in resto.items():
                    setattr(obj, campo, valor)
                obj.save()
    return CargaArchivo.objects.create(
        area=imp.area,
        tabla=imp.slug,
        nombre_archivo=nombre_archivo[:200],
        usuario=usuario if getattr(usuario, "pk", None) else None,
        filas_leidas=len(df),
        filas_ok=0 if errores else len(filas_validas),
        filas_error=n_error,
        estado=estado,
        errores=errores[:MAX_ERRORES],
    )


# --- exportación (plantillas y respaldo) -------------------------------------------------


def exportar(imp: Importador, limite: Optional[int] = None) -> pd.DataFrame:
    """Tabla con las columnas del archivo limpio, a partir de los datos cargados. Sirve de plantilla y de respaldo."""
    qs = imp.queryset() if imp.queryset else imp.modelo.objects.all()
    if limite:
        qs = qs[:limite]
    filas = []
    for obj in qs:
        fila = {}
        for col in imp.columnas:
            if col.extraer:
                fila[col.nombre] = col.extraer(obj)
                continue
            valor = getattr(obj, col.destino)
            if col.buscar and valor is not None:
                valor = _cadena(valor, col.buscar[1])
            if isinstance(valor, models.Model):
                valor = str(valor)
            fila[col.nombre] = valor
        filas.append(fila)
    return pd.DataFrame(filas, columns=[c.nombre for c in imp.columnas])


def plantilla(imp: Importador) -> pd.DataFrame:
    """Archivo vacío con encabezados y una fila de ejemplo."""
    return pd.DataFrame([{c.nombre: c.ejemplo for c in imp.columnas}])


def descubrir():
    """Importa el módulo `importers` de cada app para que se registren sus tablas."""
    from importlib import import_module

    from django.apps import apps

    for config in apps.get_app_configs():
        if config.name.startswith("apps."):
            try:
                import_module(f"{config.name}.importers")
            except ModuleNotFoundError as e:
                if not e.name or not e.name.endswith(".importers"):
                    raise
    import_module("apps.core.importers_catalogos")
    return IMPORTADORES
