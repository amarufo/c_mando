# 01. Proyectos: informe del archivo modelo `Collana 09-11.xlsx`

**Alcance:** análisis de `data/proyectos/`. Por indicación del responsable se ignoran `Cambios en el categorizador.xlsx` e `Iguain.xlsx` (solo se usa `Iguain` como ejemplo de la planilla de RR. HH. llenada; ver [04_rrhh.md](04_rrhh.md)). Se toma `Collana 09-11.xlsx` como **modelo** de reporte por proyecto y `FORMATO - PLANILLA RECURSOS HUMANOS - EJEMPLO.xlsx` como **plantilla que RR. HH. debe llenar** cada mes.

**Cifras de referencia** (corte manual 06/11/2026, archivo del 09/11/2026). Son datos de ejemplo del archivo; no se han validado contra contabilidad.

## 1. Qué es el archivo Collana y para qué sirve

Es un libro Excel **por proyecto** que combina cuatro cosas distintas en un solo lugar:

1. **Presupuesto y contrato** (`EO-PPTOs`, `Propuesto`): qué se vendió y qué se espera gastar.
2. **Avance físico valorizado** (`Valorizaciones`, `Resumen-Valorizaciones`): cuánto de la obra se ha ejecutado y cobrado cada mes.
3. **Gasto real** (`Gastos`): una línea por pago o gasto proyectado, clasificada con un catálogo de categorías (`categorias_global`).
4. **Informes ejecutivos** (`INF-Gral`, `INF-ET`, `INF-EO`, `LB-ET`): resumen del proyecto con indicadores de valor ganado (EVM: BAC, EV, PV, AC, CV, SV, CPI, SPI).

Más una hoja de **Almacén** (stock de materiales, EPP y herramientas de la obra).

Es el único archivo que ya intenta medir **rentabilidad y desempeño por proyecto**. Por eso es la base natural del módulo "Proyectos" del cuadro de mando.

## 2. Datos del proyecto Collana

| Dato                       | Valor                                                                      |
| -------------------------- | -------------------------------------------------------------------------- |
| Proyecto                   | Polideportivo Ccollana (creación del servicio deportivo)                   |
| Entidad contratante        | Municipalidad Provincial de Huanta (Ayacucho)                              |
| CUI / Código               | 2686704 / 0103                                                             |
| Expediente técnico (ET)    | Acta de terreno 04/04/2026, plazo 60 días, aprobación calculada 03/06/2026 |
| Ejecución de obra (EO)     | Inicio 17/07/2026, plazo 150 días, fin calculado 14/12/2026                |
| Fecha de corte del informe | 06/11/2026 (**escrita a mano** en `INF-Gral!F16`)                          |
| Primer gasto registrado    | 29/03/2025 (`=MIN(Gastos!G:G)`), es decir, hay gasto precontractual        |

## 3. Mapa de hojas

| Hoja                                    | Visible | Qué contiene                                                                                                 | Relación con otras hojas                                                         |
| --------------------------------------- | ------- | ------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------- |
| `INF-Gral`                              | Sí      | Informe ejecutivo del proyecto: datos, cuadro Contrato / Meta 70 % / Propuesto, tabla EVM, resumen de gastos | Lee `EO-PPTOs!F1188:L1197`, `INF-ET`, `INF-EO` y tablas dinámicas sobre `Gastos` |
| `INF-ET`                                | Sí      | Informe del expediente técnico (EVM de la fase ET)                                                           | Presupuesto ET desde `EO-PPTOs`; gasto desde tabla dinámica de `Gastos`          |
| `LB-ET`                                 | Sí      | Línea base del ET: planificado vs real vs pendiente por rubro y matriz mensual de personal profesional       | Gasto real por `GETPIVOTDATA` sobre `INF-ET`                                     |
| `INF-EO`                                | Sí      | Informe de ejecución de obra: EVM, tablas mensuales PV / EV / AC por escenario                               | `Resumen-Valorizaciones`, `EO-PPTOs`, pivote de `Gastos`                         |
| `Resumen-Valorizaciones`                | Sí      | Cronograma mensual de valorización: Contrato, Meta 70 %, Propuesto y Real                                    | `Propuesto` (fila 7) y `Valorizaciones` (filas 9 y 10)                           |
| `Valorizaciones`                        | Sí      | Árbol de partidas con metrado valorizado por mes (jul-dic), % y saldo                                        | Totales en filas 1193-1194                                                       |
| `Propuesto`                             | Sí      | Árbol de partidas con la propuesta interna: metrado, S/ y % por mes (jul-nov)                                | Totales en filas 1188-1192                                                       |
| `EO-PPTOs`                              | Sí      | Presupuesto de obra en tres versiones (Base 100 %, Meta 70 %, Propuesto) más supervisión, ET y liquidación   | Alimenta `INF-Gral`, `INF-ET`, `INF-EO`, `LB-ET`                                 |
| `ET-PPTOs`                              | Oculta  | Árbol del presupuesto del ET                                                                                 | `EO-PPTOs`                                                                       |
| `Gastos`                                | Sí      | **Base de datos de pagos/gastos (386 filas)**                                                                | Fuente de todos los AC (costo real)                                              |
| `BD`                                    | Oculta  | Listas de apoyo (PAGADO / PENDIENTE)                                                                         | Validación de `Gastos[ESTADO]`                                                   |
| `categorias_global`                     | Oculta  | Catálogo de 444 categorías (código, componente, ítem, etapa, tipo de costo...)                               | `Gastos` hace `VLOOKUP` por `CÓDIGO`                                             |
| `Almacén`                               | Sí      | 169 ítems con ingresado, utilizado y stock                                                                   | Independiente (no se conecta con `Gastos`)                                       |
| `EVM-Gral`, `EVM-EO`                    | Sí      | Hojas de solo gráfico: curvas de valor ganado (PV, EV, AC) del proyecto y de la obra                         | Gráficos sobre las tablas de `INF-Gral` e `INF-EO`                               |
| `GASTOS-Gral`, `GASTOS-ET`, `GASTOS-EO` | Sí      | Hojas de solo gráfico: gastos por componente y mes                                                           | Gráficos sobre las tablas dinámicas de `Gastos`                                  |
| `Flujo de Caja`                         | Sí      | Hoja de solo gráfico: flujo de caja del proyecto                                                             | Gráfico sobre los gastos pagados y pendientes                                    |

## 4. Lógica por hoja

### 4.1 `Gastos` (la tabla más importante)

| Columna                    | Contenido                                                       | Observaciones                                                                                       |
| -------------------------- | --------------------------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| ID ADM / ID TESO / ID FNZS | Códigos de otros reportes (Administración, Tesorería, Finanzas) | Parcialmente llenos. Sirven para conciliar, pero no hay regla única                                 |
| CÓDIGO                     | Código de categoría, p. ej. `01.02.03`                          | Dato manual, es la llave hacia `categorias_global`                                                  |
| COMPONENTE, ITEM           | `VLOOKUP(CÓDIGO, categorias_global, ...)`                       | Fórmula; si el código no existe, da error                                                           |
| FECHA DE PAGO              | Fecha real o **fecha proyectada**                               | Mezcla pagado y proyectado (hasta 01/01/2027)                                                       |
| PROVEEDOR, CONCEPTO        | Texto libre                                                     | 172 valores distintos de proveedor; hay roles ("peón", "almacenero") mezclados con razones sociales |
| SOLES, DOLARES             | Importe en cada moneda                                          | 32 filas solo en dólares                                                                            |
| MONTO (S/.)                | `=SOLES + DOLARES * 3.5`                                        | **Tipo de cambio fijo 3.5** dentro de la fórmula                                                    |
| ESTADO                     | `PAGADO` (320) o `PENDIENTE` (66)                               |                                                                                                     |
| OBS                        | Notas ("RRHH", "GASTO PROYECTADO")                              | Es el único marcador de proyectado vs real                                                          |
| PAGO REAL                  | Fecha de pago efectiva                                          | Casi no se usa                                                                                      |
| RQ                         | Número de requerimiento                                         | **Vacía en las 386 filas**: no hay vínculo con Logística                                            |

Totales (S/): gasto total 1,858,248; pagado 1,470,876; pendiente (proyectado) 387,372.

Distribución por componente (suma de `MONTO (S/.)`, pagado + pendiente):

| Componente                  | S/      |
| --------------------------- | ------- |
| 00 Precontractual           | 412,692 |
| 01 Ejecución de obra        | 720,817 |
| 02 Gastos generales         | 227,991 |
| 03 Expediente técnico       | 381,441 |
| 04 Supervisión ET           | 30,000  |
| 05 Supervisión de obra      | 62,807  |
| 3101 Gastos administrativos | 22,500  |

Dos tipos de filas **no son gasto operativo del proyecto** y conviene identificarlas: pagos de **préstamos** (por ejemplo cuotas de un financiamiento, ~20 filas) y **reembolsos** a una persona (~17 filas). Son el punto de unión con la oficina de Préstamos y con Tesorería (ver [05_arbol_y_modelo_datos.md](05_arbol_y_modelo_datos.md)).

### 4.2 `categorias_global`

444 filas: 427 de nivel `Ítem` y 17 de nivel `Subcategoría`. Columnas: `Codigo_Item`, componente, ítem, `Nivel`, `Codigo_Sub`, `Subcategoria`, `Codigo_Fase`, `Etapa`, `Nombre_Etapa_Largo`, `Tipo_Costo` (Variable 380 / Fijo 64), `Tipo_Personal`, `Categoria_Especial` (Laboral / Financiero / Social), `Descripcion`, `Keywords`, `Es_Fierro`, `Es_Otros`, `Es_Nuevo`.

- Componentes: 00 Precontractual, 01 Ejecución, 02 Gastos generales, 03 Expediente técnico, 04 Supervisión ET, 05 Supervisión de obra, 06 Gastos de gestión, 07 Liquidación, 3101 Gastos administrativos.
- `Es_Fierro` marca el rubro de **gestión/comisión** (se sospecha que es el "diezmo"; confirmar con el responsable).
- `Categoria_Especial` permite agrupar costos laborales, financieros y sociales **de forma transversal** al componente. Es una dimensión muy útil para el cuadro de mando.
- Es un catálogo **global** (no solo de Collana). Es el candidato natural a catálogo maestro único de la empresa.

### 4.3 `EO-PPTOs` y `Propuesto`

Tres escenarios sobre el mismo árbol de partidas (metrado × precio unitario):

| Escenario                 | Qué representa                                     | Cómo se calcula                          |
| ------------------------- | -------------------------------------------------- | ---------------------------------------- |
| **Contrato (Base 100 %)** | Lo contratado con la entidad                       | Metrado × PU contractual                 |
| **Meta 70 %**             | Costo objetivo interno                             | PU × 0.7 (factor fijo en fórmula)        |
| **Propuesto**             | Presupuesto interno detallado, partida por partida | PU y metrados manuales; % mensual manual |

Estructura de totales (filas 1188-1197): costo directo → gastos generales → utilidad → subtotal → IGV 18 % → **costo de obra** → supervisión → expediente técnico → liquidación → **costo total del proyecto**.

| Concepto (S/)            | Contrato       | Meta 70 %     | Propuesto     |
| ------------------------ | -------------- | ------------- | ------------- |
| Costo directo            | 4,183,897      | 2,928,728     | 3,013,200     |
| Gastos generales         | 543,907 (13 %) | 380,735       | 150,660 (5 %) |
| Utilidad                 | 418,390 (10 %) | 292,873       | 150,660 (5 %) |
| Subtotal                 | 5,146,194      | 3,602,336     | 3,314,520     |
| IGV 18 %                 | 926,315        | 648,420       | 596,614       |
| **Costo de obra**        | **6,072,509**  | **4,250,756** | **3,911,133** |
| Supervisión              | 267,884        | 187,519       | —             |
| Expediente técnico       | 194,825        | 136,377       | —             |
| Liquidación              | 5,452          | 3,817         | —             |
| **Costo total proyecto** | **6,540,670**  | **4,578,469** | —             |

### 4.4 `Valorizaciones` y `Resumen-Valorizaciones`

- `Valorizaciones` replica el árbol de partidas y registra por mes (jul-dic) el metrado ejecutado. Calcula el parcial `ROUND(metrado × PU)`, el % de avance, el acumulado y el saldo.
- `Resumen-Valorizaciones` arma el cronograma mensual:
  - **Fila 3 Contrato** y su %: montos mensuales **escritos a mano** (suman 6,072,509).
  - **Fila 5 Meta**: `=Contrato × 0.7`.
  - **Fila 7 Propuesto**: viene de `Propuesto!H1192, K1192, N1192, Q1192, T1192`.
  - **Fila 9 Real** y **fila 10 %**: viene de `Valorizaciones!H1193, K1193, N1193, Q1193, T1193, W1193`.
- Avance real valorizado a la fecha: jul 293,032; ago 122,905; set 361,230; oct 771,093. **Total 1,548,261, que es el 25.5 % del contrato.**

### 4.5 `INF-Gral`, `INF-ET`, `INF-EO` (valor ganado)

Definiciones usadas en el archivo:

| Sigla    | Significado              | Fórmula en el archivo                                                                  |
| -------- | ------------------------ | -------------------------------------------------------------------------------------- |
| BAC      | Presupuesto total        | `INF-ET` + `INF-EO` (costo de obra con IGV)                                            |
| EV       | Valor ganado ("cobrado") | En EO: `% real acumulado × BAC`; en ET: se supone **100 %** (EV = PV = BAC)            |
| PV       | Valor planificado        | Suma acumulada de las filas 3, 5 o 7 de `Resumen-Valorizaciones` hasta el mes de corte |
| AC       | Costo real ("gastado")   | `GETPIVOTDATA("MONTO (S/.)", ...)` sobre tablas dinámicas de `Gastos`                  |
| CV, SV   | `EV − AC`, `EV − PV`     |                                                                                        |
| CPI, SPI | `EV / AC`, `EV / PV`     |                                                                                        |

Resultados del archivo (a la fecha de corte):

| Indicador                | Contrato | Meta 70 % | Propuesto |
| ------------------------ | -------- | --------- | --------- |
| CPI `INF-Gral` (ET + EO) | 1.19     | 0.83      | 0.68      |
| SPI `INF-Gral`           | 0.54     | 0.54      | 0.28      |
| CPI `INF-EO` (solo obra) | 2.08     | 1.46      | 1.34      |
| SPI `INF-EO`             | 0.51     | 0.51      | 0.28      |

`INF-EO` también guarda tablas mensuales (jul-dic) de PV, EV y AC por escenario, base de los gráficos de curva S.

### 4.6 `LB-ET`

Línea base del expediente técnico: cinco rubros (carta fianza 4 %, profesionales, gastos generales, consultoría, estudios básicos) con columnas **Planificado / Real / Pendiente**, y una **matriz de personal profesional por mes** (ET may-jun, EO jul-nov, liquidación dic) con montos por persona. Varios montos están digitados sueltos (por ejemplo 20,000 en celdas aisladas), sin una tabla de contratos.

### 4.7 `Almacén`

169 ítems: Material 109, EPP 30, Herramientas y equipos 30. Columnas: código `MATnnn`, producto, unidad, ingresado, utilizado, **stock = ingresado − utilizado**, categoría. Actualizado al 02/11/2026. No hay precios ni costos, por lo que no se puede valorizar el inventario ni cruzarlo con el gasto. No hay stock negativo.

## 5. Hallazgos de calidad y consistencia

1. **El EVM mezcla alcances.** En `INF-Gral` el AC (1.47 M) incluye gasto precontractual y de expediente técnico, mientras el EV de obra solo cuenta obra, y el EV del ET se fija en 100 %. Por eso el mismo proyecto tiene CPI 1.19 en un informe y 2.08 en otro. Hay que **definir el alcance de cada indicador** (ver [06_propuesta_kpi.md](06_propuesta_kpi.md)).
2. **BAC con IGV.** El costo de obra incluye 18 % de IGV, pero el gasto pagado puede incluir o no IGV según el comprobante. El valor ganado y el costo real deben compararse en la misma base (sin IGV).
3. **Corte y cronograma manuales.** `INF-Gral!F16` (fecha de corte) y la fila 3 del cronograma contractual son datos digitados. Un olvido desfasa todo el informe.
4. **Dependencia de tablas dinámicas.** Los AC usan `GETPIVOTDATA`; si la tabla dinámica no se actualiza, el informe muestra cifras viejas sin avisar.
5. **Tipo de cambio fijo 3.5** dentro de `MONTO (S/.)`. Distorsiona los 32 pagos en dólares y no es auditable.
6. **Real y proyectado en la misma tabla.** Se distinguen por `ESTADO` y por un texto en `OBS`. Cualquier suma sin filtrar mezcla ambos.
7. **Sin vínculo con Logística.** La columna `RQ` está vacía. El gasto de proyecto no se puede conciliar con requerimientos, órdenes ni facturas.
8. **Costos no operativos dentro del proyecto** (préstamos, reembolsos). Inflan el AC y complican la rentabilidad.
9. **Metas con factor fijo 0.7** y gastos generales/utilidad con porcentajes distintos por escenario: son supuestos del negocio que deben vivir como parámetros, no en fórmulas.
10. **Árbol de partidas de más de 1,100 filas duplicado** en `EO-PPTOs`, `Propuesto` y `Valorizaciones`; cualquier cambio de partida requiere edición triple.
11. `Almacén` no tiene precio ni vínculo con `Gastos`.
12. Las **tablas dinámicas no se pueden leer con librerías de Python** (solo se ven sus valores guardados). Para automatizar hay que reconstruirlas desde `Gastos`.

## 6. Qué es "dato clave" para el cuadro de mando

| Dato                                                                          | Fuente en Collana               | Por qué importa                         |
| ----------------------------------------------------------------------------- | ------------------------------- | --------------------------------------- |
| Identificación del proyecto (CUI, código, entidad, ubicación, fechas, plazos) | `INF-Gral`                      | Dimensión Proyecto                      |
| Presupuesto por escenario (contrato, meta, propuesto) y sus componentes       | `EO-PPTOs`                      | Línea base y margen esperado            |
| Cronograma mensual de valorización planificado                                | `Resumen-Valorizaciones` fila 3 | Curva S planificada                     |
| Valorización real mensual                                                     | `Valorizaciones`                | Avance y facturación                    |
| Gasto real y proyectado por componente, categoría y mes                       | `Gastos`                        | Costo, flujo y desviaciones             |
| Catálogo de categorías                                                        | `categorias_global`             | Clasificación homogénea entre proyectos |
| Personal profesional asignado por mes                                         | `LB-ET`                         | Costo de personal clave                 |
| Stock de almacén                                                              | `Almacén`                       | Control de consumos (a futuro)          |

## 7. Plantilla de RR. HH. por proyecto: `FORMATO - PLANILLA RECURSOS HUMANOS - EJEMPLO.xlsx`

Es el archivo que RR. HH. envía a cada proyecto (o recibe de ellos) cada mes. Se describe con detalle en [04_rrhh.md](04_rrhh.md), sección 5; aquí se resume su papel:

- Hoja `SET`: cabecera con **Empresa, Proyecto y Mes/Año** (celda D5), días del mes calculados (`I5 = DAY(EOMONTH(D5,0))`).
- Cuatro bloques: **Personal clave, No clave, Administrativo, Mano de obra**.
- Por trabajador: N.º, DNI, nombre, cargo, condición laboral (planilla o recibo por honorarios), banco, CCI, fecha de inicio, días laborados, sueldo base acordado, **sueldo bruto = base / días del mes × días laborados**, observación.
- Resumen por categoría y por condición con `SUMIF`.
- Ejemplo incluido: carretera JU104, set-26, empresa DPHC, total S/ 54,800.

Es la **única fuente estructurada del costo de personal por proyecto**. Hoy el gasto de RR. HH. entra a `Gastos` como líneas sueltas con "RRHH" en observaciones; debe cuadrar con esta planilla.

## 8. Cómo se relaciona Proyectos con el resto

| Con                      | Vínculo actual                                                                      | Vínculo deseable                                              |
| ------------------------ | ----------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| RR. HH.                  | Observación "RRHH" en `Gastos`; nombre del proyecto como texto libre en la planilla | Código de proyecto en la planilla y en el maestro de personal |
| Logística                | Ninguno (`RQ` vacío)                                                                | N.º de requerimiento y de orden en cada gasto                 |
| Préstamos                | Cuotas de préstamo anotadas como gasto del proyecto                                 | Campo "origen del fondo" y tipo de gasto "financiero"         |
| Contabilidad / Tesorería | IDs ADM / TESO / FNZS parciales                                                     | ID único de comprobante o pago                                |

Véase el modelo transversal en [05_arbol_y_modelo_datos.md](05_arbol_y_modelo_datos.md).
