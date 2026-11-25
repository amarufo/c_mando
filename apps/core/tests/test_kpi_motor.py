from datetime import date

from django.test import SimpleTestCase

from apps.core import kpi
from apps.core.kpi import Contexto, DefinicionKPI, Valor, evaluar, formatear


def definicion(direccion, alerta=None, critico=None):
    return DefinicionKPI(
        "T1",
        "x",
        "prueba",
        "pct",
        direccion,
        alerta,
        critico,
        "",
        "",
        "M",
        "A",
        "",
        False,
        lambda ctx: Valor(1),
    )


class SemaforoTests(SimpleTestCase):
    def test_mayor_es_mejor(self):
        d = definicion("mayor", alerta=0.9, critico=0.75)
        self.assertEqual(evaluar(d, 1.0), "ok")
        self.assertEqual(evaluar(d, 0.9), "ok")
        self.assertEqual(evaluar(d, 0.8), "alerta")
        self.assertEqual(evaluar(d, 0.5), "critico")

    def test_menor_es_mejor(self):
        d = definicion("menor", alerta=20, critico=40)
        self.assertEqual(evaluar(d, 10), "ok")
        self.assertEqual(evaluar(d, 30), "alerta")
        self.assertEqual(evaluar(d, 50), "critico")

    def test_sin_datos_y_neutro(self):
        self.assertEqual(evaluar(definicion("mayor", 1, 0), None), "sin_datos")
        self.assertEqual(evaluar(definicion("ninguna"), 5), "neutro")

    def test_umbral_configurado_reemplaza_al_del_codigo(self):
        d = definicion("menor", alerta=20, critico=40)
        self.assertEqual(evaluar(d, 30, alerta=35, critico=60), "ok")


class FormatoTests(SimpleTestCase):
    def test_formatos(self):
        self.assertEqual(formatear(1_234_567, "pen"), "S/ 1.23 M")
        self.assertEqual(formatear(12_345, "pen"), "S/ 12,345")
        self.assertEqual(formatear(12.34, "pct"), "12.3 %")
        self.assertEqual(formatear(0.956, "ratio"), "0.96")
        self.assertEqual(formatear(None, "pen"), "—")


class RegistroTests(SimpleTestCase):
    def test_no_permite_codigos_duplicados(self):
        with self.assertRaises(ValueError):
            kpi.kpi(codigo="P3", area="proyectos", nombre="duplicado", unidad="ratio")(
                lambda ctx: Valor(1)
            )

    def test_un_kpi_que_falla_no_rompe_el_calculo(self):
        @kpi.kpi(codigo="ZZ1", area="prueba", nombre="falla", unidad="n")
        def falla(ctx):
            raise RuntimeError("error de prueba")

        try:
            with self.assertLogs("apps.core.kpi", level="ERROR"):
                r = kpi.calcular("ZZ1", Contexto(corte=date(2026, 11, 12)), configs={})
            self.assertEqual(r.estado, "error")
            self.assertIsNone(r.valor)
        finally:
            kpi.REGISTRO.pop("ZZ1")

    def test_todas_las_areas_tienen_kpi_con_formula_y_fuente(self):
        for codigo, d in kpi.REGISTRO.items():
            if codigo.startswith("ZZ"):
                continue
            self.assertTrue(d.formula and d.fuente, f"{codigo} sin fórmula o fuente")
