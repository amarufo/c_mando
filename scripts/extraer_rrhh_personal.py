"""Consolida los excels de pagos a personal (hojas Honorarios y Planilla) en un solo CSV.

Uso: python extraer_rrhh_personal.py [carpeta_origen] [csv_salida]

- Cada subcarpeta de la carpeta origen es una empresa.
- Mes y tipo de archivo (PLANILLA / GRATIFICACION / CTS) se deducen del nombre del excel.
- Se ignoran las hojas BOLETA, Resumen, MOF, etc.; solo Honorarios/Honorario y Planilla.
- Las columnas comunes se normalizan al formato del maestro de RR. HH. (apps/rrhh/importers.py);
  el resto de columnas originales se conservan con el prefijo "x_".
"""

import csv
import re
import sys
import unicodedata
from datetime import date, datetime
from pathlib import Path

import openpyxl

BASE = Path(__file__).resolve().parents[2]
ORIGEN = BASE / "data" / "261113_rrhh_personal"
SALIDA = BASE / "data" / "rrhh_personal_ene_oct_2026.csv"

MESES = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
    "julio": 7, "agosto": 8, "setiembre": 9, "septiembre": 9, "octubre": 10,
}

# nombre normalizado de columna original -> columna canónica
ALIAS = {
    "n": "nro",
    "codigo": "codigo",
    "dni": "dni",
    "nombre completo": "apellidos_nombres",
    "apellidos y nombres": "apellidos_nombres",
    "cargo": "cargo",
    "area": "area",
    "oficina": "oficina",
    "sedapal": "sedapal",
    "proyecto": "proyecto",
    "centro de costos": "centro_costo",
    "gasto": "gasto",
    "tipo gasto": "tipo_gasto",
    "numero": "numero",
    "empresa": "empresa_columna",
    "tipo trabajador": "tipo_trabajador",
    "banco": "banco",
    "banco haberes": "banco",
    "n cta": "cuenta",
    "n cuenta": "cuenta",
    "cuenta haberes": "cuenta",
    "cci": "cci",
    "cussp": "cuspp",
    "cussp ": "cuspp",
    "f inicio": "fecha_ingreso",
    "fecha de ingreso": "fecha_ingreso",
    "f termino": "fecha_fin",
    "fecha de cese": "fecha_fin",
    "termino de contrato": "fecha_fin",
    "n recibo": "recibo",
    "susp 4ta": "susp_4ta",
    "dias mensual": "dias_mes",
    "dias laborados": "dias_trabajados",
    "dias trabajados": "dias_trabajados",
    "faltas": "faltas",
    "basico mensual": "sueldo_base",
    "sueldo": "sueldo_base",
    "sueldos": "sueldo_base",
    "haber basico": "haber_basico",
    "ingreso del mes": "ingreso_mes",
    "dscto x tardanzas": "descuento_tardanzas",
    "tardanzas": "descuento_tardanzas",
    "asignacion familiar": "asignacion_familiar",
    "total remuneracion": "total_remuneracion",
    "retencion 8": "retencion_8",
    "adicionales": "adicionales",
    "otros": "otros",
    "afp": "afp",
    "onp afp": "afp",
    "snp": "onp",
    "onp": "onp",
    "fondo afp": "fondo_afp",
    "seguro afp": "seguro_afp",
    "comision afp": "comision_afp",
    "tipo de comision afp": "tipo_comision_afp",
    "renta de 5ta categoria": "renta_5ta",
    "total descuentos": "total_descuentos",
    "neto a pagar": "neto_pagar",
    "essalud": "essalud",
    "total aportes": "total_aportes",
    "bono": "bono",
    "bono sup asist": "bono",
    "gratificacion": "gratificacion",
    "bet 9": "bet_9",
}
# "Neto" a secas (honorarios DPH Enero/Feb) es el neto final tras retención
ALIAS["neto"] = "neto_final"

CANON = [
    "empresa", "tipo_archivo", "anio", "mes", "periodo", "hoja", "condicion", "tipo",
    "dni", "apellidos_nombres", "cargo", "area", "oficina", "proyecto", "centro_costo",
    "gasto", "tipo_gasto", "empresa_columna", "tipo_trabajador", "fecha_ingreso", "fecha_fin",
    "banco", "cuenta", "cci", "cuspp", "recibo", "susp_4ta",
    "dias_mes", "dias_trabajados", "faltas", "sueldo_base", "haber_basico", "ingreso_mes",
    "asignacion_familiar", "bono", "gratificacion", "bet_9", "adicionales", "otros",
    "total_remuneracion", "retencion_8", "afp", "onp", "fondo_afp", "seguro_afp",
    "comision_afp", "tipo_comision_afp", "renta_5ta", "descuento_tardanzas",
    "total_descuentos", "neto_pagar", "neto_final", "essalud", "total_aportes",
    "archivo", "fila_excel", "nro",
]


def norm(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def limpio(v):
    if isinstance(v, datetime):
        return v.date().isoformat()
    if isinstance(v, date):
        return v.isoformat()
    if isinstance(v, str):
        v = v.strip()
        return v or None
    if isinstance(v, float) and v == int(v) and abs(v) < 1e12:
        return int(v)
    return v


def mes_archivo(nombre):
    n = norm(nombre)
    for m, i in MESES.items():
        if re.search(rf"\b{m}\b", n):
            return i
    m = re.match(r"^(\d{1,2})\b", n) or re.search(r"\b(\d{2}) 2026\b", n) or re.search(r"\b(\d{2}) 26\b", n)
    if m:
        return int(m.group(1))
    m = re.search(r"planilla\s+(\d{2})\b", n)
    return int(m.group(1)) if m else None


def tipo_archivo(nombre):
    n = norm(nombre)
    if "gratificacion" in n:
        return "GRATIFICACION"
    if "cts" in n.split():
        return "CTS"
    return "PLANILLA"


def clasificar(proyecto, centro, gasto, tipo_gasto, area):
    """administrativo = gasto global de la empresa; proyecto = asignado a un proyecto específico."""
    for v in (gasto, tipo_gasto):
        t = norm(v or "")
        if t.startswith("admin") or t.startswith("indirecto"):
            return "ADMINISTRATIVO"
        if t.startswith(("proyecto", "directo", "obra")):
            return "PROYECTO"
    p = norm(proyecto or centro or "")
    if not p:
        return "ADMINISTRATIVO"
    if re.search(r"\badmin|oficina|sede|gerencia|corporativ|general", p):
        return "ADMINISTRATIVO"
    return "PROYECTO"


def encabezado(ws):
    for i, fila in enumerate(ws.iter_rows(min_row=1, max_row=25, values_only=True), 1):
        if "dni" in [norm(c) for c in fila if c is not None]:
            return i, fila
    return None, None


def filas_hoja(ws):
    i, fila = encabezado(ws)
    if i is None:
        return
    cols, vistos = [], {}
    for j, c in enumerate(fila):
        if c is None or not str(c).strip():
            cols.append(None)
            continue
        k = norm(c)
        vistos[k] = vistos.get(k, 0) + 1
        cols.append((k, str(c).strip(), vistos[k]))
    for n, r in enumerate(ws.iter_rows(min_row=i + 1, values_only=True), i + 1):
        d = {}
        for c, v in zip(cols, r):
            if c is None:
                continue
            k, orig, rep = c
            v = limpio(v)
            canon = ALIAS.get(k) if rep == 1 else None
            if canon:
                d[canon] = v
            elif v is not None:
                d["x_" + re.sub(r"\W+", "_", norm(orig)).strip("_") + (f"_{rep}" if rep > 1 else "")] = v
        dni = re.sub(r"\D", "", str(d.get("dni") or ""))
        if not dni or not d.get("apellidos_nombres"):
            continue
        d["dni"] = dni.zfill(8) if len(dni) <= 8 else dni
        yield n, d


def main(origen=ORIGEN, salida=SALIDA):
    registros, extras = [], set()
    for carpeta in sorted(p for p in Path(origen).iterdir() if p.is_dir()):
        for f in sorted(carpeta.glob("*.xlsx")):
            if f.name.startswith("~$"):
                continue
            tarch = tipo_archivo(f.name)
            mes = mes_archivo(f.name)
            if tarch == "GRATIFICACION":
                mes = 7
            elif tarch == "CTS":
                mes = 5
            wb = openpyxl.load_workbook(f, data_only=True)
            for ws in wb:
                t = norm(ws.title)
                if t.startswith("honorario"):
                    cond = "RXH"
                elif t.startswith("planilla"):
                    cond = "PLANILLA"
                else:
                    continue
                for n, d in filas_hoja(ws):
                    d.update(
                        empresa=carpeta.name, tipo_archivo=tarch, anio=2026, mes=mes,
                        periodo=f"2026-{mes:02d}-01" if mes else None, hoja=ws.title.strip(),
                        condicion=cond, archivo=f.name, fila_excel=n,
                    )
                    d["tipo"] = clasificar(
                        d.get("proyecto"), d.get("centro_costo"), d.get("gasto"),
                        d.get("tipo_gasto"), d.get("area"),
                    )
                    extras.update(k for k in d if k.startswith("x_"))
                    registros.append(d)
    campos = CANON + sorted(extras)
    with open(salida, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=campos, extrasaction="ignore")
        w.writeheader()
        w.writerows(registros)
    print(f"{len(registros)} filas, {len(campos)} columnas -> {salida}")


if __name__ == "__main__":
    main(*(Path(a) for a in sys.argv[1:3]))
