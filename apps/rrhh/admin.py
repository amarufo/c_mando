from django.contrib import admin

from .models import CostoProyectoMes, Marcacion, Obligacion, Persona, PlanillaMes


@admin.register(Persona)
class PersonaAdmin(admin.ModelAdmin):
    list_display = (
        "dni",
        "apellidos_nombres",
        "empresa",
        "cargo",
        "categoria",
        "condicion",
        "centro_costo",
    )
    list_filter = ("categoria", "condicion", "empresa")
    search_fields = ("dni", "apellidos_nombres")


admin.site.register(CostoProyectoMes)
admin.site.register(PlanillaMes)
admin.site.register(Marcacion)
admin.site.register(Obligacion)
