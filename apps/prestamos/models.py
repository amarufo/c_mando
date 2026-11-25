"""Modelos de Préstamos y deuda (archivo `Cronograma-Prestamos-Detalle-2026`).

Reemplaza las ~30 hojas de detalle y el motor `BD_CUOTAS` por tres tablas:
    Prestamo   -> catálogo (RPT_MAPA + cabecera de cada hoja)
    Cuota      -> una fila por cuota programada (BD_CUOTAS)
    PagoCuota  -> pago real; permite pasar de "se asume pagado" a "se pagó"
"""

from decimal import Decimal

from django.db import models

from apps.core.models import CentroCosto, Empresa


class Prestamo(models.Model):
    class Tipo(models.TextChoices):
        BANCO = "BANCO", "Banco"
        CAJA = "CAJA", "Caja municipal / rural"
        INVERSIONISTA = "INVERSIONISTA", "Inversionista / fondo"
        PAGARE = "PAGARE", "Pagaré"
        TARJETA = "TARJETA", "Tarjeta de negocios"

    class Sistema(models.TextChoices):
        FRANCES = "FRANCES", "Cuota fija (francés)"
        BULLET = "BULLET", "Intereses mensuales y capital al final"
        OTRO = "OTRO", "Otro"

    codigo = models.CharField(max_length=30, unique=True)
    deudor = models.ForeignKey(
        Empresa,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="prestamos",
        help_text="Vacío si es deuda personal del gerente.",
    )
    es_personal = models.BooleanField(default=False)
    acreedor = models.CharField(max_length=120)
    tipo = models.CharField(max_length=14, choices=Tipo.choices)
    moneda = models.CharField(
        max_length=3, choices=[("PEN", "Soles"), ("USD", "Dólares")], default="PEN"
    )
    capital = models.DecimalField(max_digits=14, decimal_places=2)
    fecha_desembolso = models.DateField()
    tasa = models.DecimalField(
        max_digits=6, decimal_places=3, help_text="Tasa anual en porcentaje."
    )
    tipo_tasa = models.CharField(
        max_length=3, choices=[("TEA", "TEA"), ("TNA", "TNA")], default="TEA"
    )
    sistema = models.CharField(max_length=8, choices=Sistema.choices)
    n_cuotas = models.PositiveIntegerField()
    cc_financiado = models.ForeignKey(
        CentroCosto,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Proyecto al que se destinó el fondo, si se conoce.",
    )
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["codigo"]

    def __str__(self):
        return f"{self.codigo} - {self.acreedor}"


class Cuota(models.Model):
    prestamo = models.ForeignKey(
        Prestamo, on_delete=models.CASCADE, related_name="cuotas"
    )
    n_cuota = models.PositiveIntegerField()
    fecha_vencimiento = models.DateField(db_index=True)
    saldo_inicial = models.DecimalField(max_digits=14, decimal_places=2)
    interes = models.DecimalField(max_digits=14, decimal_places=2)
    capital = models.DecimalField(max_digits=14, decimal_places=2)
    otros_costos = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_cuota = models.DecimalField(max_digits=14, decimal_places=2)

    class Meta:
        ordering = ["fecha_vencimiento"]
        constraints = [
            models.UniqueConstraint(
                fields=["prestamo", "n_cuota"], name="uq_cuota_prestamo"
            )
        ]

    @property
    def costo_financiero(self):
        return self.interes + self.otros_costos


class PagoCuota(models.Model):
    cuota = models.ForeignKey(Cuota, on_delete=models.CASCADE, related_name="pagos")
    fecha_pago = models.DateField()
    monto_pagado = models.DecimalField(max_digits=14, decimal_places=2)
    nro_operacion = models.CharField(max_length=30, blank=True)
    observacion = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["fecha_pago"]
