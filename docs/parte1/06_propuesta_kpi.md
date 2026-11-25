# 06. Propuesta de KPI por área

Hoy **no hay KPI definidos** en ningún área. Esta es una propuesta inicial para validar con cada responsable (ver [08_preguntas_clave.md](08_preguntas_clave.md)). Criterios de selección:

- Se pueden calcular con los datos que ya existen (o con una columna adicional fácil de capturar).
- Responden a una decisión concreta.
- Tienen definición clara de alcance (qué entra y qué no), para evitar el problema que hoy tiene el valor ganado de Collana (ver [01_proyectos.md](01_proyectos.md)).

Prioridad: **A** = primera versión del cuadro de mando; **B** = segunda etapa; **C** = requiere datos que hoy no existen.

Frecuencia: S = semanal, M = mensual.

## 1. Proyectos

| #   | KPI                                   | Fórmula                                                                                                     | Fuente                            | Frec. | Prior.         |
| --- | ------------------------------------- | ----------------------------------------------------------------------------------------------------------- | --------------------------------- | ----- | -------------- |
| P1  | **Avance valorizado**                 | Valorización real acumulada / monto contratado                                                              | `Valorizaciones`                  | M     | A              |
| P2  | **Avance planificado**                | Valorización planificada acumulada / monto contratado                                                       | `Resumen-Valorizaciones`          | M     | A              |
| P3  | **SPI** (cumplimiento de cronograma)  | EV / PV, ambos en la misma base (sin IGV)                                                                   | P1 y P2                           | M     | A              |
| P4  | **Costo real acumulado (AC)**         | Suma de gastos pagados del proyecto, **solo componentes de obra**, sin IGV                                  | `Gastos`                          | M     | A              |
| P5  | **CPI** (eficiencia de costo)         | EV / AC con el mismo alcance                                                                                | P1 y P4                           | M     | A              |
| P6  | **Margen esperado al cierre**         | (Monto contratado − costo estimado al cierre) / monto contratado, con costo estimado = AC + costo pendiente | `Gastos`, `EO-PPTOs`              | M     | A              |
| P7  | **Desviación frente a la meta 70 %**  | Gasto real acumulado de obra / (70 % del presupuesto × avance real)                                         | `Gastos`, `EO-PPTOs`              | M     | A              |
| P8  | **Gasto por componente**              | Suma de `MONTO (S/.)` por componente, tipo (pagado / pendiente)                                             | `Gastos`                          | M     | A              |
| P9  | **Pendiente de pago del proyecto**    | Gastos en estado PENDIENTE (con y sin "proyectado")                                                         | `Gastos`                          | S     | A              |
| P10 | **Flujo de caja del proyecto**        | Cobros (valorizaciones pagadas) − pagos, por mes                                                            | `Gastos`, valorizaciones cobradas | M     | B              |
| P11 | **Costos no operativos**              | (Préstamos + reembolsos) / gasto total del proyecto                                                         | `Gastos`                          | M     | B              |
| P12 | **Cumplimiento de plazo**             | Días transcurridos / plazo, comparado con P1                                                                | `INF-Gral`                        | M     | B              |
| P13 | **Cobertura de gasto precontractual** | Gasto precontractual / monto contratado                                                                     | `Gastos`                          | M     | B              |
| P14 | **Rotación de almacén**               | Utilizado / ingresado por ítem; ítems con stock crítico                                                     | `Almacén`                         | M     | C (sin precio) |

Alcance del valor ganado que se propone: **EV, PV y AC se miden solo para el componente de obra, sin IGV**; el expediente técnico y la supervisión se miden como un proyecto aparte o como un bloque separado. Es el punto a confirmar con el responsable de Proyectos.

## 2. Logística y pagos

| #   | KPI                                             | Fórmula                                                                                                   | Fuente                   | Frec. | Prior.                           |
| --- | ----------------------------------------------- | --------------------------------------------------------------------------------------------------------- | ------------------------ | ----- | -------------------------------- |
| L1  | **Volumen de compras**                          | Suma del total de órdenes (sin rechazadas) por proyecto, empresa y moneda                                 | ORD `Análisis`           | S     | A                                |
| L2  | **% de RQ rechazados**                          | RQ rechazados / RQ totales                                                                                | REQ                      | M     | A                                |
| L3  | **% de RQ de emergencia y regularización**      | (Emergencia + regularización) / RQ totales. Hoy 85 %                                                      | REQ                      | M     | A                                |
| L4  | **% de órdenes sin RQ** (regularización)        | Órdenes de regularización / órdenes totales. Hoy 17 % de las filas                                        | ORD                      | M     | A                                |
| L5  | **Tiempo de aprobación de RQ**                  | Fecha de aprobación − fecha de creación (promedio y percentil 90). Hoy 1.1 días                           | REQ                      | S     | A                                |
| L6  | **Tiempo RQ aprobado → orden emitida**          | Fecha de emisión − aprobación del RQ. Hoy 1.6 días                                                        | ORD                      | S     | A                                |
| L7  | **Tiempo orden aprobada → factura recibida**    | Fecha de comprobante − aprobación de la orden                                                             | ORD `Facturas`           | M     | B                                |
| L8  | **Órdenes aprobadas sin facturar**              | Cantidad e importe de órdenes en estado "Aprobada (sin facturar)". Hoy 70                                 | ORD                      | S     | A                                |
| L9  | **Órdenes pendientes de entrega**               | Cantidad e importe. Hoy 180 de 312 con estado de entrega                                                  | ORD                      | S     | A                                |
| L10 | **Cuentas por pagar**                           | Suma de comprobantes no pagados, por moneda                                                               | `Facturas`, Finanzas     | S     | A                                |
| L11 | **Deuda vencida**                               | Comprobantes no pagados con vencimiento anterior a hoy / total por pagar. Hoy 144 de 200                  | `Facturas`               | S     | A                                |
| L12 | **Antigüedad de la deuda**                      | Tramos: 0-7, 8-15, 16-30, más de 30 días                                                                  | `Facturas`               | S     | A                                |
| L13 | **Calendario de pagos**                         | Pagos programados por fecha                                                                               | Finanzas                 | S     | A                                |
| L14 | **Diferencia orden vs. factura**                | Diferencia absoluta entre total facturado y total de la orden, por orden. Hoy 43 de 279 órdenes           | ORD                      | M     | A                                |
| L15 | **Diferencia factura vs. contabilidad**         | Diferencia absoluta entre el total en Facturas y el total en Contabilidad, por comprobante. Hoy 35 de 281 | `Facturas`, Contabilidad | M     | A                                |
| L16 | **Concentración de proveedores**                | % de compras de los 10 primeros proveedores                                                               | ORD                      | M     | B                                |
| L17 | **Pagos por detracción y retención pendientes** | Importe en estado "Por detracción/retención"                                                              | Tesorería                | S     | B                                |
| L18 | **Comprobantes por validar**                    | Cantidad en estado "Pendiente de validación" o "Observada"                                                | `Facturas`, Contabilidad | S     | A                                |
| L19 | **Compra por tipo de condición de pago**        | % contado / crédito / anticipo                                                                            | ORD                      | M     | B                                |
| L20 | **Ahorro** (precio pagado vs. precio del RQ)    | (Precio RQ − precio orden) / precio RQ                                                                    | REQ, ORD                 | M     | C (precio solo en 19 % de ítems) |

## 3. Préstamos y deuda

| #   | KPI                                      | Fórmula                                                                           | Fuente                         | Frec. | Prior.                             |
| --- | ---------------------------------------- | --------------------------------------------------------------------------------- | ------------------------------ | ----- | ---------------------------------- |
| F1  | **Deuda total vigente**                  | Capital por pagar (S/ equivalente con TC del día)                                 | `BD_CUOTAS`                    | M     | A                                  |
| F2  | **Servicio de deuda del mes**            | Suma de cuotas (capital + interés + otros) del mes                                | `BD_CUOTAS`                    | S     | A                                  |
| F3  | **Vencimientos a 30, 60 y 90 días**      | Cuotas por fecha de vencimiento                                                   | `BD_CUOTAS`                    | S     | A                                  |
| F4  | **Costo financiero total y realizado**   | Interés + otros / total; % realizado. Hoy 3.72 M y 55 %                           | `BD_CUOTAS`                    | M     | A                                  |
| F5  | **Costo financiero promedio ponderado**  | Intereses anuales / capital promedio vigente                                      | `BD_CUOTAS`                    | M     | B                                  |
| F6  | **Concentración por acreedor**           | % del capital por pagar en los tres mayores acreedores                            | `BD_CUOTAS`                    | M     | A                                  |
| F7  | **Concentración por mes**                | Mayor mes de vencimiento / total por pagar. Hoy dic-26 ≈ 52 % del total por pagar | `BD_CUOTAS`                    | M     | A                                  |
| F8  | **Mora y cuotas vencidas no pagadas**    | Cuotas con vencimiento pasado y sin pago real                                     | `Pago real`                    | S     | A (requiere registro real de pago) |
| F9  | **Deuda por empresa deudora**            | Capital por empresa                                                               | `BD_CUOTAS`                    | M     | A                                  |
| F10 | **Deuda corporativa vs. personal**       | Capital de deuda de la empresa / capital personal del gerente                     | `BD_CUOTAS`                    | M     | B                                  |
| F11 | **Mix por tipo**                         | Banco / caja / inversionistas / pagarés, y % en dólares                           | `BD_CUOTAS`                    | M     | B                                  |
| F12 | **Cobertura de servicio de deuda**       | Ingresos de caja del mes / servicio de deuda del mes                              | Valorizaciones cobradas, F2    | M     | C (sin ingresos de caja)           |
| F13 | **Costo financiero imputado a proyecto** | Costo financiero de préstamos cuyo destino es el proyecto                         | Cuotas con proyecto financiado | M     | C                                  |

## 4. Recursos humanos

| #   | KPI                                        | Fórmula                                                           | Fuente                  | Frec. | Prior.               |
| --- | ------------------------------------------ | ----------------------------------------------------------------- | ----------------------- | ----- | -------------------- |
| H1  | **Dotación**                               | Personas activas por empresa, proyecto, categoría y condición     | `MAESTRO`               | M     | A                    |
| H2  | **Costo bruto de personal**                | Suma del sueldo bruto del mes, por proyecto, categoría y empresa  | Formato por proyecto    | M     | A                    |
| H3  | **Costo promedio por persona y categoría** | H2 / H1                                                           | Formato por proyecto    | M     | B                    |
| H4  | **% planilla vs. honorarios**              | Personas y costo por condición                                    | `MAESTRO`, formato      | M     | A                    |
| H5  | **Costo de personal / valorización**       | H2 / valorización del mes del proyecto                            | Formato, valorizaciones | M     | A                    |
| H6  | **Tardanzas y faltas**                     | Minutos de tardanza y días sin marcación por persona y proyecto   | Marcaciones             | S     | A                    |
| H7  | **Asistencia**                             | Días con marcación / días hábiles                                 | Marcaciones             | S     | B                    |
| H8  | **Contratos por firmar y por vencer**      | Observación "ELABORAR CONTRATO"; fin de contrato < 30 días        | `MAESTRO`               | S     | A                    |
| H9  | **Rotación**                               | Bajas del periodo / dotación promedio                             | `MAESTRO` con histórico | M     | C (no hay histórico) |
| H10 | **Cumplimiento del calendario**            | Obligaciones entregadas a tiempo (AFP día 25, SCTR día 28, PLAME) | Registro de entrega     | M     | B                    |
| H11 | **Recibos por honorarios pendientes**      | Personas con "Recibo emitido = NO"                                | `HONORARIOS`            | M     | A                    |
| H12 | **Coherencia de costo**                    | Costo de personal del formato vs. gasto "RRHH" en `Gastos`        | Formato, `Gastos`       | M     | B                    |
| H13 | **Estructura de edad**                     | Edad promedio y distribución                                      | `MAESTRO`               | M     | C                    |

## 5. Calidad de datos (KPI transversales)

| #   | KPI                         | Fórmula                                                                                             |
| --- | --------------------------- | --------------------------------------------------------------------------------------------------- |
| Q1  | **Entrega oportuna**        | Archivos recibidos a tiempo / archivos esperados por oficina                                        |
| Q2  | **Errores de carga**        | Filas rechazadas por las reglas de validación / filas cargadas                                      |
| Q3  | **Cobertura de llaves**     | % de gastos con N.º de orden; % de comprobantes con código de proyecto; % de ítems de RQ con precio |
| Q4  | **Diferencias entre áreas** | Casos de L14, L15, H12                                                                              |

## 6. Resumen gerencial sugerido

Los diez indicadores que van en la pantalla inicial:

1. Avance valorizado y SPI de la cartera (P1, P3).
2. CPI y margen esperado por proyecto (P5, P6).
3. Gasto comprometido y pendiente de pago (P9, L8).
4. Cuentas por pagar y deuda vencida (L10, L11).
5. Pagos programados en los próximos 30 días (L13, F2).
6. Deuda financiera total y concentración (F1, F6).
7. Vencimientos de deuda a 90 días (F3).
8. Costo de personal por proyecto (H2, H5).
9. Contratos y obligaciones por vencer (H8, H10).
10. Calidad de datos (Q1 a Q4).

## 7. Reglas comunes de cálculo

- **IGV:** los indicadores de costo y de avance se calculan **sin IGV**; los de caja y deuda, **con IGV**.
- **Moneda:** equivalente en soles con tipo de cambio de la fecha del movimiento; para saldos, el del cierre. Mostrar siempre el total por moneda original.
- **Estado de pago:** se usa el pago real (fecha y operación), nunca la fecha actual como sustituto.
- **Duplicados:** órdenes y RQ se cuentan por documento y no por ítem.
- **Real vs. proyectado:** nunca se suman; se muestran como series separadas.
