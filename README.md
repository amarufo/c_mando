# Cuadro de mando

Empresa: De Peru Construcción SAC
Descripción: Cuadro de mando para identificar indicadores clave de desempeño (KPI) de la empresa.

## Objetivo

**Parte 1**

- Analizar de forma profunda toda la data existente dentro de `c_mando/data` para identificar información relevante y estructurarla de manera que pueda ser utilizada en el cuadro de mando.
- El análisis debe estar orientado a identificar los datos clave, qué información es relevante, cómo debería estructurarse para automatizar el cuadro de mando.
- Descripción del árbol y estructura que tendría el cuadro de mando
- Un archivo con las preguntas clave que debo responder para proceder con la parte 2 del cuadro de mando
- Crear un informe en md con la descripción de cada archivo, incluyendo su contenido, estructura, lógica, y relevancia para el cuadro de mando. Al leer un archivo md sobre un archivo debería comprender cómo funciona dicho archivo y cómo se relaciona con el resto de la información disponible.
- Sugerir archivos limpios que debería entregar cada oficina para facilitar la integración en el cuadro de mando. Estos archivos limpios deben ser fácilmente producibles en base a sus archivos existentes actualmente: que no genere retrabajo y que mantenga la consistencia de la información.

**Parte 2**
- Definir los indicadores clave de desempeño (KPI) por área en base al análisis previo.
- Utilizar la información analizada y estructurada en la parte 1 para construir el cuadro de mando.
- Usar django, python y PostgreSQL para la implementación del cuadro de mando.
- Estructurar el cuadro de mando para actualizarla de forma manual, pero con posiblidad de escalarse automáticamente en el futuro.
- Implementar la lógica de cálculo de los KPI y su visualización en el cuadro de mando.
- Generar un informe final que incluya los resultados obtenidos y las recomendaciones para la toma de decisiones.
- Desarrollar todo dentro de "/home/amaru_fo/dph_trabajo/c_mando"
- Usar el entorno dentro de "/home/amaru_fo/dph_trabajo/c_mando/.venv"
- Seguir las buenas prácticas de desarrollo en Django y PostgreSQL para asegurar la escalabilidad y mantenibilidad del cuadro de mando.
- Debe tener una pestaña resumen de todas las áreas con los indicadores clave de desempeño (KPI) correspondientes.
- Debe haber una pestaña por área con los indicadores clave de desempeño (KPI) correspondientes.
- A futuro se añadirán más oficinas, por tanto crear una guia en md QUE ME EXPLIQUE LA ESTRUCTURA, FUNCIONAMIENTO Y FORMA DE ESCALAMIENTO DEL CUADRO DE MANDO.
- Crear un formato (paleta de colores) básico para la visualización de los indicadores clave de desempeño (KPI) en el cuadro de mando.
- Esto funcionará en local inicialmente, pero debe estar diseñado para poder escalarse automáticamente en el futuro y subirse pensando en Railway.
- Me debes enseñar (mediante documentación y código documentado) como funciona el cuadro de mando, cómo se calculan los KPI y cómo se puede escalar automáticamente en el futuro.
- La tecnología como debe estar construída debe ser similar a "/home/amaru_fo/dph_trabajo/docs/contrapropuesta_rrhh.qmd"

## Instrucciones

- Revisa minusiosamente el contenido de cada archivo dentro de cada oficina, revisa las fórmulas, como se vinculan. En conclusión: absorve completamente la estructura y la lógica de la información disponible.
- De todo lo aprendido, en varios archivos md, crea un informe de los hallazgos, incluyendo análisis de la información disponible, propuestas de indicadores clave de desempeño (KPI) por área y recomendaciones para la estructuración del cuadro de mando. Si quiero comprender los archivos de cada oficina, debería leer estos archivos para ver cómo funciona.
- Para la primera etapa puedes hacer consultas que yo las canalizaré a la persona responsable de cada área.

## Estado

Al momento se tiene información parcial inicial sobre las siguientes áreas:
- Recursos humanos
- Proyectos
- Prestamos
- Logística

## Lineamientos

- Actualmente, dentro de `c_mando/data` se encuentran carpetas por área con información en archivo tal y cual lo manejan actualmente.
- Quiero que analices la información disponible en cada área y determines qué datos son relevantes y cómo deben ser limpiados para convertirse en insumos para el cuadro de mando.
- **ACTUALMENTE NO SE TIENEN DEFINIDOS LOS INDICADORES CLAVE DE DESEMPEÑO (KPI) POR ÁREA, HAZ UNA PROPUESTA EN BASE AL ANÁLISIS DE LO EXISTENTE**

## Descripción de los archivos



### Proyectos `c_mando/data/proyectos`

Hago comentarios respecto a las hojas importantes:

- `Cambios en el categorizador.xlsx`
  - No lo tomes en cuenta, es data muy dispersa y sin estructura clara.
- `Collana 09-11.xlsx`
  - Se trabajará con esta hoja de cálculo como modelo para evaluar y extraer información clave de los proyectos
  - Contiene información sobre un proyecto específico: palabra clave: COLLANA.
  - Hojas:
    - INF-Gral: información resumida y presentación de los KPIs del proyecto
    - INF-ET: información resumen de los gastos en la elaboración del expediente técnico.
    - LB-ET: registro de gastos en personal especialista en la elaboración del expediente técnico.
    - INF-EO: información resumen de los gastos en la ejecución de obra
    - Gastos: base de datos de todos los gastos relacionados al proyecto en todas las etapas.
    - Resumen-Valorizaciones: resumen de las valorizaciones del proyecto por mes (esta información se inserta manuelmente luego de extraerlo de los informes de valorización)
    - Propuesto: hoja principal donde está el árbol de partidas para la ejecución del proyecto, con los metrados, precios unitarios por mes PROPUESTOS por partida; también incluye el propuesto meta (70%) y presupuesto propuesto (relacionada a la hoja "Propuesto"). Esta categoría de "propuesto" corresponde solo a la ejecución de obra, no a los gastos indirectos.
    - EO-PPTOs: hoja similar a "Propuesto", contiene las mismas partidas pero no los precios unitarios, pues es el presupuesto a ejecutar según el contrado del proyecto.
    - Almacén: registro de onfreso, utilizado, stock y categorización de materiales y equipos del proyecto en almacén.
- `FORMATO - PLANILLA RECURSOS HUMANOS - EJEMPLO.xlsx`
  - Plantilla de ejemplo para el registro de información de recursos humanos, incluyendo datos de personal, roles, y otros detalles relevantes para la gestión del área.
  - Bajo ese modelo el área de Recursos Humanos debe llenar información sobre el personal, roles, fechas de ingreso y salida, y otros datos relevantes para la gestión del área.
- `Iguain.xlsx`
  - Esta información es similar a los "Collana..." no tomarlo encuenta para una primera versión.

### Prestamos

Archivo: `/home/amaru_fo/dph_trabajo/c_mando/data/prestamos/Cronograma-Prestamos-Detalle-2026_REPORTE_actualizado.xlsx`

- Existen varias empresas.
- Los prestamos se realizan para diferentes empresas o prestamos personales para el gerente (LUCIO)

En este archivo se presenta un "DASHBOARD" con el resumen de todos los prestamos existentes para la empresa.

Contiene hojas por cada prestamos.

Este Excel está hecho con una IA, evalúalo completo.

### Logística

- Reporte de Requerimientos: `/home/amaru_fo/dph_trabajo/c_mando/data/logistica/CONTROL DE REQUERIMIENTOS - 12-11-2026.xlsx`
- Reporte de ordenes de compra: `/home/amaru_fo/dph_trabajo/c_mando/data/logistica/CONTROL DE ORDENES - 12-11-2026.xlsx`
- Reporte de contabilidad: `/home/amaru_fo/dph_trabajo/c_mando/data/logistica/REPORTE-CONTABILIDAD-2026-11-12.xlsx`
- Reporte de finanzas: `/home/amaru_fo/dph_trabajo/c_mando/data/logistica/REPORTE-FINANZAS-2026-11-12.xlsx`
- Reprote de tesorería: `/home/amaru_fo/dph_trabajo/c_mando/data/logistica/REPORTE-TESORERIA-2026-11-12.xlsx`

### RRHH

Revisa el flujo de `/home/amaru_fo/dph_trabajo/c_mando/data/rrhh/rrhh.mmd` llí se registra el funcionamiento de los procesos de Recursos Humanos y su vinculación con los archivos en `/home/amaru_fo/dph_trabajo/c_mando/data/rrhh`

Estos datos tienen datos anonimizados y cortos. Para la parte dos de la implementación se deberá crear datos aleatorios que simulen la operación real de Recursos Humanos.