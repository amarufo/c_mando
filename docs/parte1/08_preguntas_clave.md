# 08. Preguntas clave por área

Preguntas que **solo el responsable de cada área puede contestar** y que condicionan el diseño del cuadro de mando. Cada pregunta indica por qué importa. Las marcadas con **(bloqueante)** impiden definir un indicador o un archivo hasta que se respondan.

Formato sugerido de respuesta: una línea por pregunta, con el número (por ejemplo, `P-03: ...`).

## 0. Gerencia

| N.º  | Pregunta                                                                                                                                                 | Por qué importa                          |
| ---- | -------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------- |
| G-01 | ¿Qué decisiones quiere tomar con el cuadro de mando y con qué frecuencia lo consultará (diaria, semanal, mensual)?                                       | Define qué indicadores van en el resumen |
| G-02 | ¿Qué empresas deben aparecer: solo DPH y DPHC, o también DPH Carga, Cosudeco, Perú Seguro 365, DPH Capital y Consorcio Supervisor Junín? ¿Se consolidan? | Alcance de las dimensiones               |
| G-03 | ¿Los préstamos personales del gerente deben mostrarse junto a la deuda de las empresas o separados? (bloqueante)                                         | Sensibilidad y lectura de la deuda       |
| G-04 | ¿Quién puede ver qué? (planillas, deuda y costo por persona son información sensible)                                                                    | Perfiles de acceso                       |
| G-05 | ¿Cuáles son los 3 indicadores que hoy le generan más preocupación?                                                                                       | Priorizar la primera versión             |
| G-06 | ¿Hay metas o umbrales ya definidos (margen mínimo, plazo máximo de pago, tope de deuda, etc.)?                                                           | Semáforos                                |
| G-07 | Para los dos periodos de datos que existen (octubre y noviembre 2026): ¿hay información de periodos anteriores que debamos incorporar?                   | Tendencias e históricos                  |

## 1. Proyectos (responsable de Proyectos y administradores)

| N.º  | Pregunta                                                                                                                                         | Por qué importa                                             |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------- |
| P-01 | ¿Cuál es la definición oficial de **avance** y de **valor ganado**: valorización aprobada, avance físico o cobro? (bloqueante)                   | Un mismo proyecto da CPI de 1.19 y de 2.08 según el alcance |
| P-02 | ¿El expediente técnico y la obra se miden como **un** proyecto o como dos? ¿El gasto precontractual cuenta como costo del proyecto? (bloqueante) | Alcance del costo real                                      |
| P-03 | ¿Qué significa exactamente "**Meta 70 %**" y "**Propuesto**"? ¿Quién los fija y cuándo se actualizan?                                            | Sentido del margen esperado                                 |
| P-04 | ¿El presupuesto contractual incluye IGV? ¿Los gastos se registran con o sin IGV? (bloqueante)                                                    | Comparar peras con peras                                    |
| P-05 | ¿Qué proyectos están activos hoy y cuántos tienen un libro como el de Collana? ¿Es el mismo formato en todos? (bloqueante)                       | Alcance de la carga                                         |
| P-06 | ¿Quién fija la **fecha de corte** del informe y cada cuánto se actualiza?                                                                        | Hoy es manual                                               |
| P-07 | ¿Cómo se calcula el **cronograma contractual mensual** (fila 3 de `Resumen-Valorizaciones`)? ¿Es un plan o un valor contractual?                 | Curva S planificada                                         |
| P-08 | ¿El **tipo de cambio fijo de 3.5** es una política? ¿Se debe usar el del día de pago?                                                            | Gastos en dólares                                           |
| P-09 | ¿Qué es "**Es_Fierro**" en el catálogo de categorías? ¿Cómo se trata ese costo en el margen?                                                     | Costo de gestión                                            |
| P-10 | ¿Los pagos de **préstamos** y los **reembolsos** que aparecen en `Gastos` son costo del proyecto o movimientos de caja?                          | Rentabilidad                                                |
| P-11 | ¿Quién llena la columna `RQ` de `Gastos` y por qué está vacía? ¿Es posible que cada gasto traiga el número de orden?                             | Unión con Logística                                         |
| P-12 | ¿Las filas "GASTO PROYECTADO" son una proyección de costos o de pagos? ¿Quién las revisa?                                                        | Real vs. proyectado                                         |
| P-13 | ¿Se desea conservar las pestañas de gráficos (`EVM-*`, `GASTOS-*`, `Flujo de Caja`) como reportes finales?                                       | Diseño de pantallas                                         |
| P-14 | ¿Cómo se registra el cobro de cada valorización (fecha, monto, retención, adelanto)?                                                             | Flujo de caja del proyecto                                  |
| P-15 | ¿Se quiere medir el inventario de almacén con precios? ¿Quién lo actualiza y cada cuánto?                                                        | Alcance de `Almacén`                                        |
| P-16 | ¿Qué proyectos existen en Logística (35) y en Contabilidad (39 códigos CC2)? ¿Cuál es la lista oficial con código y nombre corto? (bloqueante)   | Catálogo de centros de costo                                |
| P-17 | ¿Se desea un código único de proyecto (CUI o código interno) igual para todas las áreas?                                                         | Dimensión Proyecto                                          |

## 2. Logística

| N.º  | Pregunta                                                                                                                                | Por qué importa             |
| ---- | --------------------------------------------------------------------------------------------------------------------------------------- | --------------------------- |
| L-01 | ¿De qué sistema vienen las exportaciones? ¿Se pueden obtener de forma automática, con las mismas columnas y con histórico? (bloqueante) | Frecuencia y automatización |
| L-02 | ¿Cuál es el flujo oficial de estados de un RQ y de una orden? ¿Qué significa "Observada" y "Observada · reenviada"?                     | Diccionario de estados      |
| L-03 | ¿Qué es una **regularización**? ¿Es una compra hecha antes de la aprobación? ¿Quién la autoriza y qué plazo se considera aceptable?     | Cumplimiento del proceso    |
| L-04 | ¿Cuál es la política de **emergencia**? ¿Por qué el 55 % de los RQ es de emergencia?                                                    | Planificación de compras    |
| L-05 | ¿Por qué el precio solo está en 19 % de los ítems de RQ? ¿Es posible completarlo?                                                       | Ahorro y presupuesto        |
| L-06 | ¿Una orden puede cargar costos a más de un proyecto? ¿Cómo se prorratea? (6 casos hoy)                                                  | Imputación de costos        |
| L-07 | ¿Cuál es el catálogo oficial de **condiciones de pago**? (hoy 19 variantes)                                                             | Normalización               |
| L-08 | ¿Qué se hace con los anticipos y las valorizaciones del proveedor? ¿Cómo se amortiza un anticipo?                                       | Cuenta por pagar neta       |
| L-09 | ¿Qué diferencia legítima hay entre total de orden y total facturado? (hoy 43 de 279) ¿Quién revisa las sobrefacturaciones?              | Control de compras          |
| L-10 | ¿Cuál es el **plazo máximo aceptable** entre RQ y orden, y entre orden y entrega?                                                       | Umbrales de semáforo        |
| L-11 | ¿Quién es responsable de corregir errores como la fecha de 2024 en una factura de 2026?                                                 | Calidad en el origen        |
| L-12 | ¿Pasajes aéreos y terrestres y recibos por honorarios son compras de Logística o gastos de otra área?                                   | Doble registro con RR. HH.  |
| L-13 | ¿Quiénes son los compradores / asignados y se mide su desempeño?                                                                        | Indicadores por persona     |
| L-14 | ¿Las órdenes de empresas distintas a DPH y DPHC (Cosudeco, Perú Seguro 365, etc.) las gestiona Logística de la misma forma?             | Alcance                     |

## 3. Contabilidad, Finanzas y Tesorería

| N.º  | Pregunta                                                                                                                                                                                                               | Por qué importa          |
| ---- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------ |
| C-01 | ¿Las tres exportaciones (Contabilidad, Finanzas, Tesorería) son realmente la misma tabla en etapas distintas? ¿Por qué se pierden comprobantes (1 de Contabilidad a Finanzas, 5 de Finanzas a Tesorería)? (bloqueante) | Diseño de la tabla única |
| C-02 | ¿Cuál es la **llave oficial** de un comprobante: RUC + serie-número? ¿Hay series repetidas legítimamente?                                                                                                              | Conciliación             |
| C-03 | ¿Cuál es la **fuente de verdad del importe** cuando hay diferencias entre Logística y Contabilidad (35 casos)?                                                                                                         | Conciliación             |
| C-04 | ¿Qué significan exactamente los estados de pago: "Programado", "Pagado", "Por detracción/retención", "Pendiente de conformidad", "Conforme", "En revisión"?                                                            | Diccionario de estados   |
| C-05 | ¿Cómo se maneja la **detracción** y la **retención de garantía**? ¿Se registran como pago separado?                                                                                                                    | Cuenta por pagar         |
| C-06 | ¿Cuál es el **calendario de pago** (días fijos de la semana o del mes)? ¿Quién reprograma y con qué criterio?                                                                                                          | Calendario de pagos      |
| C-07 | ¿Qué centros de costo CC1 (partida) son obligatorios para cada tipo de CC2? ¿Quién valida los comprobantes con "Por ítem" o sin CC1?                                                                                   | Imputación               |
| C-08 | ¿Contabilidad tiene un plan de cuentas y un asiento por comprobante? ¿Se requiere ese nivel en el cuadro de mando?                                                                                                     | Alcance                  |
| C-09 | ¿Se necesitan ingresos (cobros de valorizaciones) para ver caja? ¿De qué archivo salen? (bloqueante para el flujo de caja)                                                                                             | Flujo de caja            |
| C-10 | ¿Quién fija el **tipo de cambio** de cada movimiento? ¿Hay una tabla diaria?                                                                                                                                           | Moneda                   |
| C-11 | ¿Hay cuentas por cobrar (valorizaciones pendientes, adelantos)? ¿Dónde se registran?                                                                                                                                   | Liquidez                 |
| C-12 | ¿Qué reportes tributarios mensuales deben aparecer en el cuadro de mando (PDT, PLE, detracciones)?                                                                                                                     | Cumplimiento             |
| C-13 | ¿Los textos libres de las exportaciones (glosas, observaciones) llevan datos sensibles? ¿Se pueden eliminar de la entrega?                                                                                             | Seguridad                |

## 4. Préstamos y deuda

| N.º  | Pregunta                                                                                                                 | Por qué importa                  |
| ---- | ------------------------------------------------------------------------------------------------------------------------ | -------------------------------- |
| F-01 | ¿Quién mantiene el archivo y de qué fuente se alimenta cada hoja (contratos, estados de cuenta, Tesorería)? (bloqueante) | Responsable y frecuencia         |
| F-02 | ¿Cuál es la **lista completa de préstamos y deudas vigentes**? ¿Hay deudas que no están en el archivo?                   | Completitud                      |
| F-03 | ¿El archivo actual es confiable en importes? Se hizo con apoyo de IA: ¿quién lo revisó y contra qué documento?           | Confianza en los datos           |
| F-04 | ¿Cómo se debe registrar el **pago real** de una cuota (fecha, importe, operación) y quién lo hace? (bloqueante)          | Hoy se asume pagado si ya venció |
| F-05 | ¿Qué es cada hoja oculta y cada hoja de detalle sin descripción clara? ¿Se deben conservar?                              | Depurar el catálogo              |
| F-06 | ¿La hoja `RESUMEN_CFIN` es válida o debe descartarse? ¿Se necesita TCEA por préstamo?                                    | Costo financiero                 |
| F-07 | ¿Los **pagarés** tienen intereses mensuales, capital al final? ¿Hay un calendario formal firmado?                        | Cálculo de cuotas                |
| F-08 | ¿Qué parte de la deuda financia qué proyecto o necesidad? ¿Se debe imputar el costo financiero a cada proyecto?          | Rentabilidad                     |
| F-09 | ¿Qué tipo de cambio se usa para la deuda en dólares (de la fecha del cierre, del desembolso, fijo)?                      | Valoración                       |
| F-10 | ¿Hay **covenants** o límites impuestos por acreedores (ratios, garantías, cartas fianza)?                                | Alertas                          |
| F-11 | ¿Cuál es la política ante la concentración de vencimientos (por ejemplo, el mes de diciembre)? ¿Se planea refinanciar?   | Riesgo de caja                   |
| F-12 | ¿Los préstamos personales del gerente se pagan desde Tesorería de la empresa? ¿Se registran como retiro o como gasto?    | Tratamiento contable             |
| F-13 | ¿Se necesitan préstamos **otorgados** (a terceros o a trabajadores) en el cuadro de mando?                               | Alcance                          |

## 5. Recursos humanos

| N.º  | Pregunta                                                                                                                                                              | Por qué importa                                      |
| ---- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------- |
| H-01 | ¿Cuál es la **fuente oficial del personal** (`MAESTRO 2026`) y cuántas hojas/mes mantiene? ¿Se puede tener un único registro con fechas de inicio y fin? (bloqueante) | Histórico y rotación                                 |
| H-02 | ¿Cuántas personas hay hoy en total por empresa y condición (planilla / RH)? ¿Cuántas por proyecto?                                                                    | Validar la dotación (el archivo solo tiene ejemplos) |
| H-03 | ¿Cuál es la regla de **categoría** (clave / no clave / administrativo / mano de obra)? ¿Quién la asigna y es un campo del maestro? (bloqueante)                       | Reporte por proyecto                                 |
| H-04 | ¿Una persona puede trabajar en más de un proyecto en el mismo mes? ¿Cómo se reparte su costo?                                                                         | Imputación                                           |
| H-05 | ¿El **código del reloj** coincide con el DNI sin ceros? ¿Qué son los códigos de 1 y 2 dígitos? ¿Hay relojes en cada sede/proyecto? (bloqueante)                       | Cruce de marcaciones                                 |
| H-06 | ¿Cómo se indica entrada y salida? ¿Qué regla define tardanza y falta (horario, tolerancia)?                                                                           | Cálculo de tardanzas                                 |
| H-07 | ¿Cómo se registran las incidencias de obra (faltas, permisos, descansos)? ¿Quién las reporta?                                                                         | Asistencia                                           |
| H-08 | ¿Los parámetros (RMV, asignación familiar, tasas de AFP, EsSalud) quién los actualiza y cuándo?                                                                       | Parámetros con vigencia                              |
| H-09 | ¿Qué cifras de `Hoja1` (39 en planilla, 78 en honorarios) son reales y de qué mes? ¿Qué sedes existen?                                                                | Dotación y sedes                                     |
| H-10 | ¿El costo por proyecto del formato (sueldo bruto) incluye cargas sociales, provisiones de CTS, gratificación y vacaciones? ¿Debe incluirlas?                          | Costo total real                                     |
| H-11 | ¿Qué fecha y formato tiene el **PLAME** y quién lo presenta? ¿Se dispone de un formato?                                                                               | Obligación pendiente                                 |
| H-12 | ¿Qué contratos (Word) se generan hoy y cuáles son las plantillas por condición?                                                                                       | Automatización                                       |
| H-13 | ¿Qué datos del personal son confidenciales y no deben llegar al cuadro de mando?                                                                                      | Seguridad                                            |
| H-14 | ¿Los recibos por honorarios también se registran en Logística (comprobantes de tipo RxH)? ¿Cuál es el registro oficial?                                               | Doble registro                                       |
| H-15 | ¿Se desea medir clima laboral, capacitaciones, evaluaciones o salud ocupacional? ¿Hay datos?                                                                          | Alcance                                              |

## 6. Preguntas transversales (a todos)

| N.º  | Pregunta                                                                                                       |
| ---- | -------------------------------------------------------------------------------------------------------------- |
| T-01 | ¿Quién es el responsable de entregar cada archivo y cuál es la fecha límite mensual / semanal?                 |
| T-02 | ¿Se acepta el modelo de archivos limpios de [07_archivos_limpios.md](07_archivos_limpios.md)? ¿Qué cambiarían? |
| T-03 | ¿Qué información no debe salir de la oficina bajo ninguna circunstancia?                                       |
| T-04 | ¿Hay otro archivo, sistema o base que no nos hayan mostrado y que sea la verdadera fuente de algún dato?       |
| T-05 | ¿Qué reportes preparan hoy a mano y cuánto tiempo les toma? (para priorizar la automatización)                 |
