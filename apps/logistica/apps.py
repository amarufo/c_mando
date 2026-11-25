from django.apps import AppConfig


class LogisticaConfig(AppConfig):
    name = "apps.logistica"
    label = "logistica"
    verbose_name = "Logística y pagos"

    def ready(self):
        from apps.core.dashboard import AreaDashboard, registrar_area

        from . import dashboard, kpis  # noqa: F401

        registrar_area(
            AreaDashboard(
                slug="logistica",
                titulo="Logística y pagos",
                icono="bi-cart-check",
                descripcion="Compras, tiempos de ciclo y cuentas por pagar.",
                construir=dashboard.construir,
                orden=20,
                grafico_resumen=dashboard.para_resumen,
            )
        )
