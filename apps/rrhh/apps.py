from django.apps import AppConfig


class RrhhConfig(AppConfig):
    name = "apps.rrhh"
    label = "rrhh"
    verbose_name = "Recursos humanos"

    def ready(self):
        from apps.core.dashboard import AreaDashboard, registrar_area

        from . import dashboard, kpis  # noqa: F401

        registrar_area(
            AreaDashboard(
                slug="rrhh",
                titulo="Recursos humanos",
                icono="bi-people",
                descripcion="Dotación, costo de personal, asistencia y obligaciones.",
                construir=dashboard.construir,
                orden=40,
                grafico_resumen=dashboard.para_resumen,
            )
        )
