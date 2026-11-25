"""Datos de ejemplo de Préstamos: catálogo, cronogramas (cuota fija y capital al final) y pagos reales."""

import random
from datetime import date, timedelta
from decimal import Decimal

from apps.core.services import sumar_meses

from .models import Cuota, PagoCuota, Prestamo

# codigo, deudor (nombre corto o None si es personal), acreedor, tipo, moneda, capital, desembolso, tasa %, tipo tasa, sistema, cuotas, comisión
PRESTAMOS = [
    (
        "FIN-BBVA-001",
        "DPHC",
        "BBVA",
        "BANCO",
        "PEN",
        600000,
        date(2026, 2, 10),
        20.1,
        "TEA",
        "FRANCES",
        36,
        0,
    ),
    (
        "FIN-BBVA-002",
        "DPH",
        "BBVA",
        "BANCO",
        "PEN",
        450000,
        date(2026, 4, 12),
        20.1,
        "TEA",
        "FRANCES",
        24,
        0,
    ),
    (
        "FIN-BBVA-003",
        "DPH Carga",
        "BBVA",
        "BANCO",
        "PEN",
        200000,
        date(2026, 5, 8),
        20.1,
        "TEA",
        "FRANCES",
        24,
        0,
    ),
    (
        "FIN-ARE-001",
        "DPHC",
        "Caja Arequipa",
        "CAJA",
        "PEN",
        350000,
        date(2026, 3, 5),
        28.0,
        "TEA",
        "FRANCES",
        24,
        0,
    ),
    (
        "FIN-ARE-002",
        "DPH",
        "Caja Arequipa",
        "CAJA",
        "PEN",
        250000,
        date(2026, 6, 15),
        28.0,
        "TEA",
        "FRANCES",
        18,
        0,
    ),
    (
        "FIN-PIURA-001",
        "DPHC",
        "Caja Piura",
        "CAJA",
        "PEN",
        900000,
        date(2026, 1, 20),
        24.0,
        "TEA",
        "FRANCES",
        36,
        0,
    ),
    (
        "FIN-PIURA-002",
        "Cosudeco",
        "Caja Piura",
        "CAJA",
        "PEN",
        300000,
        date(2026, 5, 25),
        24.0,
        "TEA",
        "FRANCES",
        24,
        0,
    ),
    (
        "FIN-PIURA-003",
        "DPH Carga",
        "Caja Piura",
        "CAJA",
        "PEN",
        150000,
        date(2026, 8, 3),
        24.0,
        "TEA",
        "FRANCES",
        12,
        0,
    ),
    (
        "FIN-INSALES-001",
        "DPHC",
        "Insales Capital",
        "INVERSIONISTA",
        "PEN",
        1200000,
        date(2026, 3, 18),
        26.0,
        "TEA",
        "FRANCES",
        24,
        0,
    ),
    (
        "FIN-INSALES-002",
        "DPH",
        "Insales Capital",
        "INVERSIONISTA",
        "PEN",
        600000,
        date(2026, 7, 7),
        26.0,
        "TEA",
        "FRANCES",
        24,
        0,
    ),
    (
        "FIN-IO-001",
        "DPHC",
        "Inversiones IO",
        "INVERSIONISTA",
        "PEN",
        350000,
        date(2026, 2, 2),
        20.0,
        "TNA",
        "BULLET",
        12,
        0.09,
    ),
    (
        "FIN-IO-002",
        "DPHC",
        "Inversiones IO",
        "INVERSIONISTA",
        "USD",
        100000,
        date(2026, 4, 20),
        20.0,
        "TNA",
        "BULLET",
        12,
        0.09,
    ),
    (
        "FIN-IO-003",
        "DPH",
        "Inversiones IO",
        "INVERSIONISTA",
        "PEN",
        250000,
        date(2026, 6, 1),
        20.0,
        "TNA",
        "BULLET",
        10,
        0.09,
    ),
    (
        "PAG-001",
        "DPHC",
        "Pagaré - acreedor 01",
        "PAGARE",
        "PEN",
        2400000,
        date(2026, 6, 15),
        19.0,
        "TNA",
        "BULLET",
        6,
        0,
    ),
    (
        "PAG-002",
        "DPHC",
        "Pagaré - acreedor 02",
        "PAGARE",
        "PEN",
        1200000,
        date(2026, 5, 10),
        19.0,
        "TNA",
        "BULLET",
        14,
        0,
    ),
    (
        "PAG-003",
        "DPH",
        "Pagaré - acreedor 03",
        "PAGARE",
        "PEN",
        800000,
        date(2026, 7, 20),
        18.0,
        "TNA",
        "BULLET",
        12,
        0,
    ),
    (
        "PAG-004",
        "DPH",
        "Pagaré - acreedor 04",
        "PAGARE",
        "PEN",
        500000,
        date(2026, 8, 12),
        18.0,
        "TNA",
        "BULLET",
        9,
        0,
    ),
    (
        "PAG-005",
        "Cosudeco",
        "Pagaré - acreedor 05",
        "PAGARE",
        "PEN",
        300000,
        date(2026, 9, 1),
        18.0,
        "TNA",
        "BULLET",
        12,
        0,
    ),
    (
        "TARJ-001",
        "Cosudeco",
        "BBVA",
        "TARJETA",
        "PEN",
        240000,
        date(2026, 7, 1),
        0.0,
        "TEA",
        "OTRO",
        6,
        0,
    ),
    (
        "PERS-001",
        None,
        "BBVA",
        "BANCO",
        "PEN",
        300000,
        date(2026, 3, 1),
        18.0,
        "TEA",
        "FRANCES",
        60,
        0,
    ),
    (
        "PERS-002",
        None,
        "Mi Banco",
        "BANCO",
        "PEN",
        40385,
        date(2026, 5, 4),
        52.2,
        "TEA",
        "FRANCES",
        24,
        0,
    ),
]


def _q(x):
    return Decimal(str(round(x, 2)))


def cronograma(sistema, capital, tasa, tipo_tasa, n, comision, desembolso):
    """Devuelve [(fecha, saldo_inicial, interes, capital, otros, total)] por cuota."""
    filas, saldo = [], capital
    dia = min(desembolso.day, 28)
    if sistema == "FRANCES":
        r = (1 + tasa / 100) ** (1 / 12) - 1 if tipo_tasa == "TEA" else tasa / 100 / 12
        cuota = capital * r / (1 - (1 + r) ** -n)
        for k in range(1, n + 1):
            interes = saldo * r
            amort = cuota - interes if k < n else saldo
            otros = saldo * 0.0005  # seguro de desgravamen
            filas.append(
                (
                    sumar_meses(desembolso, k).replace(day=dia),
                    saldo,
                    interes,
                    amort,
                    otros,
                    interes + amort + otros,
                )
            )
            saldo -= amort
    elif sistema == "BULLET":
        r = tasa / 100 / 12
        for k in range(1, n + 1):
            interes = capital * r
            amort = capital if k == n else 0.0
            otros = (
                capital * comision * 1.18 if k == 1 else 0.0
            )  # comisión de estructuración + IGV
            filas.append(
                (
                    sumar_meses(desembolso, k).replace(day=dia),
                    capital,
                    interes,
                    amort,
                    otros,
                    interes + amort + otros,
                )
            )
    else:  # cuotas iguales sin interés (tarjeta)
        for k in range(1, n + 1):
            filas.append(
                (
                    sumar_meses(desembolso, k).replace(day=dia),
                    saldo,
                    0.0,
                    capital / n,
                    0.0,
                    capital / n,
                )
            )
            saldo -= capital / n
    return filas


def generar(rng: random.Random, est):
    corte = est.corte
    n_cuotas = n_pagos = 0
    for (
        codigo,
        deudor,
        acreedor,
        tipo,
        moneda,
        capital,
        desembolso,
        tasa,
        tipo_tasa,
        sistema,
        n,
        comision,
    ) in PRESTAMOS:
        p = Prestamo.objects.create(
            codigo=codigo,
            deudor=est.empresas[deudor] if deudor else None,
            es_personal=deudor is None,
            acreedor=acreedor,
            tipo=tipo,
            moneda=moneda,
            capital=Decimal(capital),
            fecha_desembolso=desembolso,
            tasa=Decimal(str(tasa)),
            tipo_tasa=tipo_tasa,
            sistema=sistema,
            n_cuotas=n,
        )
        cuotas = [
            Cuota(
                prestamo=p,
                n_cuota=k,
                fecha_vencimiento=f,
                saldo_inicial=_q(s),
                interes=_q(i),
                capital=_q(c),
                otros_costos=_q(o),
                total_cuota=_q(t),
            )
            for k, (f, s, i, c, o, t) in enumerate(
                cronograma(sistema, capital, tasa, tipo_tasa, n, comision, desembolso),
                start=1,
            )
        ]
        Cuota.objects.bulk_create(cuotas)
        n_cuotas += len(cuotas)
        pagos = []
        for c in Cuota.objects.filter(
            prestamo=p, fecha_vencimiento__lte=corte
        ).order_by("fecha_vencimiento"):
            # unas pocas cuotas recientes quedan sin pagar para que aparezca mora
            reciente = (corte - c.fecha_vencimiento).days <= 20
            if reciente and rng.random() < 0.12:
                continue
            pagos.append(
                PagoCuota(
                    cuota=c,
                    fecha_pago=min(
                        c.fecha_vencimiento - timedelta(days=rng.randint(0, 4)), corte
                    ),
                    monto_pagado=c.total_cuota,
                    nro_operacion=f"{rng.randint(100000, 999999)}",
                )
            )
        PagoCuota.objects.bulk_create(pagos)
        n_pagos += len(pagos)
    return {"prestamos": len(PRESTAMOS), "cuotas": n_cuotas, "pagos": n_pagos}
