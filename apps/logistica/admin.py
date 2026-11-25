from django.contrib import admin

from .models import Comprobante, Orden, Proveedor, Requerimiento

admin.site.register(Proveedor)


@admin.register(Requerimiento)
class RequerimientoAdmin(admin.ModelAdmin):
    list_display = ("nro", "tipo", "estado", "centro_costo", "fecha_creacion")
    list_filter = ("tipo", "estado")
    search_fields = ("nro",)


@admin.register(Orden)
class OrdenAdmin(admin.ModelAdmin):
    list_display = ("nro", "proveedor", "estado", "total", "moneda", "fecha_emision")
    list_filter = ("estado", "estado_entrega", "tipo")
    search_fields = ("nro", "proveedor__razon_social")


@admin.register(Comprobante)
class ComprobanteAdmin(admin.ModelAdmin):
    list_display = (
        "serie_numero",
        "proveedor",
        "total",
        "moneda",
        "fecha_venc",
        "estado_pago",
    )
    list_filter = ("estado_pago", "tipo_doc")
    search_fields = ("serie_numero", "nro_orden", "proveedor__razon_social")
