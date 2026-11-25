"""Comprueba que cada KPI da el número esperado con datos pequeños calculables a mano."""

from datetime import date, datetime, time
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from apps.core import kpi
from apps.core.kpi import Contexto
from apps.logistica.models import Comprobante, Orden, Proveedor, Requerimiento
from apps.prestamos.models import Cuota, PagoCuota, Prestamo
from apps.proyectos.models import Gasto
from apps.rrhh.models import Marcacion, Persona

from .base import CORTE, catalogos, proyecto_basico

CTX = Contexto(corte=CORTE)


def valor(codigo, ctx=CTX):
    return kpi.calcular(codigo, ctx, configs={}).valor


class ProyectosTests(TestCase):
    def setUp(self):
        self.empresa, self.cc, self.cat_obra, self.cat_pre = catalogos()
        self.proyecto = proyecto_basico(self.empresa, self.cc)
        # Costo real de obra: 200,000 sin IGV. El gasto precontractual NO debe contar en el AC.
        Gasto.objects.create(
            id_gasto="G1",
            proyecto=self.proyecto,
            categoria=self.cat_obra,
            fecha=date(2026, 9, 1),
            estado="PAGADO",
            proveedor="P",
            monto=Decimal("236000"),
            con_igv=True,
        )
        Gasto.objects.create(
            id_gasto="G2",
            proyecto=self.proyecto,
            categoria=self.cat_pre,
            fecha=date(2026, 3, 1),
            estado="PAGADO",
            proveedor="P",
            monto=Decimal("50000"),
            con_igv=False,
        )
        Gasto.objects.create(
            id_gasto="G3",
            proyecto=self.proyecto,
            categoria=self.cat_obra,
            fecha=date(2026, 12, 1),
            estado="PENDIENTE",
            naturaleza="PROYECTADO",
            proveedor="P",
            monto=Decimal("10000"),
        )

    def test_avance_real_y_planificado(self):
        self.assertAlmostEqual(valor("P1"), 400000 / 1180000 * 100, places=4)
        self.assertAlmostEqual(valor("P2"), 800000 / 1180000 * 100, places=4)

    def test_spi_es_real_sobre_planificado(self):
        self.assertAlmostEqual(valor("P3"), 0.5, places=6)

    def test_costo_real_excluye_precontractual_proyectado_e_igv(self):
        self.assertAlmostEqual(valor("P4"), 200000, places=2)

    def test_cpi_usa_base_de_costo_meta(self):
        ev = 400000 / 1180000 * 700000
        self.assertAlmostEqual(valor("P5"), ev / 200000, places=4)

    def test_margen_proyectado_con_el_cpi_actual(self):
        cpi = (400000 / 1180000 * 700000) / 200000
        self.assertAlmostEqual(
            valor("P6"), (1_000_000 - 700000 / cpi) / 1_000_000 * 100, places=3
        )

    def test_proyecto_sin_ejecucion_no_aporta_al_valor_ganado(self):
        self.assertIsNone(
            kpi.calcular("P3", Contexto(corte=date(2026, 6, 1)), configs={}).valor
        )

    def test_pendiente_y_precontractual(self):
        self.assertAlmostEqual(valor("P13"), 50000 / 1_000_000 * 100, places=4)
        self.assertEqual(valor("P9"), 0)

    def test_filtro_por_proyecto_sin_coincidencias(self):
        from apps.core.models import CentroCosto

        otro = CentroCosto.objects.create(cc2="099", nombre="OTRO", tipo="PROYECTO")
        self.assertIsNone(valor("P3", Contexto(corte=CORTE, proyecto=otro)))


class LogisticaTests(TestCase):
    def setUp(self):
        self.empresa, self.cc, *_ = catalogos()
        self.prov = Proveedor.objects.create(
            ruc="20111111111", razon_social="Proveedor"
        )

    def comprobante(self, serie, total, venc, estado="PROGRAMADO", pago=None, **extra):
        return Comprobante.objects.create(
            empresa=self.empresa,
            proveedor=self.prov,
            serie_numero=serie,
            centro_costo=self.cc,
            fecha_doc=date(2026, 10, 1),
            fecha_venc=venc,
            base_imponible=total,
            total=total,
            estado_pago=estado,
            fecha_pago_real=pago,
            **extra,
        )

    def test_deuda_vencida_sobre_el_total_por_pagar(self):
        self.comprobante("F1", 300, date(2026, 11, 1))  # vencido
        self.comprobante("F2", 100, date(2026, 11, 30))  # por vencer
        self.comprobante(
            "F3", 999, date(2026, 10, 15), estado="PAGADO", pago=date(2026, 10, 10)
        )  # pagado: no cuenta
        self.assertEqual(valor("L10"), 400)
        self.assertAlmostEqual(valor("L11"), 75.0)

    def test_un_pago_posterior_al_corte_sigue_siendo_deuda_a_esa_fecha(self):
        self.comprobante(
            "F1", 500, date(2026, 10, 20), estado="PAGADO", pago=date(2026, 11, 20)
        )
        self.assertEqual(valor("L10"), 500)

    def test_misma_serie_en_distintos_proveedores_es_valida_pero_no_en_el_mismo(self):
        from django.db import IntegrityError, transaction

        otro = Proveedor.objects.create(ruc="20222222222", razon_social="Otro")
        self.comprobante("E001-13", 100, date(2026, 11, 30))
        Comprobante.objects.create(
            empresa=self.empresa,
            proveedor=otro,
            serie_numero="E001-13",
            centro_costo=self.cc,
            fecha_doc=date(2026, 10, 1),
            fecha_venc=date(2026, 11, 30),
            base_imponible=1,
            total=1,
            estado_pago="PROGRAMADO",
        )
        with self.assertRaises(IntegrityError), transaction.atomic():
            self.comprobante("E001-13", 100, date(2026, 11, 30))

    def test_diferencia_logistica_vs_contabilidad(self):
        self.comprobante("F1", 100, date(2026, 11, 30), total_logistica=100)
        self.comprobante("F2", 100, date(2026, 11, 30), total_logistica=150)
        self.assertAlmostEqual(valor("L15"), 50.0)

    def test_tiempos_y_rechazos_de_requerimientos(self):
        for i, (estado, d_aprob) in enumerate(
            [("FINALIZADO", 0), ("FINALIZADO", 2), ("RECHAZADA", 1)]
        ):
            Requerimiento.objects.create(
                nro=f"RQ{i}",
                empresa=self.empresa,
                centro_costo=self.cc,
                tipo="EMERGENCIA",
                estado=estado,
                fecha_creacion=date(2026, 11, 1),
                fecha_aprobacion=date(2026, 11, 1 + d_aprob),
                n_items=2,
                n_items_con_precio=1,
            )
        self.assertAlmostEqual(valor("L2"), 100 / 3, places=4)
        self.assertAlmostEqual(valor("L5"), 1.0)
        self.assertAlmostEqual(valor("L3"), 100.0)
        self.assertAlmostEqual(valor("Q4"), 50.0)

    def test_orden_con_diferencia_contra_lo_facturado(self):
        Orden.objects.create(
            nro="OC1",
            tipo="OC",
            empresa=self.empresa,
            centro_costo=self.cc,
            proveedor=self.prov,
            estado="POR_PAGAR",
            condicion_pago="CREDITO_30",
            total=Decimal("1000"),
            fecha_emision=date(2026, 10, 1),
        )
        self.comprobante("F1", 600, date(2026, 11, 30), nro_orden="OC1")
        self.assertAlmostEqual(valor("L14"), 100.0)


class PrestamosTests(TestCase):
    def setUp(self):
        self.empresa, *_ = catalogos()
        self.p = Prestamo.objects.create(
            codigo="P1",
            deudor=self.empresa,
            acreedor="Banco",
            tipo="BANCO",
            capital=1000,
            fecha_desembolso=date(2026, 1, 1),
            tasa=10,
            sistema="FRANCES",
            n_cuotas=3,
        )
        self.cuotas = [
            Cuota.objects.create(
                prestamo=self.p,
                n_cuota=k,
                fecha_vencimiento=f,
                saldo_inicial=1000,
                interes=10,
                capital=300,
                total_cuota=310,
            )
            for k, f in (
                (1, date(2026, 10, 15)),
                (2, date(2026, 11, 5)),
                (3, date(2026, 12, 15)),
            )
        ]
        PagoCuota.objects.create(
            cuota=self.cuotas[0], fecha_pago=date(2026, 10, 14), monto_pagado=310
        )

    def test_deuda_vigente_descuenta_cuotas_pagadas(self):
        self.assertEqual(valor("F1"), 600)

    def test_mora_es_la_cuota_vencida_sin_pago(self):
        self.assertEqual(valor("F8"), 310)  # la cuota del 5/11 venció y no tiene pago

    def test_vencimientos_a_90_dias_no_incluyen_lo_vencido(self):
        self.assertEqual(valor("F3"), 310)

    def test_costo_financiero_y_realizado(self):
        r = kpi.calcular("F4", CTX, configs={})
        self.assertEqual(r.valor, 30)
        self.assertIn("33 %", r.nota)

    def test_el_pago_debe_existir_a_la_fecha_de_corte(self):
        antes = Contexto(corte=date(2026, 10, 10))
        self.assertEqual(kpi.calcular("F1", antes, configs={}).valor, 900)

    def test_deuda_personal_se_puede_excluir(self):
        Prestamo.objects.create(
            codigo="PERS",
            deudor=None,
            es_personal=True,
            acreedor="Banco",
            tipo="BANCO",
            capital=500,
            fecha_desembolso=date(2026, 1, 1),
            tasa=10,
            sistema="FRANCES",
            n_cuotas=1,
        )
        pers = Prestamo.objects.get(codigo="PERS")
        Cuota.objects.create(
            prestamo=pers,
            n_cuota=1,
            fecha_vencimiento=date(2026, 12, 1),
            saldo_inicial=500,
            interes=0,
            capital=500,
            total_cuota=500,
        )
        self.assertEqual(valor("F1"), 1100)
        self.assertEqual(
            valor("F1", Contexto(corte=CORTE, incluir_personal=False)), 600
        )


class RrhhTests(TestCase):
    def setUp(self):
        self.empresa, self.cc, *_ = catalogos()

    def persona(self, dni, **kw):
        datos = dict(
            dni=dni,
            apellidos_nombres=f"PRUEBA {dni}",
            empresa=self.empresa,
            centro_costo=self.cc,
            cargo="X",
            categoria="MANO_OBRA",
            condicion="PLANILLA",
            fecha_ingreso=date(2026, 1, 1),
            sueldo_base=Decimal("3000"),
            codigo_reloj=dni,
        )
        datos.update(kw)
        return Persona.objects.create(**datos)

    def test_dotacion_excluye_ceses_y_futuros_ingresos(self):
        self.persona("11111111")
        self.persona("22222222", fecha_cese=date(2026, 10, 1))
        self.persona("33333333", fecha_ingreso=date(2026, 12, 1))
        self.assertEqual(valor("H1"), 1)

    def test_tardanza_con_tolerancia_de_10_minutos(self):
        p = self.persona("11111111")
        for dia, hora in (
            (9, time(8, 5)),
            (10, time(8, 11)),
            (11, time(7, 50)),
        ):  # solo el 10/11 es tardanza
            Marcacion.objects.create(
                codigo_reloj="11111111",
                persona=p,
                fecha_hora=timezone.make_aware(
                    datetime.combine(date(2026, 11, dia), hora)
                ),
            )
            Marcacion.objects.create(
                codigo_reloj="11111111",
                persona=p,
                fecha_hora=timezone.make_aware(
                    datetime.combine(date(2026, 11, dia), time(17, 30))
                ),
            )
        self.assertAlmostEqual(valor("H6"), 100 / 3, places=3)

    def test_contratos_por_elaborar_y_por_vencer(self):
        self.persona("11111111", estado_contrato="ELABORAR")
        self.persona("22222222", fecha_fin_contrato=date(2026, 11, 30))
        self.persona("33333333", fecha_fin_contrato=date(2027, 6, 30))
        self.assertEqual(valor("H8"), 2)
