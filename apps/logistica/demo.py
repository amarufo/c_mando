"""Datos de ejemplo de Logística: requerimientos, órdenes y comprobantes enlazados por código."""

import math
import random
from collections import defaultdict
from datetime import timedelta
from decimal import Decimal

from apps.core.demo import dias_habiles, INICIO_DEMO, nombre_empresa_falsa, ruc_falso

from .models import Comprobante, Orden, Proveedor, Requerimiento

PESO_CC = {
    "018": 18,
    "019": 14,
    "017": 10,
    "025": 6,
    "037": 6,
    "044": 5,
    "061": 5,
    "065": 4,
    "002": 8,
    "005": 4,
    "006": 3,
    "014": 3,
    "011": 2,
    "020": 3,
    "021": 3,
    "049": 3,
}
CC1 = [
    "OE.2.1",
    "OE.3.2",
    "HU.1.4",
    "01.03.01",
    "GA",
    "GGF",
    "GGV",
    "SUBC01",
    "SUBC02",
    "1.2.1.5",
]
CONDICIONES = [
    ("CONTADO_FACTURA", 0.40),
    ("ADELANTO", 0.12),
    ("CREDITO_30", 0.12),
    ("CREDITO_7", 0.12),
    ("CREDITO_15", 0.10),
    ("CONTRAENTREGA", 0.14),
]
DIAS_CREDITO = {
    "CONTADO_FACTURA": 3,
    "ADELANTO": 0,
    "CREDITO_7": 7,
    "CREDITO_15": 15,
    "CREDITO_30": 30,
    "CONTRAENTREGA": 3,
}


def _elegir(rng, pares):
    return rng.choices([p for p, _ in pares], weights=[w for _, w in pares])[0]


def _dias_aprobacion(rng):
    return rng.choices([0, 1, 2, 3, 5, 9], weights=[55, 25, 10, 5, 4, 1])[0]


def _estado_rq(rng, edad, tipo):
    if edad <= 3:
        pares = [
            ("PENDIENTE", 25),
            ("APROBADA", 45),
            ("OBSERVADA", 15),
            ("RECHAZADA", 15),
        ]
    elif edad <= 30:
        pares = [
            ("FINALIZADO", 45),
            ("RECHAZADA", 27),
            ("APROBADA", 12),
            ("OBSERVADA", 10),
            ("POR_REGULARIZAR", 6),
        ]
    else:
        pares = [
            ("FINALIZADO", 62),
            ("RECHAZADA", 27),
            ("APROBADA", 4),
            ("OBSERVADA", 4),
            ("POR_REGULARIZAR", 3),
        ]
    estado = _elegir(rng, pares)
    if estado == "POR_REGULARIZAR" and tipo != "REGULARIZACION":
        estado = "FINALIZADO"
    return estado


def _estado_orden(rng, edad):
    if edad <= 3:
        pares = [("POR_APROBAR", 15), ("SIN_FACTURAR", 75), ("RECHAZADA", 10)]
    elif edad <= 15:
        pares = [
            ("SIN_FACTURAR", 35),
            ("FACTURADA", 10),
            ("POR_PAGAR", 35),
            ("FINALIZADA", 10),
            ("RECHAZADA", 10),
        ]
    elif edad <= 45:
        pares = [
            ("SIN_FACTURAR", 12),
            ("FACTURADA", 5),
            ("POR_PAGAR", 30),
            ("FINALIZADA", 43),
            ("RECHAZADA", 10),
        ]
    else:
        pares = [
            ("SIN_FACTURAR", 3),
            ("POR_PAGAR", 10),
            ("FINALIZADA", 77),
            ("RECHAZADA", 10),
        ]
    return _elegir(rng, pares)


def generar(rng: random.Random, est):
    corte = est.corte
    usados: set = set()
    proveedores = [
        Proveedor(ruc=ruc_falso(rng, usados), razon_social=nombre_empresa_falsa(rng))
        for _ in range(120)
    ]
    Proveedor.objects.bulk_create(proveedores)
    proveedores = list(Proveedor.objects.all())
    pesos_prov = [1 / (i + 1) ** 0.9 for i in range(len(proveedores))]

    ccs = [est.cc[c] for c in PESO_CC]
    pesos_cc = list(PESO_CC.values())
    contador = defaultdict(int)

    def numero(tipo, empresa):
        contador[(tipo, empresa.pk)] += 1
        return f"{tipo}-{empresa.prefijo_documentos}-2026-{contador[(tipo, empresa.pk)]:04d}"

    # --- Requerimientos ---
    rqs = []
    for dia in dias_habiles(INICIO_DEMO, corte):
        for _ in range(rng.randint(4, 11)):
            cc = rng.choices(ccs, weights=pesos_cc)[0]
            empresa = cc.empresa
            tipo = rng.choices(
                ["EMERGENCIA", "REGULARIZACION", "RUTINARIO", "LOGISTICO"],
                weights=[55, 30, 12, 3],
            )[0]
            estado = _estado_rq(rng, (corte - dia).days, tipo)
            aprob = (
                None
                if estado == "PENDIENTE"
                else min(dia + timedelta(days=_dias_aprobacion(rng)), corte)
            )
            items = rng.randint(1, 6)
            rqs.append(
                Requerimiento(
                    nro=numero("RQ", empresa),
                    empresa=empresa,
                    centro_costo=cc,
                    tipo=tipo,
                    clase=rng.choice(["BIENES", "SERVICIOS", "SERVICIOS"]),
                    estado=estado,
                    fecha_creacion=dia,
                    fecha_aprobacion=aprob,
                    n_items=items,
                    n_items_con_precio=sum(
                        1 for _ in range(items) if rng.random() < 0.19
                    ),
                )
            )
    Requerimiento.objects.bulk_create(rqs)

    # --- Órdenes: una por cada RQ aprobado (88 %) y un grupo de regularizaciones sin RQ ---
    ordenes = []
    base = [
        r
        for r in rqs
        if r.estado in ("FINALIZADO", "APROBADA")
        and r.fecha_aprobacion
        and rng.random() < 0.88
    ]
    origenes = [(r, False) for r in base] + [(None, True)] * int(len(base) * 0.19)
    for rq, regularizacion in origenes:
        if rq:
            cc, empresa, aprob_rq = rq.centro_costo, rq.empresa, rq.fecha_aprobacion
            emision = aprob_rq + timedelta(
                days=rng.choices([0, 1, 2, 3, 6], weights=[25, 25, 20, 15, 15])[0]
            )
        else:
            cc = rng.choices(ccs, weights=pesos_cc)[0]
            empresa, aprob_rq = cc.empresa, None
            emision = INICIO_DEMO + timedelta(
                days=rng.randint(0, (corte - INICIO_DEMO).days)
            )
        emision = min(emision, corte)
        estado = _estado_orden(rng, (corte - emision).days)
        aprobacion = (
            None
            if estado == "POR_APROBAR"
            else min(
                emision + timedelta(days=rng.choices([0, 1], weights=[60, 40])[0]),
                corte,
            )
        )
        moneda = "USD" if rng.random() < 0.08 else "PEN"
        total = Decimal(str(round(math.exp(rng.gauss(8.4, 1.1)), 2)))
        total = total / Decimal("3.5") if moneda == "USD" else total
        total = total.quantize(Decimal("0.01"))
        tc = est.conversor.tc(emision) if moneda == "USD" else Decimal(1)
        if estado in ("FINALIZADA", "POR_PAGAR", "FACTURADA"):
            entrega = rng.choices(
                ["ENTREGADO", "PARCIAL", "PENDIENTE"], weights=[93, 3, 4]
            )[0]
        elif estado == "SIN_FACTURAR":
            entrega = rng.choices(
                ["PENDIENTE", "ENTREGADO", "PARCIAL"], weights=[55, 40, 5]
            )[0]
        else:
            entrega = "PENDIENTE"
        condicion = _elegir(rng, CONDICIONES)
        ordenes.append(
            Orden(
                nro=numero(rng.choice(["OC", "OC", "OS"]), empresa),
                tipo="OC",
                empresa=empresa,
                centro_costo=cc,
                cc1=rng.choice(CC1),
                proveedor=rng.choices(proveedores, weights=pesos_prov)[0],
                rq_origen=rq.nro if rq else "",
                es_regularizacion=regularizacion,
                estado=estado,
                estado_entrega=entrega,
                condicion_pago=condicion,
                moneda=moneda,
                tc=tc,
                total=total,
                total_pen=(total * tc).quantize(Decimal("0.01")),
                fecha_aprobacion_rq=aprob_rq,
                fecha_emision=emision,
                fecha_aprobacion=aprobacion,
            )
        )
    for o in ordenes:
        o.tipo = o.nro.split("-")[0]
    Orden.objects.bulk_create(ordenes)
    for o in ordenes:
        est.ordenes_por_cc.setdefault(o.centro_costo.cc2, []).append(o.nro)

    # --- Comprobantes ---
    comprobantes, usados_serie = [], set()
    for o in ordenes:
        if o.estado not in ("FINALIZADA", "POR_PAGAR", "FACTURADA"):
            continue
        partes = (
            [Decimal(1)] if rng.random() < 0.8 else [Decimal("0.3"), Decimal("0.7")]
        )
        for i, parte in enumerate(partes):
            fecha_doc = min(
                o.fecha_aprobacion + timedelta(days=rng.randint(1, 25) + 10 * i), corte
            )
            tipo_doc = rng.choices(
                ["FACTURA", "RXH", "PASAJE_AEREO", "PASAJE_TERRESTRE"],
                weights=[80, 6, 10, 4],
            )[0]
            venc = fecha_doc + timedelta(days=DIAS_CREDITO[o.condicion_pago])
            total = (o.total * parte).quantize(Decimal("0.01"))
            if rng.random() < 0.10:  # orden y comprobante no coinciden (L14)
                total = (
                    total * Decimal(str(round(rng.uniform(0.8, 1.2), 3)))
                ).quantize(Decimal("0.01"))
            base = (
                total
                if tipo_doc != "FACTURA"
                else (total / Decimal("1.18")).quantize(Decimal("0.01"))
            )
            total_log = total
            if (
                rng.random() < 0.11
            ):  # importes distintos entre Logística y Contabilidad (L15)
                total_log = (
                    total * Decimal(str(round(rng.uniform(0.75, 1.25), 3)))
                ).quantize(Decimal("0.01"))
            if o.estado == "FINALIZADA":
                estado_pago = "PAGADO"
            else:
                estado_pago = rng.choices(
                    [
                        "PROGRAMADO",
                        "POR_DETRACCION",
                        "PEND_CONFORMIDAD",
                        "CONFORME",
                        "EN_REVISION",
                    ],
                    weights=[52, 17, 14, 10, 7],
                )[0]
            pago = programada = None
            if estado_pago == "PAGADO":
                pago = min(
                    max(
                        fecha_doc + timedelta(days=1),
                        venc - timedelta(days=rng.randint(0, 3)),
                    ),
                    corte,
                )
                programada = pago
            elif estado_pago == "PROGRAMADO" and rng.random() < 0.85:
                programada = corte + timedelta(days=rng.randint(1, 30))
            while True:
                serie = f"{rng.choice(['F001', 'F010', 'E001', 'F002'])}-{rng.randint(1, 99999):06d}"
                if (o.proveedor_id, serie) not in usados_serie:
                    usados_serie.add((o.proveedor_id, serie))
                    break
            tc = est.conversor.tc(fecha_doc) if o.moneda == "USD" else Decimal(1)
            comprobantes.append(
                Comprobante(
                    empresa=o.empresa,
                    proveedor=o.proveedor,
                    tipo_doc=tipo_doc,
                    serie_numero=serie,
                    nro_orden=o.nro,
                    centro_costo=o.centro_costo,
                    cc1=o.cc1,
                    fecha_doc=fecha_doc,
                    fecha_venc=venc,
                    moneda=o.moneda,
                    tc=tc,
                    base_imponible=base,
                    igv=total - base,
                    total=total,
                    total_logistica=total_log,
                    total_pen=(total * tc).quantize(Decimal("0.01")),
                    detraccion_monto=(
                        (total * Decimal("0.10")).quantize(Decimal("0.01"))
                        if (
                            tipo_doc == "FACTURA"
                            and total > 700
                            and rng.random() < 0.15
                        )
                        else 0
                    ),
                    retencion_garantia=(
                        (total * Decimal("0.05")).quantize(Decimal("0.01"))
                        if rng.random() < 0.03
                        else 0
                    ),
                    fecha_registro=min(fecha_doc + timedelta(days=1), corte),
                    estado_pago=estado_pago,
                    fecha_programada_pago=programada,
                    fecha_pago_real=pago,
                    nro_operacion=f"{rng.randint(100000, 999999)}" if pago else "",
                )
            )
    Comprobante.objects.bulk_create(comprobantes, batch_size=500)
    return {
        "proveedores": len(proveedores),
        "requerimientos": len(rqs),
        "ordenes": len(ordenes),
        "comprobantes": len(comprobantes),
    }
