from django.contrib import admin

from .models import Cuota, PagoCuota, Prestamo


class CuotaInline(admin.TabularInline):
    model = Cuota
    extra = 0


@admin.register(Prestamo)
class PrestamoAdmin(admin.ModelAdmin):
    list_display = (
        "codigo",
        "acreedor",
        "deudor",
        "tipo",
        "moneda",
        "capital",
        "activo",
    )
    list_filter = ("tipo", "es_personal", "activo")
    inlines = [CuotaInline]


admin.site.register(PagoCuota)
