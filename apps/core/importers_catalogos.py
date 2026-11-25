"""Archivos limpios de catálogos maestros (cat_*), definidos una sola vez y actualizados cuando cambian."""

from .importers import Columna as C, Importador, registrar
from .models import Categoria, CentroCosto, Empresa, TipoCambio

registrar(
    Importador(
        slug="cat_empresa",
        area="core",
        modelo=Empresa,
        clave=("ruc",),
        descripcion="Razones sociales del grupo.",
        columnas=[
            C("ruc", "texto", ejemplo="20607967912"),
            C("razon_social", "texto", ejemplo="DEPERU HUB E.I.R.L."),
            C("nombre_corto", "texto", ejemplo="DPH"),
            C("prefijo_documentos", "texto", obligatorio=False, ejemplo="DPH"),
        ],
    )
)

registrar(
    Importador(
        slug="cat_centro_costo",
        area="core",
        modelo=CentroCosto,
        clave=("cc2",),
        descripcion="Centros de costo: áreas, sedes y proyectos (CC2 de 3 dígitos).",
        columnas=[
            C("cc2", "texto", ejemplo="017"),
            C("nombre", "texto", ejemplo="CC COLLANA"),
            C(
                "tipo",
                "texto",
                valores=("AREA", "SEDE", "PROYECTO"),
                ejemplo="PROYECTO",
            ),
            C(
                "ruc_empresa",
                "texto",
                obligatorio=False,
                campo="empresa",
                buscar=(Empresa, "ruc"),
                ejemplo="20615105725",
            ),
        ],
    )
)

registrar(
    Importador(
        slug="cat_categoria",
        area="core",
        modelo=Categoria,
        clave=("codigo",),
        descripcion="Categorías de gasto (hoja categorias_global).",
        columnas=[
            C("codigo", "texto", ejemplo="01.02.03"),
            C("componente", "texto", ejemplo="01"),
            C("item", "texto", ejemplo="Movilización de equipos"),
            C("etapa", "texto", obligatorio=False, ejemplo="Ejecución"),
            C("tipo_costo", "texto", valores=("Fijo", "Variable"), ejemplo="Variable"),
            C("categoria_especial", "texto", obligatorio=False, ejemplo="Laboral"),
        ],
    )
)

registrar(
    Importador(
        slug="cat_tc",
        area="core",
        modelo=TipoCambio,
        clave=("fecha",),
        descripcion="Tipo de cambio diario (soles por dólar).",
        columnas=[
            C("fecha", "fecha", ejemplo="2026-11-12"),
            C("compra", "numero", ejemplo="3.4500"),
            C("venta", "numero", ejemplo="3.4700"),
        ],
    )
)
