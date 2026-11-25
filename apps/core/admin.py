from django.contrib import admin

from .models import (
    CargaArchivo,
    Categoria,
    CentroCosto,
    Empresa,
    KPIConfig,
    KPISnapshot,
    TipoCambio,
)


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ("nombre_corto", "ruc", "razon_social", "activa")
    search_fields = ("ruc", "razon_social", "nombre_corto")


@admin.register(CentroCosto)
class CentroCostoAdmin(admin.ModelAdmin):
    list_display = ("cc2", "nombre", "tipo", "empresa", "activo")
    list_filter = ("tipo", "activo")
    search_fields = ("cc2", "nombre")


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("codigo", "componente", "item", "tipo_costo", "categoria_especial")
    list_filter = ("componente", "tipo_costo")
    search_fields = ("codigo", "item")


@admin.register(TipoCambio)
class TipoCambioAdmin(admin.ModelAdmin):
    list_display = ("fecha", "compra", "venta")


@admin.register(KPIConfig)
class KPIConfigAdmin(admin.ModelAdmin):
    """Aquí se ajustan metas y umbrales de semáforo sin tocar el código."""

    list_display = ("codigo", "meta", "umbral_alerta", "umbral_critico", "activo")


@admin.register(CargaArchivo)
class CargaArchivoAdmin(admin.ModelAdmin):
    list_display = (
        "fecha",
        "tabla",
        "estado",
        "filas_leidas",
        "filas_ok",
        "filas_error",
        "usuario",
    )
    list_filter = ("estado", "area")
    readonly_fields = ("errores",)


@admin.register(KPISnapshot)
class KPISnapshotAdmin(admin.ModelAdmin):
    list_display = ("codigo", "fecha_corte", "valor", "estado")
    list_filter = ("codigo",)
