from django.apps import AppConfig


class ProyectosConfig(AppConfig):
    name = "apps.proyectos"
    label = "proyectos"
    verbose_name = "Proyectos"

    def ready(self):
        from apps.core.dashboard import AreaDashboard, registrar_area

        from . import (
            dashboard,
            kpis,
        )  # noqa: F401  (importar kpis registra los indicadores)

        registrar_area(
            AreaDashboard(
                slug="proyectos",
                titulo="Proyectos",
                icono="bi-building",
                descripcion="Avance, costo y margen de cada obra (valor ganado).",
                construir=dashboard.construir,
                orden=10,
                grafico_resumen=dashboard.para_resumen,
            )
        )
