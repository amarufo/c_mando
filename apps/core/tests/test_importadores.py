from datetime import date
from decimal import Decimal

import pandas as pd
from django.test import TestCase

from apps.core import importers
from apps.core.models import CargaArchivo
from apps.proyectos.models import Gasto

from .base import catalogos, proyecto_basico


class ConversionTests(TestCase):
    def col(self, **kw):
        return importers.Columna(**{"nombre": "x", "tipo": "texto", **kw})

    def test_tipos_basicos(self):
        self.assertEqual(
            importers.convertir(self.col(tipo="fecha"), "2026-11-12"),
            date(2026, 11, 12),
        )
        self.assertEqual(
            importers.convertir(self.col(tipo="fecha"), "12/11/2026"),
            date(2026, 11, 12),
        )
        self.assertEqual(
            importers.convertir(self.col(tipo="numero"), "1,234.50"), Decimal("1234.50")
        )
        self.assertIs(importers.convertir(self.col(tipo="bool"), "SI"), True)
        self.assertEqual(importers.convertir(self.col(tipo="texto"), 1234.0), "1234")

    def test_el_dni_conserva_los_ceros(self):
        self.assertEqual(
            importers.convertir(self.col(tipo="texto"), "01234567"), "01234567"
        )

    def test_lista_cerrada_normaliza_mayusculas(self):
        c = self.col(valores=("PAGADO", "PENDIENTE"))
        self.assertEqual(importers.convertir(c, "pagado"), "PAGADO")
        with self.assertRaises(ValueError):
            importers.convertir(c, "PAGADA")

    def test_obligatorio_vacio_falla_y_opcional_vacio_pasa(self):
        with self.assertRaises(ValueError):
            importers.convertir(self.col(), "  ")
        self.assertEqual(importers.convertir(self.col(obligatorio=False), None), "")
        self.assertIsNone(
            importers.convertir(self.col(tipo="fecha", obligatorio=False), float("nan"))
        )


class CargaDeGastosTests(TestCase):
    def setUp(self):
        self.empresa, self.cc, self.cat, _ = catalogos()
        self.proyecto = proyecto_basico(self.empresa, self.cc)
        importers.descubrir()
        self.imp = importers.IMPORTADORES["proyectos_gastos"]

    def fila(self, **cambios):
        base = {
            "id_gasto": "017-000001",
            "cc2": "017",
            "codigo_categoria": "01.01",
            "fecha": "2026-10-15",
            "fecha_pago_real": "2026-10-16",
            "estado": "PAGADO",
            "naturaleza": "REAL",
            "tipo_gasto": "OPERATIVO",
            "proveedor_ruc": "20123456789",
            "proveedor": "Prov",
            "concepto": "Cemento",
            "moneda": "PEN",
            "monto": "1180.00",
            "con_igv": "SI",
            "tc": "1",
            "nro_orden": "",
            "id_comprobante": "",
        }
        base.update(cambios)
        return base

    def test_archivo_valido_se_guarda_y_calcula_montos(self):
        carga = importers.procesar(self.imp, pd.DataFrame([self.fila()]))
        self.assertEqual(carga.estado, "OK")
        g = Gasto.objects.get()
        self.assertEqual(g.monto_pen, Decimal("1180.00"))
        self.assertEqual(g.monto_pen_sin_igv, Decimal("1000.00"))

    def test_un_error_impide_guardar_cualquier_fila(self):
        df = pd.DataFrame(
            [
                self.fila(),
                self.fila(id_gasto="017-000002", estado="PAGADA"),
                self.fila(id_gasto="017-000003", cc2="999"),
            ]
        )
        carga = importers.procesar(self.imp, df)
        self.assertEqual(carga.estado, "RECHAZADA")
        self.assertEqual(Gasto.objects.count(), 0)
        self.assertEqual(
            {e["fila"] for e in carga.errores}, {3, 4}
        )  # la fila 1 del archivo es el encabezado
        self.assertEqual(carga.filas_error, 2)

    def test_solo_validar_no_guarda(self):
        carga = importers.procesar(self.imp, pd.DataFrame([self.fila()]), guardar=False)
        self.assertEqual(carga.estado, "SIMULACION")
        self.assertEqual(Gasto.objects.count(), 0)

    def test_cargar_dos_veces_actualiza_en_vez_de_duplicar(self):
        importers.procesar(self.imp, pd.DataFrame([self.fila()]))
        importers.procesar(self.imp, pd.DataFrame([self.fila(monto="2360.00")]))
        self.assertEqual(Gasto.objects.count(), 1)
        self.assertEqual(Gasto.objects.get().monto_pen, Decimal("2360.00"))

    def test_clave_repetida_dentro_del_archivo(self):
        carga = importers.procesar(self.imp, pd.DataFrame([self.fila(), self.fila()]))
        self.assertEqual(carga.estado, "RECHAZADA")
        self.assertIn("repetida", carga.errores[0]["error"])

    def test_columnas_obligatorias_faltantes(self):
        df = pd.DataFrame([self.fila()]).drop(columns=["monto"])
        carga = importers.procesar(self.imp, df)
        self.assertEqual(carga.estado, "RECHAZADA")
        self.assertIn("monto", carga.errores[0]["columna"])

    def test_gasto_en_dolares_usa_el_tipo_de_cambio_de_la_tabla(self):
        from apps.core.models import TipoCambio

        TipoCambio.objects.create(
            fecha=date(2026, 10, 15), compra=Decimal("3.40"), venta=Decimal("3.50")
        )
        importers.procesar(
            self.imp,
            pd.DataFrame([self.fila(moneda="USD", monto="100", con_igv="NO", tc="")]),
        )
        self.assertEqual(Gasto.objects.get().monto_pen, Decimal("350.00"))

    def test_exportar_y_volver_a_importar_no_cambia_nada(self):
        importers.procesar(
            self.imp,
            pd.DataFrame([self.fila(), self.fila(id_gasto="017-000002", monto="500")]),
        )
        exportado = importers.exportar(self.imp)
        carga = importers.procesar(self.imp, exportado)
        self.assertEqual(carga.estado, "OK")
        self.assertEqual(Gasto.objects.count(), 2)

    def test_la_carga_queda_registrada(self):
        importers.procesar(
            self.imp, pd.DataFrame([self.fila(estado="X")]), nombre_archivo="malo.csv"
        )
        c = CargaArchivo.objects.get()
        self.assertEqual(
            (c.tabla, c.estado, c.nombre_archivo),
            ("proyectos_gastos", "RECHAZADA", "malo.csv"),
        )


class PlantillasTests(TestCase):
    def test_todas_las_tablas_tienen_columnas_con_ejemplo_y_clave_valida(self):
        for slug, imp in importers.descubrir().items():
            campos = {c.destino for c in imp.columnas}
            for k in imp.clave:
                if (
                    imp.armar is None
                ):  # con `armar`, parte de la clave se resuelve en código
                    self.assertIn(k, campos, f"{slug}: la clave {k} no es una columna")
            self.assertEqual(
                list(importers.plantilla(imp).columns), [c.nombre for c in imp.columnas]
            )
