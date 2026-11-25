from django.contrib import admin

from .models import Gasto, PresupuestoEscenario, Proyecto, Valorizacion


@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "centro_costo", "entidad", "monto_contrato", "estado")


admin.site.register(PresupuestoEscenario)
admin.site.register(Valorizacion)


@admin.register(Gasto)
class GastoAdmin(admin.ModelAdmin):
    list_display = (
        "id_gasto",
        "proyecto",
        "fecha",
        "proveedor",
        "monto_pen",
        "estado",
        "naturaleza",
    )
    list_filter = ("estado", "naturaleza", "tipo_gasto", "proyecto")
    search_fields = ("id_gasto", "proveedor", "concepto", "nro_orden")
