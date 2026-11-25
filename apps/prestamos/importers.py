"""Archivos limpios de Préstamos (docs/parte1/07_archivos_limpios.md, sección 6)."""

from apps.core.importers import Columna as C, Importador, registrar
from apps.core.models import CentroCosto, Empresa

from .models import Cuota, PagoCuota, Prestamo

registrar(
    Importador(
        slug="prestamos_catalogo",
        area="prestamos",
        modelo=Prestamo,
        clave=("codigo",),
        descripcion="Catálogo de préstamos y deudas (una fila por préstamo).",
        columnas=[
            C("id_prestamo", "texto", campo="codigo", ejemplo="FIN-BBVA-001"),
            C(
                "ruc_deudor",
                "texto",
                obligatorio=False,
                campo="deudor",
                buscar=(Empresa, "ruc"),
                ejemplo="20615105725",
            ),
            C("es_personal", "bool", ejemplo="NO"),
            C("acreedor", "texto", ejemplo="BBVA"),
            C(
                "tipo",
                "texto",
                valores=tuple(v for v, _ in Prestamo.Tipo.choices),
                ejemplo="BANCO",
            ),
            C("moneda", "texto", valores=("PEN", "USD"), ejemplo="PEN"),
            C("capital", "numero", ejemplo="300000"),
            C("fecha_desembolso", "fecha", ejemplo="2026-01-15"),
            C("tasa", "numero", ejemplo="20.1"),
            C("tipo_tasa", "texto", valores=("TEA", "TNA"), ejemplo="TEA"),
            C(
                "sistema",
                "texto",
                valores=tuple(v for v, _ in Prestamo.Sistema.choices),
                ejemplo="FRANCES",
            ),
            C("n_cuotas", "entero", ejemplo="36"),
            C(
                "cc2_financiado",
                "texto",
                obligatorio=False,
                campo="cc_financiado",
                buscar=(CentroCosto, "cc2"),
                ejemplo="",
            ),
            C("activo", "bool", ejemplo="SI"),
        ],
    )
)

registrar(
    Importador(
        slug="prestamos_cuotas",
        area="prestamos",
        modelo=Cuota,
        clave=("prestamo", "n_cuota"),
        descripcion="Cronograma: una fila por cuota. Cargar antes el catálogo.",
        columnas=[
            C(
                "id_prestamo",
                "texto",
                campo="prestamo",
                buscar=(Prestamo, "codigo"),
                ejemplo="FIN-BBVA-001",
            ),
            C("n_cuota", "entero", ejemplo="1"),
            C("fecha_vencimiento", "fecha", ejemplo="2026-02-15"),
            C("saldo_inicial", "numero", ejemplo="300000"),
            C("interes", "numero", ejemplo="4500"),
            C("capital", "numero", ejemplo="7000"),
            C("otros_costos", "numero", obligatorio=False, ejemplo="50"),
            C("total_cuota", "numero", ejemplo="11550"),
        ],
    )
)


def _armar_pago(datos, cache):
    """El pago se asocia a su cuota por (id_prestamo, n_cuota): no existe un único código de cuota en los archivos."""
    prestamo = cache.obtener(Prestamo, "codigo", datos["_id_prestamo"])
    cuota = Cuota.objects.filter(prestamo=prestamo, n_cuota=datos["_n_cuota"]).first()
    if cuota is None:
        raise ValueError(
            f"no existe la cuota {datos['_n_cuota']} del préstamo {datos['_id_prestamo']}"
        )
    return {"cuota": cuota}


registrar(
    Importador(
        slug="prestamos_pagos",
        area="prestamos",
        modelo=PagoCuota,
        clave=("cuota", "fecha_pago"),
        armar=_armar_pago,
        descripcion="Pagos reales de cuotas (de los reportes de Tesorería).",
        columnas=[
            C(
                "id_prestamo",
                "texto",
                campo="_id_prestamo",
                ejemplo="FIN-BBVA-001",
                extraer=lambda o: o.cuota.prestamo.codigo,
            ),
            C(
                "n_cuota",
                "entero",
                campo="_n_cuota",
                ejemplo="1",
                extraer=lambda o: o.cuota.n_cuota,
            ),
            C("fecha_pago", "fecha", ejemplo="2026-02-14"),
            C("monto_pagado", "numero", ejemplo="11550"),
            C("nro_operacion", "texto", obligatorio=False, ejemplo="000123"),
            C("observacion", "texto", obligatorio=False, ejemplo=""),
        ],
    )
)
