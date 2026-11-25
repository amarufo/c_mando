"""Modelos de Recursos Humanos.

Correspondencia con los archivos actuales (ver docs/parte1/04_rrhh.md):
    Persona          -> MAESTRO 2026.xlsx (MAESTRA 1)
    Marcacion        -> Marcaciones al 09.11.txt (MAESTRA 2)
    PlanillaMes      -> hojas PLANILLA y HONORARIOS de la planilla mensual
    CostoProyectoMes -> formato de planilla por proyecto (4 bloques -> 1 fila por persona y mes)
    Obligacion       -> calendario AFP (día 25), SCTR (día 28) y PLAME

El cuadro de mando solo debe mostrar agregados; los datos personales viven aquí y
no se exponen en las pantallas de resumen.
"""

from django.db import models

from apps.core.models import CentroCosto, Empresa


class Persona(models.Model):
    class Categoria(models.TextChoices):
        CLAVE = "CLAVE", "Personal clave"
        NO_CLAVE = "NO_CLAVE", "Personal no clave"
        ADMINISTRATIVO = "ADMINISTRATIVO", "Administrativo"
        MANO_OBRA = "MANO_OBRA", "Mano de obra"

    class Condicion(models.TextChoices):
        PLANILLA = "PLANILLA", "Planilla"
        RXH = "RXH", "Recibo por honorarios"

    dni = models.CharField(max_length=8, unique=True)
    apellidos_nombres = models.CharField(max_length=150)
    empresa = models.ForeignKey(Empresa, on_delete=models.PROTECT, related_name="+")
    centro_costo = models.ForeignKey(
        CentroCosto, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    area = models.CharField(max_length=60, blank=True)
    cargo = models.CharField(max_length=80)
    categoria = models.CharField(max_length=15, choices=Categoria.choices)
    condicion = models.CharField(max_length=8, choices=Condicion.choices)
    fecha_ingreso = models.DateField()
    fecha_fin_contrato = models.DateField(null=True, blank=True)
    fecha_cese = models.DateField(null=True, blank=True)
    estado_contrato = models.CharField(
        max_length=10,
        choices=[("FIRMADO", "Firmado"), ("ELABORAR", "Por elaborar")],
        default="FIRMADO",
    )
    sueldo_base = models.DecimalField(max_digits=10, decimal_places=2)
    sistema_pension = models.CharField(
        max_length=3,
        choices=[("AFP", "AFP"), ("ONP", "ONP"), ("NA", "No aplica")],
        default="AFP",
    )
    sede = models.CharField(max_length=60, blank=True)
    codigo_reloj = models.CharField(
        max_length=10,
        blank=True,
        help_text="Código del reloj; hoy es el DNI sin ceros a la izquierda.",
    )

    class Meta:
        ordering = ["apellidos_nombres"]

    def __str__(self):
        return self.apellidos_nombres


class CostoProyectoMes(models.Model):
    """Costo bruto de una persona en un proyecto y mes (formato de planilla por proyecto)."""

    periodo = models.DateField(help_text="Primer día del mes.")
    empresa = models.ForeignKey(Empresa, on_delete=models.PROTECT, related_name="+")
    centro_costo = models.ForeignKey(
        CentroCosto, on_delete=models.PROTECT, related_name="+"
    )
    persona = models.ForeignKey(
        Persona, on_delete=models.CASCADE, related_name="costos"
    )
    categoria = models.CharField(max_length=15, choices=Persona.Categoria.choices)
    condicion = models.CharField(max_length=8, choices=Persona.Condicion.choices)
    dias_laborados = models.PositiveSmallIntegerField()
    sueldo_base_acordado = models.DecimalField(max_digits=10, decimal_places=2)
    sueldo_bruto = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Base / días del mes x días laborados.",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["periodo", "persona", "centro_costo"],
                name="uq_costo_proyecto_mes",
            )
        ]
        indexes = [models.Index(fields=["periodo", "centro_costo"])]


class PlanillaMes(models.Model):
    """Resumen del cálculo mensual por persona (el detalle de 64 columnas queda en el archivo de RR. HH.)."""

    periodo = models.DateField()
    persona = models.ForeignKey(
        Persona, on_delete=models.CASCADE, related_name="planillas"
    )
    condicion = models.CharField(max_length=8, choices=Persona.Condicion.choices)
    dias_trabajados = models.PositiveSmallIntegerField()
    remuneracion_bruta = models.DecimalField(max_digits=10, decimal_places=2)
    descuentos_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    aporte_pension = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    essalud = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    neto_pagar = models.DecimalField(max_digits=10, decimal_places=2)
    recibo_emitido = models.BooleanField(
        null=True, blank=True, help_text="Solo recibos por honorarios; NO = no se paga."
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["periodo", "persona"], name="uq_planilla_mes_persona"
            )
        ]


class Marcacion(models.Model):
    """Una marca del reloj. Sin indicador de entrada o salida: se infiere por la hora."""

    codigo_reloj = models.CharField(max_length=10, db_index=True)
    fecha_hora = models.DateTimeField(db_index=True)
    persona = models.ForeignKey(
        Persona,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="marcaciones",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["codigo_reloj", "fecha_hora"], name="uq_marcacion"
            )
        ]


class Obligacion(models.Model):
    class Tipo(models.TextChoices):
        AFP = "AFP", "AFP (día 25)"
        SCTR = "SCTR", "SCTR (día 28)"
        VIDA_LEY = "VIDA_LEY", "Seguro de vida ley (día 28)"
        PLAME = "PLAME", "PLAME"

    periodo = models.DateField()
    tipo = models.CharField(max_length=10, choices=Tipo.choices)
    fecha_limite = models.DateField()
    fecha_entrega = models.DateField(null=True, blank=True)
    responsable = models.CharField(
        max_length=80, blank=True, help_text="Rol, no nombre de persona."
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["periodo", "tipo"], name="uq_obligacion_periodo"
            )
        ]
        ordering = ["-periodo", "fecha_limite"]
