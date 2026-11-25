"""Modelos del área de Proyectos (libro modelo: `Collana 09-11.xlsx`).

Correspondencia con el libro actual:
    Proyecto              -> hoja INF-Gral (bloque de datos del proyecto)
    PresupuestoEscenario  -> hoja EO-PPTOs (totales Contrato / Meta 70 % / Propuesto)
    Valorizacion          -> hojas Resumen-Valorizaciones y Valorizaciones (una fila por mes)
    Gasto                 -> hoja Gastos (base de datos de pagos y gastos proyectados)
"""

from datetime import timedelta
from decimal import Decimal

from django.db import models

from apps.core.models import Categoria, CentroCosto
from apps.core.services import a_soles, sin_igv, tc_efectivo


class Proyecto(models.Model):
    centro_costo = models.OneToOneField(
        CentroCosto, on_delete=models.PROTECT, related_name="proyecto"
    )
    nombre = models.CharField(max_length=200)
    cui = models.CharField(max_length=12, blank=True)
    codigo = models.CharField(max_length=20, blank=True)
    entidad = models.CharField(max_length=200, blank=True)
    ubicacion = models.CharField(max_length=150, blank=True)
    fecha_acta_et = models.DateField(null=True, blank=True)
    plazo_et_dias = models.PositiveIntegerField(default=0)
    fecha_acta_eo = models.DateField(null=True, blank=True)
    plazo_eo_dias = models.PositiveIntegerField(default=0)
    monto_contrato = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        help_text="Costo de obra del contrato, con IGV.",
    )
    factor_meta = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=Decimal("0.70"),
        help_text="Meta de costo sobre el contrato (70 %).",
    )
    estado = models.CharField(
        max_length=10,
        choices=[("ACTIVO", "Activo"), ("CERRADO", "Cerrado")],
        default="ACTIVO",
    )

    class Meta:
        ordering = ["centro_costo__cc2"]

    def __str__(self):
        return self.nombre

    @property
    def fecha_fin_eo(self):
        return (
            self.fecha_acta_eo + timedelta(days=self.plazo_eo_dias)
            if self.fecha_acta_eo
            else None
        )


class PresupuestoEscenario(models.Model):
    """Presupuesto de obra en uno de sus tres escenarios; los totales se calculan como en EO-PPTOs."""

    class Escenario(models.TextChoices):
        CONTRATO = "CONTRATO", "Contrato (base 100 %)"
        META = "META", "Meta (70 %)"
        PROPUESTO = "PROPUESTO", "Propuesto"

    proyecto = models.ForeignKey(
        Proyecto, on_delete=models.CASCADE, related_name="presupuestos"
    )
    escenario = models.CharField(max_length=10, choices=Escenario.choices)
    costo_directo = models.DecimalField(max_digits=14, decimal_places=2)
    gg_pct = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="Gastos generales (0.13 = 13 %)."
    )
    utilidad_pct = models.DecimalField(max_digits=5, decimal_places=2)
    igv_pct = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0.18")
    )
    supervision = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    expediente_tecnico = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    liquidacion = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["proyecto", "escenario"], name="uq_presupuesto_escenario"
            )
        ]

    @property
    def subtotal(self):
        return self.costo_directo * (1 + self.gg_pct + self.utilidad_pct)

    @property
    def costo_obra(self):
        return self.subtotal * (1 + self.igv_pct)

    @property
    def costo_obra_sin_igv(self):
        return self.subtotal

    @property
    def costo_total(self):
        return (
            self.costo_obra
            + self.supervision
            + self.expediente_tecnico
            + self.liquidacion
        )


class Valorizacion(models.Model):
    """Una fila por proyecto y mes. Importes con IGV, como en el libro actual."""

    proyecto = models.ForeignKey(
        Proyecto, on_delete=models.CASCADE, related_name="valorizaciones"
    )
    periodo = models.DateField(help_text="Primer día del mes.")
    monto_planificado = models.DecimalField(
        max_digits=14, decimal_places=2, help_text="Cronograma contractual."
    )
    monto_real = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Valorizado en el mes; vacío si aún no existe.",
    )
    monto_cobrado = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    fecha_cobro = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["proyecto", "periodo"]
        constraints = [
            models.UniqueConstraint(
                fields=["proyecto", "periodo"], name="uq_valorizacion_mes"
            )
        ]


class Gasto(models.Model):
    """Pago o gasto proyectado imputado a un proyecto y a una categoría."""

    class Estado(models.TextChoices):
        PAGADO = "PAGADO", "Pagado"
        PENDIENTE = "PENDIENTE", "Pendiente"

    class Naturaleza(models.TextChoices):
        REAL = "REAL", "Real"
        PROYECTADO = "PROYECTADO", "Proyectado"

    class Tipo(models.TextChoices):
        OPERATIVO = "OPERATIVO", "Operativo"
        PRESTAMO = "PRESTAMO", "Pago de préstamo"
        REEMBOLSO = "REEMBOLSO", "Reembolso"
        RRHH = "RRHH", "Personal"

    id_gasto = models.CharField(max_length=30, unique=True)
    proyecto = models.ForeignKey(
        Proyecto, on_delete=models.CASCADE, related_name="gastos"
    )
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name="+")
    fecha = models.DateField(db_index=True)
    fecha_pago_real = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=10, choices=Estado.choices)
    naturaleza = models.CharField(
        max_length=10, choices=Naturaleza.choices, default=Naturaleza.REAL
    )
    tipo_gasto = models.CharField(
        max_length=10, choices=Tipo.choices, default=Tipo.OPERATIVO
    )
    proveedor_ruc = models.CharField(max_length=11, blank=True)
    proveedor = models.CharField(max_length=200)
    concepto = models.CharField(max_length=300, blank=True)
    moneda = models.CharField(
        max_length=3, choices=[("PEN", "Soles"), ("USD", "Dólares")], default="PEN"
    )
    monto = models.DecimalField(max_digits=14, decimal_places=2)
    con_igv = models.BooleanField(default=True)
    tc = models.DecimalField(max_digits=7, decimal_places=4, default=Decimal("1"))
    nro_orden = models.CharField(
        max_length=30,
        blank=True,
        help_text="Vínculo con Logística (orden de compra o servicio).",
    )
    id_comprobante = models.CharField(
        max_length=40, blank=True, help_text="RUC + serie-número."
    )
    # Derivados (se calculan en save(); permiten sumar en la base de datos sin repetir la lógica).
    monto_pen = models.DecimalField(
        max_digits=14, decimal_places=2, editable=False, default=0
    )
    monto_pen_sin_igv = models.DecimalField(
        max_digits=14, decimal_places=2, editable=False, default=0
    )

    class Meta:
        ordering = ["fecha"]
        indexes = [models.Index(fields=["proyecto", "estado", "naturaleza"])]

    def calcular_montos(self):
        self.tc = tc_efectivo(
            self.moneda, self.tc, self.fecha
        )  # sin TC explícito, usa la tabla TipoCambio
        self.monto_pen = a_soles(self.monto, self.moneda, self.tc)
        self.monto_pen_sin_igv = sin_igv(self.monto_pen, self.con_igv)

    def save(self, *args, **kwargs):
        self.calcular_montos()
        super().save(*args, **kwargs)
