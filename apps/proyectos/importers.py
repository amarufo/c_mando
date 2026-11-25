"""Archivos limpios de Proyectos (ver docs/parte1/07_archivos_limpios.md, sección 3)."""

from apps.core.importers import Columna as C, Importador, registrar
from apps.core.models import Categoria, CentroCosto

from .models import Gasto, PresupuestoEscenario, Proyecto, Valorizacion

PROYECTO = (Proyecto, "centro_costo__cc2")
_proy = lambda: C(
    "cc2", "texto", campo="proyecto", buscar=PROYECTO, ejemplo="017"
)  # noqa: E731

registrar(
    Importador(
        slug="proyectos_ficha",
        area="proyectos",
        modelo=Proyecto,
        clave=("centro_costo",),
        descripcion="Una fila por proyecto: datos generales, plazos y monto del contrato.",
        columnas=[
            C(
                "cc2",
                "texto",
                campo="centro_costo",
                buscar=(CentroCosto, "cc2"),
                ejemplo="017",
            ),
            C("nombre", "texto", ejemplo="Polideportivo Ccollana"),
            C("cui", "texto", obligatorio=False, ejemplo="2686704"),
            C("codigo", "texto", obligatorio=False, ejemplo="0103"),
            C(
                "entidad",
                "texto",
                obligatorio=False,
                ejemplo="Municipalidad Provincial",
            ),
            C("ubicacion", "texto", obligatorio=False, ejemplo="Ayacucho, Huanta"),
            C("fecha_acta_et", "fecha", obligatorio=False, ejemplo="2026-04-04"),
            C(
                "plazo_et",
                "entero",
                obligatorio=False,
                campo="plazo_et_dias",
                ejemplo="60",
            ),
            C("fecha_acta_eo", "fecha", obligatorio=False, ejemplo="2026-07-17"),
            C(
                "plazo_eo",
                "entero",
                obligatorio=False,
                campo="plazo_eo_dias",
                ejemplo="150",
            ),
            C("monto_contrato", "numero", ejemplo="6072508.74"),
            C(
                "estado",
                "texto",
                obligatorio=False,
                valores=("ACTIVO", "CERRADO"),
                ejemplo="ACTIVO",
            ),
        ],
    )
)

registrar(
    Importador(
        slug="proyectos_presupuesto",
        area="proyectos",
        modelo=PresupuestoEscenario,
        clave=("proyecto", "escenario"),
        descripcion="Presupuesto de obra por escenario (contrato, meta, propuesto) con sus porcentajes.",
        columnas=[
            _proy(),
            C(
                "escenario",
                "texto",
                valores=("CONTRATO", "META", "PROPUESTO"),
                ejemplo="META",
            ),
            C("costo_directo", "numero", ejemplo="2928728.15"),
            C("gg_pct", "numero", ejemplo="0.13"),
            C("utilidad_pct", "numero", ejemplo="0.10"),
            C("igv_pct", "numero", obligatorio=False, ejemplo="0.18"),
            C("supervision", "numero", obligatorio=False, ejemplo="187518.79"),
            C("expediente_tecnico", "numero", obligatorio=False, ejemplo="136377.30"),
            C("liquidacion", "numero", obligatorio=False, ejemplo="3816.53"),
        ],
    )
)

registrar(
    Importador(
        slug="proyectos_valorizacion",
        area="proyectos",
        modelo=Valorizacion,
        clave=("proyecto", "periodo"),
        descripcion="Una fila por proyecto y mes: cronograma contractual y valorización real.",
        columnas=[
            _proy(),
            C("periodo", "fecha", ejemplo="2026-10-01"),
            C("monto_planificado", "numero", ejemplo="800000"),
            C("monto_real", "numero", obligatorio=False, ejemplo="771093"),
            C("monto_cobrado", "numero", obligatorio=False, ejemplo="771093"),
            C("fecha_cobro", "fecha", obligatorio=False, ejemplo="2026-11-05"),
        ],
    )
)

registrar(
    Importador(
        slug="proyectos_gastos",
        area="proyectos",
        modelo=Gasto,
        clave=("id_gasto",),
        descripcion="Pagos y gastos proyectados imputados a un proyecto (hoja Gastos).",
        columnas=[
            C("id_gasto", "texto", ejemplo="017-000123"),
            _proy(),
            C(
                "codigo_categoria",
                "texto",
                campo="categoria",
                buscar=(Categoria, "codigo"),
                ejemplo="01.02.03",
            ),
            C("fecha", "fecha", ejemplo="2026-10-15"),
            C("fecha_pago_real", "fecha", obligatorio=False, ejemplo="2026-10-16"),
            C("estado", "texto", valores=("PAGADO", "PENDIENTE"), ejemplo="PAGADO"),
            C("naturaleza", "texto", valores=("REAL", "PROYECTADO"), ejemplo="REAL"),
            C(
                "tipo_gasto",
                "texto",
                valores=("OPERATIVO", "PRESTAMO", "REEMBOLSO", "RRHH"),
                ejemplo="OPERATIVO",
            ),
            C("proveedor_ruc", "texto", obligatorio=False, ejemplo="20123456789"),
            C("proveedor", "texto", ejemplo="Proveedor de ejemplo SAC"),
            C("concepto", "texto", obligatorio=False, ejemplo="Compra de cemento"),
            C("moneda", "texto", valores=("PEN", "USD"), ejemplo="PEN"),
            C("monto", "numero", ejemplo="1180.00"),
            C("con_igv", "bool", ejemplo="SI"),
            C("tc", "numero", obligatorio=False, ejemplo="1"),
            C("nro_orden", "texto", obligatorio=False, ejemplo="OC-DPHC-2026-0123"),
            C(
                "id_comprobante",
                "texto",
                obligatorio=False,
                ejemplo="20123456789|F001-123",
            ),
        ],
    )
)
