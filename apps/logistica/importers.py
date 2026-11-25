"""Archivos limpios de Logística y compras (docs/parte1/07_archivos_limpios.md, secciones 4 y 5)."""

from apps.core.importers import Columna as C, Importador, registrar
from apps.core.models import CentroCosto, Empresa

from .models import Comprobante, Orden, Proveedor, Requerimiento

EMPRESA = (Empresa, "ruc")
CC = (CentroCosto, "cc2")
MONEDA = ("PEN", "USD")

registrar(
    Importador(
        slug="logistica_proveedores",
        area="logistica",
        modelo=Proveedor,
        clave=("ruc",),
        descripcion="Proveedores (RUC y razón social).",
        columnas=[
            C("ruc", "texto", ejemplo="20123456789"),
            C("razon_social", "texto", ejemplo="Proveedor de ejemplo SAC"),
        ],
    )
)

registrar(
    Importador(
        slug="logistica_requerimientos",
        area="logistica",
        modelo=Requerimiento,
        clave=("nro",),
        descripcion="Requerimientos (una fila por RQ, con la cantidad de ítems y de ítems con precio).",
        columnas=[
            C("nro", "texto", ejemplo="RQ-DPHC-2026-0261"),
            C(
                "ruc_empresa",
                "texto",
                campo="empresa",
                buscar=EMPRESA,
                ejemplo="20615105725",
            ),
            C("cc2", "texto", campo="centro_costo", buscar=CC, ejemplo="017"),
            C(
                "tipo",
                "texto",
                valores=tuple(v for v, _ in Requerimiento.Tipo.choices),
                ejemplo="RUTINARIO",
            ),
            C("clase", "texto", valores=("BIENES", "SERVICIOS"), ejemplo="BIENES"),
            C(
                "estado",
                "texto",
                valores=tuple(v for v, _ in Requerimiento.Estado.choices),
                ejemplo="FINALIZADO",
            ),
            C("fecha_creacion", "fecha", ejemplo="2026-10-05"),
            C("fecha_aprobacion", "fecha", obligatorio=False, ejemplo="2026-10-06"),
            C("n_items", "entero", ejemplo="3"),
            C("n_items_con_precio", "entero", ejemplo="1"),
        ],
    )
)

registrar(
    Importador(
        slug="logistica_ordenes",
        area="logistica",
        modelo=Orden,
        clave=("nro",),
        descripcion="Órdenes de compra y de servicio (una fila por orden). Cargar antes los proveedores.",
        columnas=[
            C("nro", "texto", ejemplo="OC-DPHC-2026-0039"),
            C("tipo", "texto", valores=("OC", "OS"), ejemplo="OC"),
            C(
                "ruc_empresa",
                "texto",
                campo="empresa",
                buscar=EMPRESA,
                ejemplo="20615105725",
            ),
            C("cc2", "texto", campo="centro_costo", buscar=CC, ejemplo="017"),
            C("cc1", "texto", obligatorio=False, ejemplo="OE.2.1"),
            C(
                "ruc_proveedor",
                "texto",
                campo="proveedor",
                buscar=(Proveedor, "ruc"),
                ejemplo="20123456789",
            ),
            C("rq_origen", "texto", obligatorio=False, ejemplo="RQ-DPHC-2026-0261"),
            C("es_regularizacion", "bool", ejemplo="NO"),
            C(
                "estado",
                "texto",
                valores=tuple(v for v, _ in Orden.Estado.choices),
                ejemplo="POR_PAGAR",
            ),
            C(
                "estado_entrega",
                "texto",
                valores=tuple(v for v, _ in Orden.Entrega.choices),
                ejemplo="ENTREGADO",
            ),
            C(
                "condicion_pago",
                "texto",
                valores=tuple(v for v, _ in Orden.CONDICIONES),
                ejemplo="CREDITO_30",
            ),
            C("moneda", "texto", valores=MONEDA, ejemplo="PEN"),
            C("tc", "numero", obligatorio=False, ejemplo="1"),
            C("total", "numero", ejemplo="5900.00"),
            C("fecha_aprobacion_rq", "fecha", obligatorio=False, ejemplo="2026-10-06"),
            C("fecha_emision", "fecha", ejemplo="2026-10-07"),
            C("fecha_aprobacion", "fecha", obligatorio=False, ejemplo="2026-10-07"),
        ],
    )
)

registrar(
    Importador(
        slug="compras_comprobantes",
        area="logistica",
        modelo=Comprobante,
        clave=("proveedor", "serie_numero"),
        descripcion="Tabla única de Contabilidad, Finanzas y Tesorería: cada oficina completa sus columnas.",
        columnas=[
            C(
                "ruc_empresa",
                "texto",
                campo="empresa",
                buscar=EMPRESA,
                ejemplo="20615105725",
            ),
            C(
                "ruc_proveedor",
                "texto",
                campo="proveedor",
                buscar=(Proveedor, "ruc"),
                ejemplo="20123456789",
            ),
            C(
                "tipo_doc",
                "texto",
                valores=tuple(v for v, _ in Comprobante.TIPOS_DOC),
                ejemplo="FACTURA",
            ),
            C("serie_numero", "texto", ejemplo="F001-000123"),
            C("nro_orden", "texto", obligatorio=False, ejemplo="OC-DPHC-2026-0039"),
            C("cc2", "texto", campo="centro_costo", buscar=CC, ejemplo="017"),
            C("cc1", "texto", obligatorio=False, ejemplo="OE.2.1"),
            C("fecha_doc", "fecha", ejemplo="2026-10-20"),
            C("fecha_venc", "fecha", ejemplo="2026-11-19"),
            C("moneda", "texto", valores=MONEDA, ejemplo="PEN"),
            C("tc", "numero", obligatorio=False, ejemplo="1"),
            C("base_imponible", "numero", ejemplo="5000.00"),
            C("igv", "numero", obligatorio=False, ejemplo="900.00"),
            C("total", "numero", ejemplo="5900.00"),
            C("total_logistica", "numero", obligatorio=False, ejemplo="5900.00"),
            C("detraccion_monto", "numero", obligatorio=False, ejemplo="0"),
            C("retencion_garantia", "numero", obligatorio=False, ejemplo="0"),
            C("fecha_registro", "fecha", obligatorio=False, ejemplo="2026-10-21"),
            C(
                "estado_pago",
                "texto",
                valores=tuple(v for v, _ in Comprobante.EstadoPago.choices),
                ejemplo="PROGRAMADO",
            ),
            C(
                "fecha_programada_pago",
                "fecha",
                obligatorio=False,
                ejemplo="2026-11-18",
            ),
            C("fecha_pago_real", "fecha", obligatorio=False, ejemplo=""),
            C("nro_operacion", "texto", obligatorio=False, ejemplo=""),
        ],
    )
)
