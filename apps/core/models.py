"""Modelos compartidos por todas las áreas.

Criterio de diseño: cada área es dueña de sus tablas; lo único que comparten son
estos catálogos (empresa, centro de costo, categoría, tipo de cambio) y los
registros de control (cargas, configuración de KPI, historial de KPI).
Las áreas se enlazan entre sí por **códigos estables** (RUC, CC2, DNI, N.º de orden),
no por claves foráneas entre tablas de áreas distintas.
"""

from django.conf import settings
from django.db import models


class Empresa(models.Model):
    """Razón social del grupo. Llave natural: RUC."""

    ruc = models.CharField(max_length=11, unique=True)
    razon_social = models.CharField(max_length=200)
    nombre_corto = models.CharField(max_length=40)
    prefijo_documentos = models.CharField(
        max_length=10, blank=True, help_text="Ej.: DPH, DPHC, CSD."
    )
    activa = models.BooleanField(default=True)

    class Meta:
        ordering = ["nombre_corto"]

    def __str__(self):
        return self.nombre_corto


class CentroCosto(models.Model):
    """Dónde se carga el costo: un área, una sede o un proyecto. Llave natural: CC2 (3 dígitos)."""

    class Tipo(models.TextChoices):
        AREA = "AREA", "Área administrativa"
        SEDE = "SEDE", "General de sede"
        PROYECTO = "PROYECTO", "Proyecto"

    cc2 = models.CharField(max_length=3, unique=True)
    nombre = models.CharField(max_length=150)
    tipo = models.CharField(max_length=10, choices=Tipo.choices, default=Tipo.PROYECTO)
    empresa = models.ForeignKey(
        Empresa,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="centros_costo",
    )
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["cc2"]

    def __str__(self):
        return f"{self.cc2} - {self.nombre}"


class Categoria(models.Model):
    """Catálogo global de categorías de gasto (hoja `categorias_global` del libro de proyectos)."""

    COMPONENTES = {
        "00": "Precontractual",
        "01": "Ejecución de obra",
        "02": "Gastos generales",
        "03": "Expediente técnico",
        "04": "Supervisión de ET",
        "05": "Supervisión de obra",
        "06": "Gastos de gestión",
        "07": "Liquidación",
        "3101": "Gastos administrativos",
    }

    codigo = models.CharField(max_length=20, unique=True)
    componente = models.CharField(max_length=4)
    item = models.CharField(max_length=200)
    etapa = models.CharField(max_length=60, blank=True)
    tipo_costo = models.CharField(
        max_length=10,
        choices=[("Fijo", "Fijo"), ("Variable", "Variable")],
        default="Variable",
    )
    categoria_especial = models.CharField(
        max_length=15, blank=True, help_text="Laboral, Financiero o Social."
    )

    class Meta:
        ordering = ["codigo"]

    @property
    def componente_nombre(self):
        return self.COMPONENTES.get(self.componente, self.componente)

    def __str__(self):
        return f"{self.codigo} {self.item}"


class TipoCambio(models.Model):
    """Tipo de cambio diario (S/ por US$). Reemplaza los 3.5 y 3.45 fijos de los archivos actuales."""

    fecha = models.DateField(unique=True)
    compra = models.DecimalField(max_digits=7, decimal_places=4)
    venta = models.DecimalField(max_digits=7, decimal_places=4)

    class Meta:
        ordering = ["-fecha"]
        verbose_name_plural = "tipos de cambio"

    def __str__(self):
        return f"{self.fecha}: {self.venta}"


class CargaArchivo(models.Model):
    """Registro de cada archivo cargado (manual, por API o por comando). Alimenta la pestaña de calidad."""

    class Estado(models.TextChoices):
        OK = "OK", "Cargado"
        RECHAZADA = "RECHAZADA", "Rechazado por errores"
        SIMULACION = "SIMULACION", "Validación sin guardar"

    area = models.CharField(max_length=30)
    tabla = models.CharField(max_length=60)
    nombre_archivo = models.CharField(max_length=200, blank=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )
    fecha = models.DateTimeField(auto_now_add=True)
    filas_leidas = models.PositiveIntegerField(default=0)
    filas_ok = models.PositiveIntegerField(default=0)
    filas_error = models.PositiveIntegerField(default=0)
    estado = models.CharField(max_length=12, choices=Estado.choices)
    errores = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ["-fecha"]
        verbose_name_plural = "cargas de archivos"

    def __str__(self):
        return f"{self.tabla} ({self.estado}) {self.fecha:%Y-%m-%d}"


class KPIConfig(models.Model):
    """Meta y umbrales editables desde el admin; si no existe fila se usan los valores por defecto del código."""

    codigo = models.CharField(max_length=10, unique=True)
    meta = models.FloatField(null=True, blank=True)
    umbral_alerta = models.FloatField(null=True, blank=True)
    umbral_critico = models.FloatField(null=True, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "configuración de KPI"
        verbose_name_plural = "configuración de KPI"

    def __str__(self):
        return self.codigo


class KPISnapshot(models.Model):
    """Valor de un KPI en una fecha de corte. Permite tendencias sin recalcular el pasado."""

    codigo = models.CharField(max_length=10, db_index=True)
    fecha_corte = models.DateField(db_index=True)
    empresa = models.ForeignKey(
        Empresa, null=True, blank=True, on_delete=models.CASCADE
    )
    centro_costo = models.ForeignKey(
        CentroCosto, null=True, blank=True, on_delete=models.CASCADE
    )
    valor = models.FloatField(null=True)
    estado = models.CharField(max_length=10)
    calculado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["codigo", "fecha_corte"]
        constraints = [
            models.UniqueConstraint(
                fields=["codigo", "fecha_corte", "empresa", "centro_costo"],
                name="uq_kpi_snapshot",
                nulls_distinct=False,
            )
        ]

    def __str__(self):
        return f"{self.codigo} {self.fecha_corte}: {self.valor}"
