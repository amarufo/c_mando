"""Modelos de Logística y pagos.

Cadena de documentos (ver docs/parte1/03_logistica.md):
    Requerimiento -> Orden -> Comprobante -> (programación y pago)

En Contabilidad, Finanzas y Tesorería la tabla es la misma en tres etapas, por eso
`Comprobante` concentra los campos de las tres oficinas; cada una completa los suyos.
Los vínculos entre documentos son por código (N.º de RQ, N.º de orden), tal como
llegan en las exportaciones de los sistemas.
"""

from decimal import Decimal

from django.db import models

from apps.core.models import CentroCosto, Empresa
from apps.core.services import a_soles, tc_efectivo

MONEDAS = [("PEN", "Soles"), ("USD", "Dólares")]


class Proveedor(models.Model):
    ruc = models.CharField(max_length=11, unique=True)
    razon_social = models.CharField(max_length=200)

    class Meta:
        ordering = ["razon_social"]

    def __str__(self):
        return self.razon_social


class Requerimiento(models.Model):
    class Tipo(models.TextChoices):
        EMERGENCIA = "EMERGENCIA", "Emergencia"
        REGULARIZACION = "REGULARIZACION", "Regularización"
        RUTINARIO = "RUTINARIO", "Rutinario"
        LOGISTICO = "LOGISTICO", "Logístico"

    class Estado(models.TextChoices):
        FINALIZADO = "FINALIZADO", "Finalizado"
        RECHAZADA = "RECHAZADA", "Rechazada"
        APROBADA = "APROBADA", "Aprobada"
        OBSERVADA = "OBSERVADA", "Observada"
        POR_REGULARIZAR = "POR_REGULARIZAR", "Por regularizar"
        PENDIENTE = "PENDIENTE", "Pendiente de aprobación"

    nro = models.CharField(max_length=30, unique=True)
    empresa = models.ForeignKey(Empresa, on_delete=models.PROTECT, related_name="+")
    centro_costo = models.ForeignKey(
        CentroCosto, on_delete=models.PROTECT, related_name="+"
    )
    tipo = models.CharField(max_length=15, choices=Tipo.choices)
    clase = models.CharField(
        max_length=10,
        choices=[("BIENES", "Bienes"), ("SERVICIOS", "Servicios")],
        default="BIENES",
    )
    estado = models.CharField(max_length=16, choices=Estado.choices)
    fecha_creacion = models.DateField(db_index=True)
    fecha_aprobacion = models.DateField(null=True, blank=True)
    n_items = models.PositiveIntegerField(default=1)
    n_items_con_precio = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-fecha_creacion"]


class Orden(models.Model):
    class Estado(models.TextChoices):
        FINALIZADA = "FINALIZADA", "Finalizada (pagada)"
        POR_PAGAR = "POR_PAGAR", "Por pagar"
        SIN_FACTURAR = "SIN_FACTURAR", "Aprobada (sin facturar)"
        FACTURADA = "FACTURADA", "Facturada"
        RECHAZADA = "RECHAZADA", "Rechazada"
        POR_APROBAR = "POR_APROBAR", "Por aprobar"

    class Entrega(models.TextChoices):
        ENTREGADO = "ENTREGADO", "Entregado"
        PENDIENTE = "PENDIENTE", "Pendiente de entrega"
        PARCIAL = "PARCIAL", "Entrega parcial"

    CONDICIONES = [
        ("CONTADO_FACTURA", "Contado a la recepción de factura"),
        ("ADELANTO", "Adelanto / anticipado"),
        ("CREDITO_7", "Crédito a 7 días"),
        ("CREDITO_15", "Crédito a 15 días"),
        ("CREDITO_30", "Crédito a 30 días"),
        ("CONTRAENTREGA", "Contado contraentrega"),
    ]

    nro = models.CharField(max_length=30, unique=True)
    tipo = models.CharField(
        max_length=2, choices=[("OC", "Orden de compra"), ("OS", "Orden de servicio")]
    )
    empresa = models.ForeignKey(Empresa, on_delete=models.PROTECT, related_name="+")
    centro_costo = models.ForeignKey(
        CentroCosto, on_delete=models.PROTECT, related_name="+"
    )
    cc1 = models.CharField(
        max_length=20, blank=True, help_text="Partida (OE.2.1, GA, GGF...)."
    )
    proveedor = models.ForeignKey(
        Proveedor, on_delete=models.PROTECT, related_name="ordenes"
    )
    rq_origen = models.CharField(
        max_length=30, blank=True, help_text="Vacío = regularización."
    )
    es_regularizacion = models.BooleanField(default=False)
    estado = models.CharField(max_length=14, choices=Estado.choices)
    estado_entrega = models.CharField(
        max_length=10, choices=Entrega.choices, default=Entrega.PENDIENTE
    )
    condicion_pago = models.CharField(max_length=16, choices=CONDICIONES)
    moneda = models.CharField(max_length=3, choices=MONEDAS, default="PEN")
    tc = models.DecimalField(max_digits=7, decimal_places=4, default=Decimal("1"))
    total = models.DecimalField(
        max_digits=14, decimal_places=2, help_text="Con IGV, en la moneda de la orden."
    )
    total_pen = models.DecimalField(
        max_digits=14, decimal_places=2, editable=False, default=0
    )
    fecha_aprobacion_rq = models.DateField(null=True, blank=True)
    fecha_emision = models.DateField(db_index=True)
    fecha_aprobacion = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["-fecha_emision"]

    def save(self, *args, **kwargs):
        self.tc = tc_efectivo(self.moneda, self.tc, self.fecha_emision)
        self.total_pen = a_soles(self.total, self.moneda, self.tc)
        super().save(*args, **kwargs)


class Comprobante(models.Model):
    """Comprobante de compra y su recorrido por Contabilidad, Finanzas y Tesorería."""

    class EstadoPago(models.TextChoices):
        PROGRAMADO = "PROGRAMADO", "Programado"
        PAGADO = "PAGADO", "Pagado"
        POR_DETRACCION = "POR_DETRACCION", "Por detracción/retención"
        PEND_CONFORMIDAD = "PEND_CONFORMIDAD", "Pendiente de conformidad"
        CONFORME = "CONFORME", "Conforme"
        EN_REVISION = "EN_REVISION", "En revisión"

    TIPOS_DOC = [
        ("FACTURA", "Factura"),
        ("RXH", "Recibo por honorarios"),
        ("PASAJE_AEREO", "Pasaje aéreo"),
        ("PASAJE_TERRESTRE", "Pasaje terrestre"),
    ]

    empresa = models.ForeignKey(Empresa, on_delete=models.PROTECT, related_name="+")
    proveedor = models.ForeignKey(
        Proveedor, on_delete=models.PROTECT, related_name="comprobantes"
    )
    tipo_doc = models.CharField(max_length=16, choices=TIPOS_DOC, default="FACTURA")
    serie_numero = models.CharField(max_length=30)
    nro_orden = models.CharField(max_length=30, blank=True, db_index=True)
    centro_costo = models.ForeignKey(
        CentroCosto, on_delete=models.PROTECT, related_name="+"
    )
    cc1 = models.CharField(max_length=20, blank=True)
    fecha_doc = models.DateField(db_index=True)
    fecha_venc = models.DateField()
    moneda = models.CharField(max_length=3, choices=MONEDAS, default="PEN")
    tc = models.DecimalField(max_digits=7, decimal_places=4, default=Decimal("1"))
    base_imponible = models.DecimalField(max_digits=14, decimal_places=2)
    igv = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        help_text="Importe registrado por Contabilidad.",
    )
    total_logistica = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Importe de la hoja Facturas de Órdenes, para conciliar.",
    )
    total_pen = models.DecimalField(
        max_digits=14, decimal_places=2, editable=False, default=0
    )
    detraccion_monto = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    retencion_garantia = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    # Contabilidad
    fecha_registro = models.DateField(null=True, blank=True)
    estado_pago = models.CharField(max_length=18, choices=EstadoPago.choices)
    # Finanzas
    fecha_programada_pago = models.DateField(null=True, blank=True)
    # Tesorería
    fecha_pago_real = models.DateField(null=True, blank=True)
    nro_operacion = models.CharField(max_length=30, blank=True)

    class Meta:
        ordering = ["-fecha_doc"]
        constraints = [
            # Llave real de un comprobante: el número solo no es único entre proveedores.
            models.UniqueConstraint(
                fields=["proveedor", "serie_numero"],
                name="uq_comprobante_proveedor_numero",
            )
        ]

    def save(self, *args, **kwargs):
        self.tc = tc_efectivo(self.moneda, self.tc, self.fecha_doc)
        self.total_pen = a_soles(self.total, self.moneda, self.tc)
        super().save(*args, **kwargs)

    @property
    def pagado(self):
        return self.estado_pago == self.EstadoPago.PAGADO
