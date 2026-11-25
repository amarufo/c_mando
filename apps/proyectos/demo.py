"""Datos de ejemplo de Proyectos: ficha, presupuesto, valorizaciones mensuales y gastos."""

import math
import random
from datetime import date, timedelta
from decimal import Decimal

from apps.core.demo import nombre_empresa_falsa, ruc_falso
from apps.core.models import Categoria
from apps.core.services import fin_de_mes, primer_dia, sumar_meses

from .models import Gasto, PresupuestoEscenario, Proyecto, Valorizacion

# cc2, nombre, CUI, código, entidad, ubicación, acta ET, plazo ET, acta EO, plazo EO, contrato con IGV, ritmo (real/plan), costo/contrato sin IGV
FICHAS = [
    (
        "017",
        "Polideportivo Ccollana",
        "2686704",
        "0103",
        "Municipalidad Provincial (ejemplo)",
        "Ayacucho, Huanta",
        date(2026, 4, 4),
        60,
        date(2026, 7, 17),
        150,
        6072509,
        0.55,
        0.60,
    ),
    (
        "018",
        "Mejoramiento de carretera JU-104",
        "2650011",
        "0104",
        "Gobierno Regional (ejemplo)",
        "Junín",
        date(2026, 2, 16),
        60,
        date(2026, 5, 4),
        240,
        9800000,
        0.95,
        0.66,
    ),
    (
        "019",
        "Reservorio Iguain",
        "2641022",
        "0105",
        "Municipalidad Distrital (ejemplo)",
        "Ayacucho",
        date(2026, 3, 23),
        60,
        date(2026, 6, 1),
        180,
        3900000,
        0.86,
        0.73,
    ),
    (
        "025",
        "Puente Chacarilla Mencia",
        "2660033",
        "0106",
        "Gobierno Regional (ejemplo)",
        "Ica, Pisco",
        date(2026, 4, 6),
        60,
        date(2026, 6, 15),
        150,
        2400000,
        1.00,
        0.63,
    ),
    (
        "037",
        "Defensa ribereña Cherrelique",
        "2670044",
        "0107",
        "Municipalidad Provincial (ejemplo)",
        "Tumbes",
        date(2026, 3, 2),
        60,
        date(2026, 5, 18),
        210,
        4600000,
        0.80,
        0.78,
    ),
    (
        "044",
        "Canal de riego Mochumi",
        "2680055",
        "0108",
        "Gobierno Regional (ejemplo)",
        "Lambayeque",
        date(2026, 5, 4),
        60,
        date(2026, 7, 6),
        150,
        2900000,
        0.92,
        0.69,
    ),
    (
        "061",
        "Defensa ribereña río Chochope",
        "2690066",
        "0109",
        "Autoridad Nacional (ejemplo)",
        "Lambayeque",
        date(2026, 2, 23),
        55,
        date(2026, 4, 20),
        240,
        5200000,
        0.97,
        0.67,
    ),
    (
        "065",
        "Canal Taymi 2",
        "2700077",
        "0110",
        "Gobierno Regional (ejemplo)",
        "Lambayeque",
        date(2026, 6, 1),
        60,
        date(2026, 8, 3),
        150,
        3300000,
        0.84,
        0.71,
    ),
]
PORCENTAJE_IGV = Decimal("1.18")


def _d(x, nd=2):
    return Decimal(str(round(x, nd)))


def _meses(inicio: date, fin: date):
    m, lista = primer_dia(inicio), []
    while m <= fin:
        lista.append(m)
        m = sumar_meses(m, 1)
    return lista


def generar(rng: random.Random, est):
    corte = est.corte
    cats = {}
    for c in est.categorias:
        cats.setdefault(c.componente, []).append(c)
    pool_proveedores = [
        (ruc_falso(rng, set()), nombre_empresa_falsa(rng)) for _ in range(60)
    ]
    n_gastos = 0

    for (
        cc2,
        nombre,
        cui,
        codigo,
        entidad,
        ubic,
        acta_et,
        plazo_et,
        acta_eo,
        plazo_eo,
        contrato,
        ritmo,
        costo,
    ) in FICHAS:
        cc = est.cc[cc2]
        proy = Proyecto.objects.create(
            centro_costo=cc,
            nombre=nombre,
            cui=cui,
            codigo=codigo,
            entidad=entidad,
            ubicacion=ubic,
            fecha_acta_et=acta_et,
            plazo_et_dias=plazo_et,
            fecha_acta_eo=acta_eo,
            plazo_eo_dias=plazo_eo,
            monto_contrato=Decimal(contrato),
        )
        est.proyectos[cc2] = proy
        contrato_sin = contrato / 1.18
        cd = contrato_sin / 1.23
        PresupuestoEscenario.objects.bulk_create(
            [
                PresupuestoEscenario(
                    proyecto=proy,
                    escenario="CONTRATO",
                    costo_directo=_d(cd),
                    gg_pct=Decimal("0.13"),
                    utilidad_pct=Decimal("0.10"),
                    supervision=_d(contrato * 0.044),
                    expediente_tecnico=_d(contrato * 0.032),
                    liquidacion=_d(contrato * 0.001),
                ),
                PresupuestoEscenario(
                    proyecto=proy,
                    escenario="META",
                    costo_directo=_d(cd * 0.7),
                    gg_pct=Decimal("0.13"),
                    utilidad_pct=Decimal("0.10"),
                    supervision=_d(contrato * 0.044 * 0.7),
                    expediente_tecnico=_d(contrato * 0.032 * 0.7),
                    liquidacion=_d(contrato * 0.001 * 0.7),
                ),
                PresupuestoEscenario(
                    proyecto=proy,
                    escenario="PROPUESTO",
                    costo_directo=_d(cd * rng.uniform(0.70, 0.74)),
                    gg_pct=Decimal("0.05"),
                    utilidad_pct=Decimal("0.05"),
                ),
            ]
        )

        # --- Valorizaciones: curva S planificada y avance real de los meses cerrados ---
        fin_eo = acta_eo + timedelta(days=plazo_eo)
        meses = _meses(acta_eo, fin_eo)
        pesos = [
            math.sin(math.pi * (i + 0.5) / len(meses)) ** 2 for i in range(len(meses))
        ]
        suma = sum(pesos)
        valorizaciones, real_acum = [], 0.0
        plan_mes = {}
        for m, w in zip(meses, pesos):
            plan = contrato * w / suma
            plan_mes[m] = plan
            real = cobrado = fecha_cobro = None
            if m < primer_dia(corte):
                real = min(plan * ritmo * rng.uniform(0.9, 1.1), contrato - real_acum)
                real_acum += real
                cobro = fin_de_mes(m) + timedelta(days=rng.randint(20, 40))
                if cobro <= corte:
                    cobrado, fecha_cobro = _d(real * 0.97), cobro
                real = _d(real)
            valorizaciones.append(
                Valorizacion(
                    proyecto=proy,
                    periodo=m,
                    monto_planificado=_d(plan),
                    monto_real=real,
                    monto_cobrado=cobrado,
                    fecha_cobro=fecha_cobro,
                )
            )
        Valorizacion.objects.bulk_create(valorizaciones)

        # --- Gastos ---
        gastos, contador = [], [0]

        def nuevo(
            fecha,
            categoria,
            monto_sin_igv,
            estado,
            naturaleza,
            tipo="OPERATIVO",
            concepto="",
            con_igv=True,
            usd=False,
        ):
            contador[0] += 1
            ruc, prov = rng.choice(pool_proveedores)
            monto = monto_sin_igv * (1.18 if con_igv else 1.0)
            moneda, tc = "PEN", Decimal(1)
            if usd:
                moneda, tc = "USD", est.conversor.tc(fecha)
                monto = float(Decimal(str(monto)) / tc)
            g = Gasto(
                id_gasto=f"{cc2}-{contador[0]:06d}",
                proyecto=proy,
                categoria=categoria,
                fecha=fecha,
                estado=estado,
                naturaleza=naturaleza,
                tipo_gasto=tipo,
                proveedor_ruc=ruc,
                proveedor=prov,
                concepto=concepto or categoria.item,
                moneda=moneda,
                monto=_d(monto),
                con_igv=con_igv,
                tc=tc,
                fecha_pago_real=(
                    min(fecha + timedelta(days=rng.randint(0, 5)), corte)
                    if estado == "PAGADO"
                    else None
                ),
            )
            ordenes = est.ordenes_por_cc.get(cc2)
            if (
                tipo == "OPERATIVO"
                and categoria.componente in ("01", "02", "05")
                and ordenes
                and rng.random() < 0.6
            ):
                g.nro_orden = rng.choice(ordenes)
            g.calcular_montos()
            gastos.append(g)

        def lineas(
            inicio, fin, total_sin_igv, componentes, naturaleza="REAL", tamano=11000
        ):
            n = max(1, int(total_sin_igv / tamano))
            for _ in range(n):
                fecha = inicio + timedelta(
                    days=rng.randint(0, max(0, (fin - inicio).days))
                )
                comp = rng.choices(
                    list(componentes), weights=list(componentes.values())
                )[0]
                cat = rng.choice(cats[comp])
                monto = total_sin_igv / n * rng.uniform(0.4, 1.6)
                if naturaleza == "PROYECTADO":
                    estado = "PENDIENTE"
                elif fecha <= corte - timedelta(days=10):
                    estado = "PAGADO" if rng.random() < 0.97 else "PENDIENTE"
                else:
                    estado = "PAGADO" if rng.random() < 0.6 else "PENDIENTE"
                tipo = "RRHH" if cat.categoria_especial == "Laboral" else "OPERATIVO"
                nuevo(
                    fecha,
                    cat,
                    monto,
                    estado,
                    naturaleza,
                    tipo,
                    con_igv=rng.random() < 0.88,
                    usd=rng.random() < 0.04,
                )

        lineas(acta_et - timedelta(days=100), acta_et, contrato_sin * 0.06, {"00": 1})
        lineas(
            acta_et,
            acta_et + timedelta(days=plazo_et),
            contrato_sin * 0.05,
            {"03": 9, "04": 1},
        )
        componentes_obra = {"01": 70, "02": 22, "05": 8}
        for m, plan in plan_mes.items():
            if m < primer_dia(corte):  # mes cerrado: costo proporcional a lo valorizado
                real = float(
                    next(v.monto_real for v in valorizaciones if v.periodo == m)
                )
                lineas(
                    max(m, acta_eo),
                    fin_de_mes(m),
                    real / 1.18 * costo * rng.uniform(0.93, 1.07),
                    componentes_obra,
                )
            elif m <= corte:  # mes en curso: devengado parcial
                transcurrido = max((corte - m).days + 1, 1) / 30
                lineas(
                    m,
                    corte,
                    plan / 1.18 * ritmo * costo * transcurrido,
                    componentes_obra,
                )
                lineas(
                    corte + timedelta(days=1),
                    fin_de_mes(m),
                    plan / 1.18 * ritmo * costo * max(1 - transcurrido, 0),
                    componentes_obra,
                    "PROYECTADO",
                )
            else:
                lineas(
                    m,
                    fin_de_mes(m),
                    plan / 1.18 * ritmo * costo,
                    componentes_obra,
                    "PROYECTADO",
                )
            if (
                m <= corte
            ):  # pagos de préstamo y reembolsos que se cargaron al proyecto (costo no operativo)
                tope = min(fin_de_mes(m), corte)
                fecha_prestamo = min(
                    max(m, acta_eo) + timedelta(days=rng.randint(0, 20)), tope
                )
                nuevo(
                    fecha_prestamo,
                    cats["3101"][0],
                    rng.uniform(8000, 22000),
                    "PAGADO",
                    "REAL",
                    "PRESTAMO",
                    "Cuota de préstamo del proyecto",
                    con_igv=False,
                )
                for _ in range(rng.randint(0, 2)):
                    nuevo(
                        tope - timedelta(days=rng.randint(0, 10)),
                        cats["3101"][0],
                        rng.uniform(800, 3500),
                        "PAGADO",
                        "REAL",
                        "REEMBOLSO",
                        "Reembolso de gastos",
                        con_igv=False,
                    )
        Gasto.objects.bulk_create(gastos, batch_size=500)
        n_gastos += len(gastos)
    return {"proyectos": len(FICHAS), "gastos": n_gastos}
