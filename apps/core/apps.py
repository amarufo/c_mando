from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = "apps.core"
    label = "core"
    verbose_name = "Núcleo del cuadro de mando"

    def ready(self):
        from . import dashboard_calidad, kpis_calidad  # noqa: F401
        from .dashboard import AreaDashboard, registrar_area

        registrar_area(
            AreaDashboard(
                slug="calidad",
                titulo="Calidad de datos",
                icono="bi-shield-check",
                descripcion="Qué se cargó, cuándo y qué tan completo está.",
                construir=dashboard_calidad.construir,
                orden=90,
            )
        )
