from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("", views.resumen, name="resumen"),
    path("area/<slug:slug>/", views.area, name="area"),
    path("kpi/", views.diccionario, name="diccionario"),
    path("kpi/<str:codigo>/", views.kpi_detalle, name="kpi_detalle"),
    path("cargas/", views.cargas, name="cargas"),
    path("cargas/plantilla/<slug:slug>.csv", views.plantilla_csv, name="plantilla_csv"),
    path("salud/", views.salud, name="salud"),
    path(
        "ingresar/",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    path("salir/", auth_views.LogoutView.as_view(), name="logout"),
]
