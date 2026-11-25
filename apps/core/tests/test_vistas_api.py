from datetime import date

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from rest_framework.authtoken.models import Token

from apps.core.models import KPISnapshot

from .base import catalogos, proyecto_basico


class VistasTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("crear_grupos", verbosity=0)
        cls.empresa, cls.cc, *_ = catalogos()
        proyecto_basico(cls.empresa, cls.cc)
        KPISnapshot.objects.create(
            codigo="P3", fecha_corte=date(2026, 11, 12), valor=0.5, estado="critico"
        )
        User = get_user_model()
        cls.gerente = User.objects.create_user("g", password="x")
        cls.gerente.groups.add(Group.objects.get(name="gerencia"))
        cls.rrhh = User.objects.create_user("r", password="x")
        cls.rrhh.groups.add(Group.objects.get(name="rrhh"))

    def test_exige_iniciar_sesion(self):
        r = self.client.get(reverse("resumen"))
        self.assertEqual(r.status_code, 302)
        self.assertIn("/ingresar/", r["Location"])

    def test_salud_no_exige_sesion(self):
        self.assertEqual(self.client.get(reverse("salud")).status_code, 200)

    def test_gerencia_ve_el_resumen_y_todas_las_areas(self):
        self.client.force_login(self.gerente)
        self.assertContains(self.client.get(reverse("resumen")), "Resumen gerencial")
        for slug in ("proyectos", "logistica", "prestamos", "rrhh", "calidad"):
            r = self.client.get(reverse("area", args=[slug]))
            self.assertEqual(r.status_code, 200, slug)

    def test_cada_area_solo_la_ve_su_grupo(self):
        self.client.force_login(self.rrhh)
        self.assertEqual(
            self.client.get(reverse("area", args=["rrhh"])).status_code, 200
        )
        self.assertEqual(
            self.client.get(reverse("area", args=["prestamos"])).status_code, 403
        )
        resumen = self.client.get(reverse("resumen")).content.decode()
        self.assertNotIn("Deuda vigente", resumen)
        self.assertIn("Dotación activa", resumen)

    def test_area_inexistente_es_404(self):
        self.client.force_login(self.gerente)
        self.assertEqual(self.client.get(reverse("area", args=["xx"])).status_code, 404)

    def test_filtros_invalidos_se_ignoran(self):
        self.client.force_login(self.gerente)
        r = self.client.get(
            reverse("area", args=["proyectos"]),
            {"corte": "no-es-fecha", "empresa": "000", "proyecto": "zzz"},
        )
        self.assertEqual(r.status_code, 200)

    def test_diccionario_y_detalle_de_kpi(self):
        self.client.force_login(self.gerente)
        self.assertContains(self.client.get(reverse("diccionario")), "SPI")
        self.assertEqual(
            self.client.get(reverse("kpi_detalle", args=["P3"])).status_code, 200
        )
        self.assertEqual(
            self.client.get(reverse("kpi_detalle", args=["NOEXISTE"])).status_code, 404
        )

    def test_carga_manual_rechaza_y_acepta(self):
        self.client.force_login(self.gerente)
        malo = SimpleUploadedFile(
            "t.csv", "ruc,razon_social\n123,Sin nombre corto\n".encode()
        )
        r = self.client.post(
            reverse("cargas"), {"tabla": "cat_empresa", "archivo": malo}
        )
        self.assertContains(r, "Rechazado")
        bueno = SimpleUploadedFile(
            "t.csv",
            "ruc,razon_social,nombre_corto\n20999999999,Nueva SAC,NUE\n".encode(),
        )
        self.client.post(reverse("cargas"), {"tabla": "cat_empresa", "archivo": bueno})
        from apps.core.models import Empresa

        self.assertTrue(Empresa.objects.filter(ruc="20999999999").exists())

    def test_un_usuario_de_area_no_carga_tablas_de_otra_area(self):
        self.client.force_login(self.rrhh)
        r = self.client.get(reverse("plantilla_csv", args=["prestamos_cuotas"]))
        self.assertEqual(r.status_code, 404)
        self.assertEqual(
            self.client.get(
                reverse("plantilla_csv", args=["rrhh_personal"])
            ).status_code,
            200,
        )


class ApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("crear_grupos", verbosity=0)
        cls.empresa, cls.cc, *_ = catalogos()
        cls.usuario = get_user_model().objects.create_user("api", password="x")
        cls.usuario.groups.add(Group.objects.get(name="gerencia"))
        cls.token = Token.objects.create(user=cls.usuario)

    def cabecera(self):
        return {"HTTP_AUTHORIZATION": f"Token {self.token.key}"}

    def test_api_exige_token(self):
        self.assertEqual(self.client.get("/api/v1/kpis/").status_code, 401)

    def test_lista_de_kpi(self):
        r = self.client.get("/api/v1/kpis/", **self.cabecera())
        self.assertEqual(r.status_code, 200)
        self.assertIn("P3", {k["codigo"] for k in r.json()["kpi"]})

    def test_carga_por_api_con_filas_json(self):
        fila = {
            "ruc": "20888888888",
            "razon_social": "Por API SAC",
            "nombre_corto": "API",
        }
        r = self.client.post(
            "/api/v1/cargas/cat_empresa/",
            {"filas": [fila]},
            content_type="application/json",
            **self.cabecera(),
        )
        self.assertEqual(r.status_code, 201, r.content)
        r = self.client.post(
            "/api/v1/cargas/cat_empresa/",
            {"filas": [{"ruc": "1"}]},
            content_type="application/json",
            **self.cabecera(),
        )
        self.assertEqual(r.status_code, 422)
        self.assertTrue(r.json()["errores"])

    def test_validar_no_guarda(self):
        fila = {
            "ruc": "20777777777",
            "razon_social": "Solo validar",
            "nombre_corto": "SV",
        }
        r = self.client.post(
            "/api/v1/cargas/cat_empresa/?validar=1",
            {"filas": [fila]},
            content_type="application/json",
            **self.cabecera(),
        )
        self.assertEqual(r.json()["estado"], "SIMULACION")
        from apps.core.models import Empresa

        self.assertFalse(Empresa.objects.filter(ruc="20777777777").exists())
