from django.apps import AppConfig


class PrestamosConfig(AppConfig):
    name = "apps.prestamos"
    label = "prestamos"
    verbose_name = "Préstamos y deuda"

    def ready(self):
        from apps.core.dashboard import AreaDashboard, registrar_area

        from . import dashboard, kpis  # noqa: F401

        registrar_area(
            AreaDashboard(
                slug="prestamos",
                titulo="Préstamos y deuda",
                icono="bi-bank",
                descripcion="Deuda vigente, vencimientos y costo financiero.",
                construir=dashboard.construir,
                orden=30,
                grafico_resumen=dashboard.para_resumen,
            )
        )
