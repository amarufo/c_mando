from django.urls import path

from . import api

urlpatterns = [
    path("kpis/", api.lista_kpi, name="api_kpis"),
    path("kpis/<str:codigo>/historial/", api.historial_kpi, name="api_kpi_historial"),
    path("cargas/<slug:tabla>/", api.cargar, name="api_cargar"),
]
