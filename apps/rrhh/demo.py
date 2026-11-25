"""Datos de ejemplo de RR. HH.: personal ficticio, costos por proyecto, planilla, marcaciones y obligaciones.

Nombres y DNI son inventados; no corresponden a personas reales.
"""
import random
from datetime import date, datetime, time, timedelta
from decimal import Decimal

from django.utils import timezone

from apps.core.demo import APELLIDOS, NOMBRES, dias_habiles
from apps.core.services import fin_de_mes, primer_dia, rango_meses, sumar_meses

from .models import CostoProyectoMes, Marcacion, Obligacion, Persona, PlanillaMes

# Personas por centro de costo (proyectos y áreas): suman 117, como en el resumen de planilla actual.
DOTACION = {"018": 22, "019": 18, "017": 16, "025": 6, "037": 9, "044": 6, "061": 10, "065": 6,
            "002": 6, "005": 4, "006": 3, "011": 3, "014": 2, "001": 2, "003": 2, "004": 2}
SUELDOS = {"CLAVE": (6000, 12000), "NO_CLAVE": (3500, 6000), "ADMINISTRATIVO": (2500, 5000), "MANO_OBRA": (1800, 3000)}
CARGOS = {
    "CLAVE": ["Residente de obra", "Supervisor de obra", "Jefe de calidad", "Especialista en seguridad", "Administrador de obra"],
    "NO_CLAVE": ["Asistente técnico", "Topógrafo", "Almacenero", "Maestro de obra", "Asistente administrativo"],
    "ADMINISTRATIVO": ["Asistente contable", "Asistente de logística", "Analista de RR. HH.", "Soporte TI", "Asistente de tesorería"],
    "MANO_OBRA": ["Operario", "Oficial", "Peón", "Operador de maquinaria", "Vigilante"],
}


def _dni(rng, usados):
    while True:
        dni = str(rng.randint(10_000_000, 79_999_999))
        if dni not in usados:
            usados.add(dni)
            return dni


def _redondear(x):
    return Decimal(int(round(x / 50.0) * 50))


def generar(rng: random.Random, est):
    corte = est.corte
    usados: set = set()
    personas = []
    for cc2, n in DOTACION.items():
        cc = est.cc[cc2]
        proyecto = est.proyectos.get(cc2)
        inicio_base = proyecto.fecha_acta_eo if proyecto else date(2025, 6, 1)
        for i in range(n):
            if cc.tipo == "PROYECTO":
                categoria = "CLAVE" if i < 3 else "NO_CLAVE" if i < 3 + round(n * 0.22) else "ADMINISTRATIVO" if i < 3 + round(n * 0.22) + round(n * 0.13) else "MANO_OBRA"
            else:
                categoria = "ADMINISTRATIVO"
            planilla_prob = {"CLAVE": 0.7, "NO_CLAVE": 0.6, "ADMINISTRATIVO": 0.75, "MANO_OBRA": 0.15}[categoria]
            condicion = "PLANILLA" if rng.random() < planilla_prob else "RXH"
            ingreso = inicio_base - timedelta(days=rng.randint(0, 25)) if cc.tipo == "PROYECTO" else inicio_base + timedelta(days=rng.randint(0, 400))
            fin_contrato = (proyecto.fecha_fin_eo + timedelta(days=30)) if proyecto and rng.random() < 0.8 else (date(2026, 12, 31) if rng.random() < 0.5 else None)
            dni = _dni(rng, usados)
            lo, hi = SUELDOS[categoria]
            personas.append(Persona(
                dni=dni, apellidos_nombres=f"{rng.choice(APELLIDOS).upper()} {rng.choice(APELLIDOS).upper()}, {rng.choice(NOMBRES)}",
                empresa=cc.empresa, centro_costo=cc, area="Obra" if cc.tipo == "PROYECTO" else cc.nombre.title(), cargo=rng.choice(CARGOS[categoria]),
                categoria=categoria, condicion=condicion, fecha_ingreso=ingreso, fecha_fin_contrato=fin_contrato, estado_contrato="FIRMADO",
                sueldo_base=_redondear(rng.uniform(lo, hi)), sistema_pension="AFP" if rng.random() < 0.8 else "ONP", sede=cc.nombre.title()[:30],
                codigo_reloj=dni if condicion == "PLANILLA" else "",
            ))
    # Casos para las alertas: ingresos recientes (contrato por elaborar), contratos por vencer y ceses
    for p in rng.sample(personas, 6):
        p.fecha_ingreso = corte - timedelta(days=rng.randint(3, 25))
    for p in rng.sample([x for x in personas if x.fecha_ingreso > corte - timedelta(days=30)], 4):
        p.estado_contrato = "ELABORAR"
    for p in rng.sample(personas, 7):
        p.fecha_fin_contrato = corte + timedelta(days=rng.randint(3, 28))
    for p in rng.sample([x for x in personas if x.condicion == "RXH"], 5):
        p.fecha_cese = corte - timedelta(days=rng.randint(10, 60))
    Persona.objects.bulk_create(personas)
    personas = list(Persona.objects.select_related("centro_costo", "empresa"))

    # --- Costo por proyecto y planilla: meses completos (hasta el mes anterior al corte) ---
    costos, planillas = [], []
    for m in rango_meses(date(2026, 3, 1), sumar_meses(primer_dia(corte), -1)):
        ultimo = fin_de_mes(m)
        dias_mes = ultimo.day
        for p in personas:
            if p.fecha_ingreso > ultimo or (p.fecha_cese and p.fecha_cese < m):
                continue
            desde = max(p.fecha_ingreso, m)
            hasta = min(p.fecha_cese or ultimo, ultimo)
            dias = (hasta - desde).days + 1
            bruto = (p.sueldo_base / dias_mes * dias).quantize(Decimal("0.01"))
            costos.append(CostoProyectoMes(periodo=m, empresa=p.empresa, centro_costo=p.centro_costo, persona=p, categoria=p.categoria, condicion=p.condicion,
                                           dias_laborados=dias, sueldo_base_acordado=p.sueldo_base, sueldo_bruto=bruto))
            es_planilla = p.condicion == "PLANILLA"
            descuentos = bruto * Decimal("0.13" if es_planilla else "0.08")
            planillas.append(PlanillaMes(
                periodo=m, persona=p, condicion=p.condicion, dias_trabajados=dias, remuneracion_bruta=bruto, descuentos_total=descuentos.quantize(Decimal("0.01")),
                aporte_pension=(bruto * Decimal("0.10")).quantize(Decimal("0.01")) if es_planilla else 0,
                essalud=(bruto * Decimal("0.09")).quantize(Decimal("0.01")) if es_planilla else 0,
                neto_pagar=(bruto - descuentos).quantize(Decimal("0.01")),
                recibo_emitido=None if es_planilla else rng.random() < (0.86 if m == sumar_meses(primer_dia(corte), -1) else 0.97),
            ))
    CostoProyectoMes.objects.bulk_create(costos, batch_size=1000)
    PlanillaMes.objects.bulk_create(planillas, batch_size=1000)

    # --- Marcaciones de los últimos 15 días del personal en planilla ---
    marcas = []
    for p in personas:
        if p.condicion != "PLANILLA" or (p.fecha_cese and p.fecha_cese <= corte):
            continue
        tendencia = rng.uniform(-9, 3)  # minutos respecto de las 08:00 (algunas personas llegan siempre tarde)
        for d in dias_habiles(max(corte - timedelta(days=14), p.fecha_ingreso), corte):
            if rng.random() < 0.04:
                continue
            entrada = datetime.combine(d, time(8, 0)) + timedelta(minutes=tendencia + rng.gauss(0, 6))
            salida = datetime.combine(d, time(17, 30)) + timedelta(minutes=rng.randint(-20, 70))
            for fh in (entrada, salida):
                marcas.append(Marcacion(codigo_reloj=p.codigo_reloj, fecha_hora=timezone.make_aware(fh.replace(second=0, microsecond=0)), persona=p))
    for codigo in ("1", "2", "12"):  # códigos internos del reloj sin persona asociada
        for d in list(dias_habiles(corte - timedelta(days=6), corte))[:3]:
            marcas.append(Marcacion(codigo_reloj=codigo, fecha_hora=timezone.make_aware(datetime.combine(d, time(8, rng.randint(0, 30))))))
    Marcacion.objects.bulk_create(marcas, batch_size=1000, ignore_conflicts=True)

    # --- Obligaciones mensuales ---
    obligaciones = []
    for m in rango_meses(date(2026, 3, 1), primer_dia(corte)):
        sig = sumar_meses(m, 1)
        for tipo, limite in (("AFP", m.replace(day=25)), ("SCTR", m.replace(day=28)), ("VIDA_LEY", m.replace(day=28)), ("PLAME", sig.replace(day=15))):
            entrega = None
            if limite <= corte:
                entrega = limite - timedelta(days=rng.randint(0, 3)) if rng.random() < 0.9 else limite + timedelta(days=rng.randint(1, 3))
                entrega = min(entrega, corte)
            obligaciones.append(Obligacion(periodo=m, tipo=tipo, fecha_limite=limite, fecha_entrega=entrega, responsable="Asistente de RR. HH."))
    Obligacion.objects.bulk_create(obligaciones)
    return {"personas": len(personas), "costos": len(costos), "marcaciones": len(marcas), "obligaciones": len(obligaciones)}
