"""Archivos limpios de RR. HH. (docs/parte1/07_archivos_limpios.md, sección 7)."""

from apps.core.importers import Columna as C, Importador, registrar
from apps.core.models import CentroCosto, Empresa

from .models import CostoProyectoMes, Marcacion, Obligacion, Persona, PlanillaMes

EMPRESA = (Empresa, "ruc")
CC = (CentroCosto, "cc2")
CATEGORIA = tuple(v for v, _ in Persona.Categoria.choices)
CONDICION = tuple(v for v, _ in Persona.Condicion.choices)

registrar(
    Importador(
        slug="rrhh_personal",
        area="rrhh",
        modelo=Persona,
        clave=("dni",),
        descripcion="Maestro de personal. No incluye cuentas bancarias ni datos familiares.",
        columnas=[
            C("dni", "texto", ejemplo="01234567"),
            C("apellidos_nombres", "texto", ejemplo="PEREZ GOMEZ, JUAN"),
            C(
                "ruc_empresa",
                "texto",
                campo="empresa",
                buscar=EMPRESA,
                ejemplo="20615105725",
            ),
            C(
                "cc2",
                "texto",
                obligatorio=False,
                campo="centro_costo",
                buscar=CC,
                ejemplo="017",
            ),
            C("area", "texto", obligatorio=False, ejemplo="Obra"),
            C("cargo", "texto", ejemplo="Ingeniero residente"),
            C("categoria", "texto", valores=CATEGORIA, ejemplo="CLAVE"),
            C("condicion", "texto", valores=CONDICION, ejemplo="PLANILLA"),
            C("fecha_ingreso", "fecha", ejemplo="2026-03-01"),
            C("fecha_fin_contrato", "fecha", obligatorio=False, ejemplo="2026-12-31"),
            C("fecha_cese", "fecha", obligatorio=False, ejemplo=""),
            C(
                "estado_contrato",
                "texto",
                valores=("FIRMADO", "ELABORAR"),
                ejemplo="FIRMADO",
            ),
            C("sueldo_base", "numero", ejemplo="4500"),
            C("sistema_pension", "texto", valores=("AFP", "ONP", "NA"), ejemplo="AFP"),
            C("sede", "texto", obligatorio=False, ejemplo="Lima"),
            C("codigo_reloj", "texto", obligatorio=False, ejemplo="1234567"),
        ],
    )
)

registrar(
    Importador(
        slug="rrhh_costo_proyecto",
        area="rrhh",
        modelo=CostoProyectoMes,
        clave=("periodo", "persona", "centro_costo"),
        descripcion="Formato de planilla por proyecto: una fila por persona y mes.",
        columnas=[
            C("periodo", "fecha", ejemplo="2026-10-01"),
            C(
                "ruc_empresa",
                "texto",
                campo="empresa",
                buscar=EMPRESA,
                ejemplo="20615105725",
            ),
            C("cc2", "texto", campo="centro_costo", buscar=CC, ejemplo="017"),
            C(
                "dni",
                "texto",
                campo="persona",
                buscar=(Persona, "dni"),
                ejemplo="01234567",
            ),
            C("categoria", "texto", valores=CATEGORIA, ejemplo="CLAVE"),
            C("condicion", "texto", valores=CONDICION, ejemplo="PLANILLA"),
            C("dias_laborados", "entero", ejemplo="31"),
            C("sueldo_base_acordado", "numero", ejemplo="4500"),
            C("sueldo_bruto", "numero", ejemplo="4500"),
        ],
    )
)

registrar(
    Importador(
        slug="rrhh_planilla",
        area="rrhh",
        modelo=PlanillaMes,
        clave=("periodo", "persona"),
        descripcion="Resumen mensual de planilla y honorarios por persona.",
        columnas=[
            C("periodo", "fecha", ejemplo="2026-10-01"),
            C(
                "dni",
                "texto",
                campo="persona",
                buscar=(Persona, "dni"),
                ejemplo="01234567",
            ),
            C("condicion", "texto", valores=CONDICION, ejemplo="PLANILLA"),
            C("dias_trabajados", "entero", ejemplo="30"),
            C("remuneracion_bruta", "numero", ejemplo="4500"),
            C("descuentos_total", "numero", obligatorio=False, ejemplo="600"),
            C("aporte_pension", "numero", obligatorio=False, ejemplo="450"),
            C("essalud", "numero", obligatorio=False, ejemplo="405"),
            C("neto_pagar", "numero", ejemplo="3900"),
            C("recibo_emitido", "bool", obligatorio=False, ejemplo=""),
        ],
    )
)


def _armar_marcacion(datos, cache):
    """Relaciona la marca con la persona por código del reloj; si no existe queda sin persona (KPI Q5 lo mide)."""
    persona = Persona.objects.filter(codigo_reloj=datos["codigo_reloj"]).first()
    return {"persona": persona}


registrar(
    Importador(
        slug="rrhh_marcaciones",
        area="rrhh",
        modelo=Marcacion,
        clave=("codigo_reloj", "fecha_hora"),
        armar=_armar_marcacion,
        descripcion="Marcas del reloj tal como salen del equipo (código y fecha-hora).",
        columnas=[
            C("codigo_reloj", "texto", ejemplo="1234567"),
            C("fecha_hora", "fechahora", ejemplo="2026-11-09 07:58"),
        ],
    )
)

registrar(
    Importador(
        slug="rrhh_obligaciones",
        area="rrhh",
        modelo=Obligacion,
        clave=("periodo", "tipo"),
        descripcion="Calendario de obligaciones: AFP (25), SCTR y vida ley (28), PLAME.",
        columnas=[
            C("periodo", "fecha", ejemplo="2026-10-01"),
            C(
                "obligacion",
                "texto",
                campo="tipo",
                valores=tuple(v for v, _ in Obligacion.Tipo.choices),
                ejemplo="AFP",
            ),
            C("fecha_limite", "fecha", ejemplo="2026-10-25"),
            C("fecha_entrega", "fecha", obligatorio=False, ejemplo="2026-10-24"),
            C(
                "responsable",
                "texto",
                obligatorio=False,
                ejemplo="Asistente de RR. HH.",
            ),
        ],
    )
)
