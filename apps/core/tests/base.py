"""Datos mínimos y deterministas para las pruebas (distintos de los datos de ejemplo aleatorios)."""

from datetime import date
from decimal import Decimal

from apps.core.models import Categoria, CentroCosto, Empresa

CORTE = date(2026, 11, 12)


def catalogos():
    empresa = Empresa.objects.create(
        ruc="20615105725",
        razon_social="Empresa de prueba SAC",
        nombre_corto="DPHC",
        prefijo_documentos="DPHC",
    )
    cc = CentroCosto.objects.create(
        cc2="017", nombre="CC PRUEBA", tipo="PROYECTO", empresa=empresa
    )
    cat_obra = Categoria.objects.create(
        codigo="01.01", componente="01", item="Concreto", tipo_costo="Variable"
    )
    cat_pre = Categoria.objects.create(
        codigo="00.01", componente="00", item="Estudios previos"
    )
    return empresa, cc, cat_obra, cat_pre


def proyecto_basico(empresa, cc):
    """Contrato 1,180,000 con IGV (1,000,000 sin IGV); meta de costo 70 % = 700,000 (sin IGV)."""
    from apps.proyectos.models import Proyecto, Valorizacion

    p = Proyecto.objects.create(
        centro_costo=cc,
        nombre="Obra de prueba",
        monto_contrato=Decimal("1180000"),
        fecha_acta_eo=date(2026, 7, 1),
        plazo_eo_dias=200,
    )
    for mes in (7, 8, 9, 10):  # 4 meses cerrados: plan 200,000 y real 100,000 por mes
        Valorizacion.objects.create(
            proyecto=p,
            periodo=date(2026, mes, 1),
            monto_planificado=Decimal("200000"),
            monto_real=Decimal("100000"),
        )
    return p
