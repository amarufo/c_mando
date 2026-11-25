# Diccionario de KPI

Documento **generado automáticamente** con `python manage.py generar_diccionario_kpi` desde el registro de KPI (`apps/*/kpis.py`). No se edita a mano: para cambiar una definición se cambia el código y se vuelve a generar.

Semáforo: **ok** si se cumple el umbral de atención, **atención** entre ambos umbrales, **crítico** más allá del umbral crítico. Los umbrales pueden ajustarse en el administrador (Configuración de KPI) sin tocar el código.

## Proyectos

Avance, costo y margen de cada obra (valor ganado).

| Código | Indicador                            | Unidad | Mejor       | Atención | Crítico | Frec. | Prior. |
| ------ | ------------------------------------ | ------ | ----------- | -------- | ------- | ----- | ------ |
| P1     | Avance valorizado                    | %      | informativo | —        | —       | M     | A      |
| P2     | Avance planificado                   | %      | informativo | —        | —       | M     | A      |
| P3     | SPI (cronograma)                     | índice | más alto    | 0.9      | 0.75    | M     | A      |
| P4     | Costo real de obra (AC)              | S/     | informativo | —        | —       | M     | A      |
| P5     | CPI (costo)                          | índice | más alto    | 0.95     | 0.85    | M     | A      |
| P6     | Margen esperado al cierre            | %      | más alto    | 20       | 10      | M     | A      |
| P7     | Desviación frente a la meta de costo | %      | más bajo    | 5        | 15      | M     | A      |
| P8     | Gasto pagado total                   | S/     | informativo | —        | —       | S     | A      |
| P9     | Pendiente de pago                    | S/     | informativo | —        | —       | S     | A      |
| P10    | Flujo neto acumulado                 | S/     | más alto    | 0        | -500000 | M     | B      |
| P11    | Costos no operativos                 | %      | más bajo    | 5        | 10      | M     | B      |
| P12    | Brecha plazo vs avance               | %      | más bajo    | 5        | 15      | M     | B      |
| P13    | Gasto precontractual / contrato      | %      | más bajo    | 8        | 12      | M     | B      |

### P1 · Avance valorizado

- **Fórmula:** Valorización real acumulada / monto contratado (meses cerrados)
- **Fuente:** Valorizacion.monto_real

### P2 · Avance planificado

- **Fórmula:** Valorización planificada acumulada / monto contratado (meses cerrados)
- **Fuente:** Valorizacion.monto_planificado

### P3 · SPI (cronograma)

- **Fórmula:** EV / PV = avance real / avance planificado
  - Fórmulas:
    - EV = avance real x BAC de costo (meta 70 %, sin IGV)
    - Avance real: valorización real acumulada / monto contratado (meses cerrados)
- **Fuente:** Valorizacion
- **Lectura:** Mayor o igual a 1: la obra va a tiempo o adelantada. Menor a 0.75: atraso importante.

### P4 · Costo real de obra (AC)

- **Fórmula:** Gastos reales y pagados de los componentes de obra, sin IGV
- **Fuente:** Gasto
- **Lectura:** Componentes incluidos: 01, 02, 05

### P5 · CPI (costo)

- **Fórmula:** EV / AC. EV = avance real x BAC de costo (meta 70 %, sin IGV)
- **Fuente:** Valorizacion, Gasto, PresupuestoEscenario
- **Lectura:** Mayor a 1: se gasta menos de lo que corresponde al avance logrado.

### P6 · Margen esperado al cierre

- **Fórmula:** (Contrato sin IGV - EAC) / Contrato sin IGV; EAC = BAC / CPI
- **Fuente:** PresupuestoEscenario, Gasto, Valorizacion
- **Lectura:** Proyección del margen de obra si se mantiene el CPI actual. No incluye expediente técnico ni precontractual.

### P7 · Desviación frente a la meta de costo

- **Fórmula:** (AC / EV - 1) x 100
- **Fuente:** Valorizacion, Gasto
- **Lectura:** Cuánto se gastó de más (positivo) o de menos (negativo) respecto al costo meta del avance logrado.

### P8 · Gasto pagado total

- **Fórmula:** Gastos REALES pagados de todos los componentes, sin IGV
- **Fuente:** Gasto

### P9 · Pendiente de pago

- **Fórmula:** Gastos REALES en estado PENDIENTE (los proyectados se muestran aparte)
- **Fuente:** Gasto

### P10 · Flujo neto acumulado

- **Fórmula:** Cobros de valorizaciones - pagos reales (sin IGV)
- **Fuente:** Valorizacion.monto_cobrado, Gasto
- **Lectura:** Negativo: el proyecto se financia con caja de la empresa.

### P11 · Costos no operativos

- **Fórmula:** (Préstamos + reembolsos) / gasto pagado total
- **Fuente:** Gasto.tipo_gasto
- **Lectura:** Pagos de préstamos y reembolsos cargados al proyecto; inflan el costo real.

### P12 · Brecha plazo vs avance

- **Fórmula:** % de plazo de obra transcurrido - % de avance real (puntos porcentuales)
- **Fuente:** Proyecto, Valorizacion
- **Lectura:** Positivo: se consumió más plazo que avance.

### P13 · Gasto precontractual / contrato

- **Fórmula:** Gasto componente 00 / contrato sin IGV
- **Fuente:** Gasto, Proyecto

## Logística y pagos

Compras, tiempos de ciclo y cuentas por pagar.

| Código | Indicador                                             | Unidad   | Mejor       | Atención | Crítico | Frec. | Prior. |
| ------ | ----------------------------------------------------- | -------- | ----------- | -------- | ------- | ----- | ------ |
| L1     | Compras emitidas en el mes                            | S/       | informativo | —        | —       | S     | A      |
| L2     | RQ rechazados                                         | %        | más bajo    | 20       | 30      | M     | A      |
| L3     | RQ de emergencia y regularización                     | %        | más bajo    | 40       | 60      | M     | A      |
| L4     | Órdenes sin RQ (regularización)                       | %        | más bajo    | 10       | 20      | M     | A      |
| L5     | Tiempo de aprobación de RQ                            | días     | más bajo    | 2        | 4       | S     | A      |
| L6     | Tiempo RQ aprobado a orden emitida                    | días     | más bajo    | 2        | 4       | S     | A      |
| L8     | Órdenes aprobadas sin facturar                        | cantidad | informativo | —        | —       | S     | A      |
| L9     | Órdenes pendientes de entrega                         | cantidad | informativo | —        | —       | S     | A      |
| L10    | Cuentas por pagar                                     | S/       | informativo | —        | —       | S     | A      |
| L11    | Deuda vencida                                         | %        | más bajo    | 20       | 40      | S     | A      |
| L12    | Deuda vencida de más de 30 días                       | S/       | más bajo    | 100000   | 500000  | S     | A      |
| L13    | Pagos programados a 30 días                           | S/       | informativo | —        | —       | S     | A      |
| L14    | Órdenes con diferencia vs facturado                   | %        | más bajo    | 10       | 20      | M     | A      |
| L15    | Comprobantes con diferencia Logística vs Contabilidad | %        | más bajo    | 5        | 10      | M     | A      |
| L16    | Concentración en 10 proveedores                       | %        | más bajo    | 60       | 80      | M     | B      |
| L17    | Pagos pendientes por detracción o retención           | S/       | informativo | —        | —       | M     | B      |
| L18    | Comprobantes por validar                              | cantidad | más bajo    | 15       | 30      | S     | A      |

### L1 · Compras emitidas en el mes

- **Fórmula:** Suma del total de órdenes no rechazadas emitidas en el mes del corte
- **Fuente:** Orden.total_pen

### L2 · RQ rechazados

- **Fórmula:** RQ rechazados / RQ creados (90 días)
- **Fuente:** Requerimiento.estado

### L3 · RQ de emergencia y regularización

- **Fórmula:** (Emergencia + regularización) / RQ creados (90 días)
- **Fuente:** Requerimiento.tipo
- **Lectura:** Indica qué parte de las compras no se planifica. En el archivo de octubre-noviembre llegaba al 85 %.

### L4 · Órdenes sin RQ (regularización)

- **Fórmula:** Órdenes de regularización / órdenes emitidas (90 días)
- **Fuente:** Orden.es_regularizacion

### L5 · Tiempo de aprobación de RQ

- **Fórmula:** Promedio de (fecha de aprobación - fecha de creación)
- **Fuente:** Requerimiento

### L6 · Tiempo RQ aprobado a orden emitida

- **Fórmula:** Promedio de (fecha de emisión - aprobación del RQ)
- **Fuente:** Orden

### L8 · Órdenes aprobadas sin facturar

- **Fórmula:** Cantidad de órdenes en estado 'Aprobada (sin facturar)'
- **Fuente:** Orden.estado

### L9 · Órdenes pendientes de entrega

- **Fórmula:** Órdenes aprobadas con entrega pendiente o parcial
- **Fuente:** Orden.estado_entrega

### L10 · Cuentas por pagar

- **Fórmula:** Suma de comprobantes no pagados
- **Fuente:** Comprobante.total_pen

### L11 · Deuda vencida

- **Fórmula:** Importe vencido no pagado / importe total por pagar
- **Fuente:** Comprobante.fecha_venc
- **Lectura:** Vencido = fecha de vencimiento anterior a la fecha de corte.

### L12 · Deuda vencida de más de 30 días

- **Fórmula:** Comprobantes no pagados con más de 30 días de vencidos
- **Fuente:** Comprobante.fecha_venc

### L13 · Pagos programados a 30 días

- **Fórmula:** Comprobantes programados con fecha de pago entre hoy y +30 días
- **Fuente:** Comprobante.fecha_programada_pago

### L14 · Órdenes con diferencia vs facturado

- **Fórmula:** Órdenes cuyo total facturado difiere más de 1 sol del total de la orden / órdenes con comprobante
- **Fuente:** Orden.total, Comprobante.total
- **Lectura:** Incluye anticipos y facturas parciales: revisar caso a caso.

### L15 · Comprobantes con diferencia Logística vs Contabilidad

- **Fórmula:** Comprobantes con |total Contabilidad - total Logística| > 1 sol / comprobantes con ambos importes
- **Fuente:** Comprobante.total, Comprobante.total_logistica

### L16 · Concentración en 10 proveedores

- **Fórmula:** Compras de los 10 mayores proveedores / compras totales (90 días)
- **Fuente:** Orden.proveedor

### L17 · Pagos pendientes por detracción o retención

- **Fórmula:** Comprobantes en estado 'Por detracción/retención'
- **Fuente:** Comprobante.estado_pago

### L18 · Comprobantes por validar

- **Fórmula:** Comprobantes pendientes de conformidad o en revisión
- **Fuente:** Comprobante.estado_pago

## Préstamos y deuda

Deuda vigente, vencimientos y costo financiero.

| Código | Indicador                         | Unidad | Mejor       | Atención | Crítico | Frec. | Prior. |
| ------ | --------------------------------- | ------ | ----------- | -------- | ------- | ----- | ------ |
| F1     | Deuda vigente (capital por pagar) | S/     | informativo | —        | —       | M     | A      |
| F2     | Servicio de deuda del mes         | S/     | informativo | —        | —       | S     | A      |
| F3     | Vencimientos a 90 días            | S/     | informativo | —        | —       | S     | A      |
| F4     | Costo financiero total            | S/     | informativo | —        | —       | M     | A      |
| F6     | Concentración en 3 acreedores     | %      | más bajo    | 50       | 70      | M     | A      |
| F7     | Concentración en un mes           | %      | más bajo    | 30       | 45      | M     | A      |
| F8     | Cuotas vencidas sin pago          | S/     | más bajo    | 0        | 100000  | S     | A      |
| F10    | Deuda personal del gerente        | %      | más bajo    | 5        | 15      | M     | B      |
| F11    | Deuda en dólares                  | %      | informativo | —        | —       | M     | B      |

### F1 · Deuda vigente (capital por pagar)

- **Fórmula:** Suma del capital de las cuotas no pagadas
- **Fuente:** Cuota.capital, PagoCuota
- **Lectura:** Equivalente en soles; los préstamos en dólares usan el TC vigente al corte.

### F2 · Servicio de deuda del mes

- **Fórmula:** Cuotas (capital + interés + otros) con vencimiento en el mes del corte
- **Fuente:** Cuota.total_cuota

### F3 · Vencimientos a 90 días

- **Fórmula:** Cuotas no pagadas con vencimiento entre el corte y +90 días
- **Fuente:** Cuota

### F4 · Costo financiero total

- **Fórmula:** Intereses + otros costos de todas las cuotas programadas
- **Fuente:** Cuota.interes, Cuota.otros_costos

### F6 · Concentración en 3 acreedores

- **Fórmula:** Capital por pagar de los 3 mayores acreedores / capital por pagar total
- **Fuente:** Cuota, Prestamo.acreedor

### F7 · Concentración en un mes

- **Fórmula:** Mayor vencimiento mensual / total por pagar
- **Fuente:** Cuota.fecha_vencimiento
- **Lectura:** Un valor alto indica riesgo de caja en un mes puntual.

### F8 · Cuotas vencidas sin pago

- **Fórmula:** Cuotas con vencimiento anterior al corte y sin pago registrado
- **Fuente:** Cuota, PagoCuota
- **Lectura:** Requiere el registro real de pagos (tabla PagoCuota). El archivo actual la reemplaza por TODAY().

### F10 · Deuda personal del gerente

- **Fórmula:** Capital por pagar personal / capital por pagar total
- **Fuente:** Prestamo.es_personal
- **Lectura:** Pregunta G-03 pendiente: ¿se muestra junto a la deuda de las empresas?

### F11 · Deuda en dólares

- **Fórmula:** Capital por pagar en US$ (en soles) / capital por pagar total
- **Fuente:** Prestamo.moneda

## Recursos humanos

Dotación, costo de personal, asistencia y obligaciones.

| Código | Indicador                                       | Unidad   | Mejor       | Atención | Crítico | Frec. | Prior. |
| ------ | ----------------------------------------------- | -------- | ----------- | -------- | ------- | ----- | ------ |
| H1     | Dotación activa                                 | cantidad | informativo | —        | —       | M     | A      |
| H2     | Costo bruto de personal del mes                 | S/       | informativo | —        | —       | M     | A      |
| H3     | Costo promedio por persona                      | S/       | informativo | —        | —       | M     | B      |
| H4     | Personal bajo recibo por honorarios             | %        | informativo | —        | —       | M     | A      |
| H5     | Costo de personal / valorización                | %        | más bajo    | 25       | 35      | M     | A      |
| H6     | Tardanzas                                       | %        | más bajo    | 10       | 20      | S     | A      |
| H8     | Contratos por firmar o por vencer               | cantidad | más bajo    | 3        | 8       | S     | A      |
| H10    | Cumplimiento de obligaciones (AFP, SCTR, PLAME) | %        | más alto    | 95       | 80      | M     | B      |
| H11    | Recibos por honorarios pendientes               | cantidad | más bajo    | 2        | 6       | S     | A      |

### H1 · Dotación activa

- **Fórmula:** Personas con contrato vigente a la fecha de corte
- **Fuente:** Persona

### H2 · Costo bruto de personal del mes

- **Fórmula:** Suma del sueldo bruto del último mes cargado, por proyecto y categoría
- **Fuente:** CostoProyectoMes.sueldo_bruto
- **Lectura:** Es costo bruto: no incluye cargas sociales ni provisiones (pregunta H-10 pendiente).

### H3 · Costo promedio por persona

- **Fórmula:** Costo bruto del mes / personas con costo en el mes
- **Fuente:** CostoProyectoMes

### H4 · Personal bajo recibo por honorarios

- **Fórmula:** Personas RxH / dotación activa
- **Fuente:** Persona.condicion

### H5 · Costo de personal / valorización

- **Fórmula:** Costo bruto de personal del mes / valorización real del mismo mes (sin IGV)
- **Fuente:** CostoProyectoMes, Valorizacion
- **Lectura:** Cruza RR. HH. con Proyectos mediante el código de centro de costo.

### H6 · Tardanzas

- **Fórmula:** Días-persona con tardanza / días-persona con marcación (últimos 15 días)
- **Fuente:** Marcacion
- **Lectura:** Entrada 08:00 con 10 minutos de tolerancia (supuesto; pregunta H-06).

### H8 · Contratos por firmar o por vencer

- **Fórmula:** Contratos 'por elaborar' + contratos que vencen en los próximos 30 días
- **Fuente:** Persona.estado_contrato, fecha_fin_contrato

### H10 · Cumplimiento de obligaciones (AFP, SCTR, PLAME)

- **Fórmula:** Obligaciones entregadas a tiempo / obligaciones con fecha límite cumplida (6 meses)
- **Fuente:** Obligacion
- **Lectura:** Fechas límite: AFP día 25, SCTR y seguro de vida día 28; PLAME por confirmar.

### H11 · Recibos por honorarios pendientes

- **Fórmula:** Personas RxH del último periodo con 'recibo emitido = NO'
- **Fuente:** PlanillaMes.recibo_emitido
- **Lectura:** Si no entregan el recibo no se les paga.

## Calidad de datos

Qué se cargó, cuándo y qué tan completo está.

| Código | Indicador                            | Unidad | Mejor    | Atención | Crítico | Frec. | Prior. |
| ------ | ------------------------------------ | ------ | -------- | -------- | ------- | ----- | ------ |
| Q1     | Días desde la última carga           | días   | más bajo | 7        | 14      | S     | A      |
| Q2     | Cargas rechazadas (30 días)          | %      | más bajo | 10       | 25      | M     | A      |
| Q3     | Gastos de proyecto con N.º de orden  | %      | más alto | 80       | 50      | M     | A      |
| Q4     | RQ con precio estimado               | %      | más alto | 70       | 40      | M     | A      |
| Q5     | Marcaciones sin persona identificada | %      | más bajo | 2        | 10      | M     | A      |

### Q1 · Días desde la última carga

- **Fórmula:** Días entre hoy y la carga aceptada más reciente
- **Fuente:** CargaArchivo
- **Lectura:** Si nadie carga datos, el cuadro de mando muestra información vieja sin avisar.

### Q2 · Cargas rechazadas (30 días)

- **Fórmula:** Cargas rechazadas por errores de validación / cargas intentadas
- **Fuente:** CargaArchivo.estado

### Q3 · Gastos de proyecto con N.º de orden

- **Fórmula:** Gastos operativos con nro_orden / gastos operativos
- **Fuente:** Gasto.nro_orden
- **Lectura:** Mide el vínculo Proyectos-Logística; en el libro actual la columna RQ está vacía.

### Q4 · RQ con precio estimado

- **Fórmula:** Ítems de RQ con precio / ítems de RQ (90 días)
- **Fuente:** Requerimiento.n_items_con_precio
- **Lectura:** Sin precio en el RQ no se puede medir ahorro (L20). En el archivo actual solo el 19 % tenía precio.

### Q5 · Marcaciones sin persona identificada

- **Fórmula:** Marcaciones cuyo código del reloj no coincide con ninguna persona / marcaciones totales
- **Fuente:** Marcacion.persona
- **Lectura:** Mide el cruce código del reloj - DNI (pregunta H-05).
