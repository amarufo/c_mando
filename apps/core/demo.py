"""Datos de ejemplo (aleatorios y reproducibles) que imitan la operación descrita en docs/parte1.

NO contienen datos reales: nombres, RUC, DNI y montos son inventados. Las proporciones (estado de los RQ,
porcentaje de emergencias, deuda concentrada en diciembre, etc.) se calibraron con lo observado en
los archivos de octubre-noviembre de 2026 para que los indicadores sean realistas.
"""

import random
from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import Decimal

from .models import Categoria, CentroCosto, Empresa, TipoCambio
from .services import ConversorMoneda

CORTE_DEMO = date(2026, 11, 12)
INICIO_DEMO = date(2026, 3, 1)

NOMBRES = [
    "Juan",
    "Luis",
    "Carlos",
    "Miguel",
    "José",
    "Pedro",
    "Jorge",
    "Víctor",
    "Raúl",
    "César",
    "Ana",
    "María",
    "Rosa",
    "Carmen",
    "Lucía",
    "Elena",
    "Patricia",
    "Sofía",
    "Diana",
    "Julia",
    "Hugo",
    "Óscar",
    "Walter",
    "Edgar",
    "Iván",
    "Rocío",
    "Milagros",
    "Nelly",
    "Percy",
    "Alex",
]
APELLIDOS = [
    "Quispe",
    "Huamán",
    "Flores",
    "Rojas",
    "Mamani",
    "Chávez",
    "Torres",
    "Ramos",
    "Vargas",
    "Castro",
    "Díaz",
    "Salazar",
    "Paredes",
    "Medina",
    "Cruz",
    "Rivera",
    "Soto",
    "Campos",
    "Ortiz",
    "Vega",
    "Silva",
    "León",
    "Núñez",
    "Ponce",
    "Aguirre",
    "Valdez",
    "Córdova",
    "Herrera",
    "Ccori",
    "Apaza",
]
PALABRAS_EMPRESA = [
    "Andina",
    "Del Sur",
    "Los Andes",
    "Norte",
    "Pacífico",
    "Continental",
    "Peruana",
    "Industrial",
    "Global",
    "Moderna",
    "Central",
    "Inca",
]
RUBROS = [
    "Ferretería",
    "Constructora",
    "Comercial",
    "Servicios Generales",
    "Transportes",
    "Maquinarias",
    "Agregados",
    "Suministros",
    "Ingeniería",
    "Concretos",
]


@dataclass
class EstadoDemo:
    """Objetos compartidos entre generadores para que las áreas queden enlazadas por código."""

    corte: date = CORTE_DEMO
    empresas: dict = field(default_factory=dict)  # nombre_corto -> Empresa
    cc: dict = field(default_factory=dict)  # cc2 -> CentroCosto
    categorias: list = field(default_factory=list)
    conversor: ConversorMoneda = None
    proyectos: dict = field(default_factory=dict)  # cc2 -> Proyecto
    ordenes_por_cc: dict = field(default_factory=dict)  # cc2 -> [nro de orden]


def ruc_falso(rng: random.Random, usados: set) -> str:
    while True:
        ruc = rng.choice(["20", "10"]) + "".join(
            str(rng.randint(0, 9)) for _ in range(9)
        )
        if ruc not in usados:
            usados.add(ruc)
            return ruc


def nombre_empresa_falsa(rng: random.Random) -> str:
    return f"{rng.choice(RUBROS)} {rng.choice(PALABRAS_EMPRESA)} {rng.choice(['S.A.C.', 'E.I.R.L.', 'S.R.L.'])}"


def dias_habiles(desde: date, hasta: date):
    d = desde
    while d <= hasta:
        if d.weekday() < 6:  # lunes a sábado
            yield d
        d += timedelta(days=1)


EMPRESAS = [
    ("20607967912", "DEPERU HUB E.I.R.L.", "DPH", "DPH"),
    ("20615105725", "DEPERU HUB CONSTRUCCION S.A.C.", "DPHC", "DPHC"),
    ("20600000013", "DPH CARGA Y TRANSPORTE S.A.C. (ejemplo)", "DPH Carga", "DPC"),
    (
        "20600000021",
        "COOPERATIVA SUDAMERICANA COSUDECO S.A.C. (ejemplo)",
        "Cosudeco",
        "CSD",
    ),
    ("20600000039", "PERU SEGURO 365 S.A.C. (ejemplo)", "Perú Seguro 365", "PS"),
    ("20600000047", "DEPERU HUB CAPITAL S.A.C. (ejemplo)", "DPH Capital", "DPK"),
]

# (cc2, nombre, tipo, empresa)
CENTROS = [
    ("001", "GERENCIA GENERAL", "AREA", "DPH"),
    ("002", "ADMINISTRACIÓN", "AREA", "DPH"),
    ("003", "FINANZAS Y TESORERÍA", "AREA", "DPH"),
    ("004", "CONTABILIDAD", "AREA", "DPH"),
    ("005", "LOGÍSTICA Y COMPRAS", "AREA", "DPH"),
    ("006", "ALMACÉN E INVENTARIOS", "AREA", "DPH"),
    ("007", "LICITACIONES", "AREA", "DPHC"),
    ("008", "PROYECTOS Y EXPEDIENTES", "AREA", "DPHC"),
    ("011", "RECURSOS HUMANOS", "AREA", "DPH"),
    ("014", "SISTEMAS Y TI", "AREA", "DPH"),
    ("017", "CC COLLANA", "PROYECTO", "DPHC"),
    ("018", "CC CARRETERA", "PROYECTO", "DPHC"),
    ("019", "CC IGUAIN", "PROYECTO", "DPH"),
    ("020", "CC GENERAL PIURA", "SEDE", "DPH"),
    ("021", "CC GENERAL TUMBES", "SEDE", "DPH"),
    ("025", "PISCO - SAN CLEMENTE - CHACARILLA MENCIA", "PROYECTO", "DPHC"),
    ("037", "TUMBES - ZORRITOS - CHERRELIQUE", "PROYECTO", "DPH"),
    ("044", "LAMBAYEQUE - CHICLAYO - MOCHUMI", "PROYECTO", "DPH"),
    ("049", "CC GENERAL LIMA", "SEDE", "DPH"),
    ("061", "RIO CHOCHOPE - LAMBAYEQUE", "PROYECTO", "DPHC"),
    ("065", "CANAL TAYMI 2 - CHICLAYO", "PROYECTO", "DPHC"),
]

COMPONENTES_CATEGORIAS = {
    "00": [
        "Estudios previos",
        "Elaboración de propuesta",
        "Carta fianza",
        "Visitas de campo",
        "Trámites y legalización",
    ],
    "01": [
        "Movimiento de tierras",
        "Concreto armado",
        "Acero de refuerzo",
        "Encofrado",
        "Albañilería",
        "Instalaciones eléctricas",
        "Instalaciones sanitarias",
        "Pavimentos",
        "Acabados",
        "Alquiler de maquinaria",
        "Subcontratos",
        "Combustible",
    ],
    "02": [
        "Personal de obra",
        "Seguridad y salud",
        "Alquiler de oficina y almacén",
        "Movilidad y viáticos",
        "Servicios públicos",
        "Herramientas y equipos",
    ],
    "03": [
        "Especialistas del expediente técnico",
        "Estudios básicos",
        "Topografía",
        "Gastos del expediente",
    ],
    "04": ["Supervisión del expediente"],
    "05": ["Supervisión de obra", "Control de calidad"],
    "06": ["Gastos de gestión"],
    "07": ["Liquidación de obra"],
    "3101": ["Gastos administrativos"],
}


def generar_catalogos(rng: random.Random) -> EstadoDemo:
    estado = EstadoDemo()
    for ruc, razon, corto, prefijo in EMPRESAS:
        estado.empresas[corto] = Empresa.objects.create(
            ruc=ruc, razon_social=razon, nombre_corto=corto, prefijo_documentos=prefijo
        )
    for cc2, nombre, tipo, emp in CENTROS:
        estado.cc[cc2] = CentroCosto.objects.create(
            cc2=cc2, nombre=nombre, tipo=tipo, empresa=estado.empresas[emp]
        )
    for comp, items in COMPONENTES_CATEGORIAS.items():
        for i, item in enumerate(items, start=1):
            especial = (
                "Laboral"
                if "ersonal" in item or "pecialistas" in item
                else ("Financiero" if "arta fianza" in item else "")
            )
            estado.categorias.append(
                Categoria.objects.create(
                    codigo=f"{comp}.{i:02d}",
                    componente=comp,
                    item=item,
                    etapa=Categoria.COMPONENTES[comp],
                    tipo_costo="Fijo" if comp in ("02", "3101") else "Variable",
                    categoria_especial=especial,
                )
            )
    tc, d = 3.48, date(2026, 1, 1)
    filas = []
    while d <= date(2027, 1, 31):
        tc = min(3.62, max(3.38, tc + rng.uniform(-0.012, 0.012)))
        filas.append(
            TipoCambio(
                fecha=d,
                compra=Decimal(str(round(tc - 0.015, 4))),
                venta=Decimal(str(round(tc + 0.015, 4))),
            )
        )
        d += timedelta(days=1)
    TipoCambio.objects.bulk_create(filas)
    estado.conversor = ConversorMoneda()
    return estado
