# 07. Archivos limpios de entrega por oficina

Propuesta de los archivos que cada oficina entregaría al cuadro de mando. Objetivos:

- **Fáciles de producir** a partir de los archivos actuales (copiar columnas, no reescribir).
- **Sin retrabajo:** cada dato se captura una sola vez y en el lugar donde ya se captura hoy.
- **Consistentes:** mismos nombres de campo, mismos códigos y mismo formato en todas las oficinas.

## 1. Convenciones generales (valen para todos los archivos)

| Tema        | Regla                                                                                                                                                              |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Formato     | `.xlsx` o `.csv` UTF-8. **Una hoja de datos por archivo**, encabezado en la **fila 1**, sin celdas combinadas, sin filas de título, sin totales dentro de la tabla |
| Nombre      | `AAAA-MM-DD_oficina_tabla.xlsx` (fecha de corte primero). Ejemplo: `2026-11-30_logistica_ordenes.xlsx`                                                             |
| Fechas      | Celdas de fecha reales, o texto `AAAA-MM-DD`. Nunca texto libre                                                                                                    |
| Importes    | Número con dos decimales, **sin símbolo de moneda ni separador de miles**. Una columna `moneda` (`PEN` / `USD`)                                                    |
| Códigos     | Texto: el DNI con 8 dígitos y ceros a la izquierda, el RUC con 11 dígitos, el CC2 con 3 dígitos (`017`)                                                            |
| Valores     | Se usan **catálogos cerrados** (lista de valores permitidos). Sin variantes de escritura                                                                           |
| Fórmulas    | Los datos de entrega son **valores**. Las fórmulas se quedan en el archivo de trabajo                                                                              |
| Sensibles   | Cuentas, CCI y datos familiares **no** viajan en los archivos del cuadro de mando salvo que Tesorería lo pida expresamente y por un canal propio                   |
| Responsable | Cada archivo tiene un responsable y una fecha límite de entrega                                                                                                    |
| Versión     | Cada entrega agrega la fecha de corte; nunca se sobrescribe un archivo anterior                                                                                    |

## 2. Catálogos maestros (se definen una sola vez)

| Catálogo           | Responsable                | Campos                                                                                                                                          | Cómo se obtiene                                                                                   |
| ------------------ | -------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| `cat_empresa`      | Contabilidad               | `ruc`, `razon_social`, `nombre_corto`, `prefijo_documentos`                                                                                     | De los reportes de Contabilidad y los prefijos de órdenes (DPH, DPHC, CSD, CSJ, PS, DPC)          |
| `cat_centro_costo` | Proyectos                  | `cc2` (3 dígitos), `nombre_corto`, `tipo` (área / general de sede / proyecto), `cui_o_codigo`, `entidad`, `fecha_inicio`, `fecha_fin`, `estado` | De la lista de CC2 que ya usa Contabilidad (≈ 39 códigos) y de la ficha del proyecto (`INF-Gral`) |
| `cat_categoria`    | Proyectos                  | `codigo`, `componente`, `item`, `nivel`, `etapa`, `tipo_costo`, `categoria_especial`                                                            | Directamente de `categorias_global`                                                               |
| `cat_partida_cc1`  | Contabilidad               | `cc1`, `nombre`, `cc2_aplicable`                                                                                                                | De la lista de CC1 que ya usa Contabilidad (35 códigos)                                           |
| `cat_estado`       | Equipo del cuadro de mando | Equivalencias de estado entre Facturas, Contabilidad, Finanzas y Tesorería                                                                      | Se arma una vez a partir de los estados actuales                                                  |
| `cat_tc`           | Tesorería                  | `fecha`, `tc_compra`, `tc_venta`                                                                                                                | Tabla diaria; hoy hay 3.5 y 3.45 fijos                                                            |

Con estos seis catálogos se evita la mayor parte de las inconsistencias detectadas (nombres de proyecto, estados, condiciones de pago, tipo de cambio).

## 3. Proyectos (administración de cada proyecto)

Se entregan **tres tablas por proyecto** (se pueden mantener en el mismo libro con tres hojas, o en tres archivos).

### 3.1 `proyectos_gastos` (fuente: hoja `Gastos`)

| Campo              | Tipo   | Oblig. | Origen en el archivo actual                               | Regla                                           |
| ------------------ | ------ | ------ | --------------------------------------------------------- | ----------------------------------------------- |
| `id_gasto`         | texto  | Sí     | Nuevo: `cc2` + correlativo                                | Único                                           |
| `cc2`              | texto  | Sí     | Nuevo (hoy el archivo es de un solo proyecto)             | Debe estar en `cat_centro_costo`                |
| `codigo_categoria` | texto  | Sí     | `CÓDIGO`                                                  | Debe estar en `cat_categoria`                   |
| `fecha`            | fecha  | Sí     | `FECHA DE PAGO`                                           |                                                 |
| `fecha_pago_real`  | fecha  | No     | `PAGO REAL`                                               | Obligatoria si `estado` = `PAGADO`              |
| `estado`           | lista  | Sí     | `ESTADO`                                                  | `PAGADO`, `PENDIENTE`                           |
| `naturaleza`       | lista  | Sí     | `OBS` ("GASTO PROYECTADO" → `PROYECTADO`; si no → `REAL`) | `REAL`, `PROYECTADO`                            |
| `proveedor_ruc`    | texto  | No     | Nuevo (hoy solo nombre)                                   | RUC válido                                      |
| `proveedor`        | texto  | Sí     | `PROVEEDOR`                                               |                                                 |
| `concepto`         | texto  | Sí     | `CONCEPTO`                                                |                                                 |
| `moneda`           | lista  | Sí     | Derivada de `SOLES` / `DOLARES`                           | `PEN`, `USD`                                    |
| `monto`            | número | Sí     | `SOLES` o `DOLARES`                                       | Un solo importe, no dos columnas                |
| `con_igv`          | lista  | Sí     | Nuevo                                                     | `SI`, `NO`                                      |
| `nro_orden`        | texto  | No     | Nuevo (`RQ` hoy vacío)                                    | Si la compra pasó por Logística, es obligatorio |
| `id_comprobante`   | texto  | No     | `ID ADM` / `ID TESO` / `ID FNZS`                          | `RUC + serie-número`                            |
| `tipo_gasto`       | lista  | Sí     | Nuevo                                                     | `OPERATIVO`, `PRESTAMO`, `REEMBOLSO`, `RRHH`    |

Esfuerzo de producción: **una vez**, se agregan cuatro columnas (`cc2`, `naturaleza`, `con_igv`, `tipo_gasto`); el resto sale de lo que ya existe. No se vuelve a escribir el monto en soles (lo calcula el sistema).

### 3.2 `proyectos_presupuesto` (fuente: `EO-PPTOs`)

`cc2`, `escenario` (`CONTRATO`, `META`, `PROPUESTO`), `codigo_partida`, `descripcion`, `unidad`, `metrado`, `precio_unitario`, `parcial`, más los **parámetros** en una tabla aparte (`escenario`, `gg_pct`, `utilidad_pct`, `igv_pct`, `factor_meta`) para que los 13 %, 10 %, 18 % y 0.7 no vivan dentro de fórmulas. Se produce copiando las columnas de partidas (sin la fila de totales).

### 3.3 `proyectos_valorizacion` (fuente: `Valorizaciones`, `Resumen-Valorizaciones`)

`cc2`, `periodo` (AAAA-MM), `escenario_plan` (`CONTRATO`, `META`, `PROPUESTO`), `monto_planificado`, `monto_real`, `estado_cobro`, `fecha_cobro`. Hoy el cronograma contractual mensual está escrito a mano; en este formato se entrega **una fila por mes**.

### 3.4 `proyectos_ficha` (fuente: `INF-Gral`, bloque de datos)

Una fila por proyecto: `cc2`, `nombre`, `cui`, `codigo`, `entidad`, `ubicacion`, `fecha_acta_et`, `plazo_et`, `fecha_acta_eo`, `plazo_eo`, `monto_contrato`, `fecha_corte`. Sustituye la fecha de corte manual de `INF-Gral!F16` por un campo explícito.

## 4. Logística

Los archivos ya son **exportaciones de sistema**, es decir, ya son tablas. Solo se piden **ajustes en el origen**:

| Archivo        | Ajuste                                                                                                                                                                    |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Requerimientos | Código `cc2` (3 dígitos) en lugar de texto largo; precio en todos los ítems o columna `precio_estimado` aparte                                                            |
| Órdenes        | Un `cc2` por orden (si hay varios, líneas separadas); condición de pago de un catálogo; `proyecto` desde `cat_centro_costo`; `rq_origen` o `REGULARIZACION` sin variantes |
| Facturas       | `ruc_proveedor` + `serie_numero` (separados); `fecha_pago` obligatoria si `estado` = pagada                                                                               |
| Todos          | Fechas reales (la de 2024 se corrige en origen); sin observaciones con cuentas ni DNI                                                                                     |

## 5. Contabilidad, Finanzas y Tesorería

Hoy son tres exportaciones de la **misma tabla** con columnas acumuladas. Propuesta: **una sola tabla** `compras_comprobantes` con una fila por comprobante y la siguiente estructura:

| Grupo        | Campos                                                                                                                                       |
| ------------ | -------------------------------------------------------------------------------------------------------------------------------------------- |
| Documento    | `ruc_empresa`, `ruc_proveedor`, `tipo_doc`, `serie_numero`, `fecha_doc`, `fecha_venc`, `moneda`, `tc`                                        |
| Importes     | `base_imponible`, `igv`, `no_gravado`, `total`, `total_soles`, `detraccion_pct`, `detraccion_monto`, `retencion_monto`, `retencion_garantia` |
| Orden        | `nro_orden`                                                                                                                                  |
| Imputación   | `cc1`, `cc2` (códigos, sin nombres repetidos)                                                                                                |
| Contabilidad | `fecha_registro`, `estado_conformidad`                                                                                                       |
| Finanzas     | `fecha_programacion`, `fecha_pago_programada`, `cuotas`                                                                                      |
| Tesorería    | `fecha_pago_real`, `nro_operacion`, `nro_operacion_detraccion`, `nro_operacion_retencion`, `monto_neto_pagado`                               |
| Estado       | `estado_pago` (catálogo único)                                                                                                               |

Se **eliminan** las columnas redundantes (`RUC`, `R.Social`, `Tipo`, `Tip.Doc.Iden`, nombres de CC repetidos, `MONTO OS/OC` repetido por comprobante). Banco, cuenta y CCI **no** van; si se necesitan para pagos, viajan por otro canal.

Cada oficina llena **solo sus campos** sobre la misma tabla: Contabilidad registra el comprobante; Finanzas añade la programación; Tesorería añade el pago. No se copian entre archivos.

## 6. Préstamos

Se reemplazan las 30 hojas de detalle por **dos tablas** y una tercera nueva:

### 6.1 `prestamos_catalogo` (fuente: `RPT_MAPA` y cabeceras de cada hoja)

`id_prestamo`, `deudor` (empresa o `PERSONAL`), `acreedor`, `tipo` (`BANCO`, `CAJA`, `INVERSIONISTA`, `PAGARE`, `TARJETA`), `moneda`, `capital`, `fecha_desembolso`, `tasa` y `tipo_tasa` (`TEA` / `TNA`), `sistema` (`FRANCES` / `BULLET` / `OTRO`), `n_cuotas`, `comision`, `cc2_financiado` (si aplica), `activo` (`SI` / `NO`).

### 6.2 `prestamos_cuotas` (fuente: `BD_CUOTAS`, o cada hoja de detalle)

`id_prestamo`, `n_cuota`, `fecha_vencimiento`, `saldo_inicial`, `interes`, `capital`, `otros_costos`, `total_cuota`. **Una fila por cuota.** Se obtiene copiando las tablas de cada hoja de detalle (las columnas ya existen con nombres distintos). Esta tabla reemplaza los 33,900 cálculos del motor.

### 6.3 `prestamos_pagos` (nuevo)

`id_prestamo`, `n_cuota`, `fecha_pago`, `monto_pagado`, `moneda`, `nro_operacion`, `observacion`. Permite pasar de "se asume que pagó" a "se pagó". Tesorería ya tiene esta información en sus reportes; se obtiene de allí.

## 7. Recursos humanos

### 7.1 `rrhh_personal` (fuente: `MAESTRO 2026.xlsx`)

| Campo                                                                                | Origen                                                      |
| ------------------------------------------------------------------------------------ | ----------------------------------------------------------- |
| `dni` (8 dígitos), `apellidos_nombres`*                                              | `MAESTRO`                                                   |
| `empresa_ruc`                                                                        | `Empresa` → catálogo                                        |
| `cc2`                                                                                | `PROYECTO` → catálogo                                       |
| `area`, `cargo`, `categoria` (`CLAVE`, `NO CLAVE`, `ADMINISTRATIVO`, `MANO DE OBRA`) | `AREA`, `Cargo` y clasificación de la planilla por proyecto |
| `condicion` (`PLANILLA`, `RXH`)                                                      | `MODALIDAD`                                                 |
| `fecha_ingreso`, `fecha_fin_contrato`, `estado_contrato` (`FIRMADO`, `ELABORAR`)     | `MAESTRO`                                                   |
| `sueldo_base`, `asignacion_familiar`                                                 | `MAESTRO`                                                   |
| `sistema_pension` (`AFP` / `ONP`), `afp`                                             | `MAESTRO`                                                   |
| `sede`                                                                               | `MAESTRO`                                                   |
| `vigente_desde`, `vigente_hasta`                                                     | Nuevo (histórico)                                           |

*Se mantiene solo en el sistema de gestión; el cuadro de mando usa el DNI seudonimizado.

No viajan: cuenta, CCI, correos, teléfono, familiares. Se mantienen en el archivo operativo de RR. HH.

### 7.2 `rrhh_costo_proyecto` (fuente: formato de planilla por proyecto)

`periodo`, `empresa_ruc`, `cc2`, `dni`, `categoria`, `condicion`, `fecha_inicio`, `dias_laborados`, `sueldo_base_acordado`, `sueldo_bruto`, `observacion`. Una fila por persona y mes (no cuatro bloques). El archivo actual se puede convertir a esta tabla pegando los cuatro bloques uno debajo del otro y agregando la columna `categoria`. Los resúmenes por categoría y condición los calcula el sistema.

### 7.3 `rrhh_planilla` (fuente: `PLANILLA` y `HONORARIOS`)

`periodo`, `dni`, `condicion`, `dias_trabajados`, `remuneracion_bruta`, `descuentos_total`, `aporte_pension`, `essalud`, `neto_pagar`, `recibo_emitido` (solo RxH). Es el resumen de los cálculos; el detalle de las 64 columnas sigue en el archivo de trabajo de RR. HH.

### 7.4 `rrhh_marcaciones` (fuente: archivo del reloj)

`codigo_reloj`, `fecha_hora`. Más una tabla de equivalencia `codigo_reloj` ↔ `dni`. Se entrega tal cual sale del reloj; el sistema depura duplicados y líneas mal formadas.

### 7.5 `rrhh_obligaciones` (fuente: `rrhh.mmd`)

`periodo`, `obligacion` (`AFP`, `SCTR`, `VIDA_LEY`, `PLAME`), `fecha_limite`, `fecha_entrega`, `responsable`. Cuatro filas por mes; permite medir el cumplimiento del calendario.

## 8. Resumen: lo que cada oficina entrega

| Oficina                             | Archivos                                                                                                     | Frecuencia                    | Esfuerzo nuevo frente a hoy                                                 |
| ----------------------------------- | ------------------------------------------------------------------------------------------------------------ | ----------------------------- | --------------------------------------------------------------------------- |
| Proyectos (administradores)         | `proyectos_gastos`, `proyectos_valorizacion`, `proyectos_presupuesto` (una vez), `proyectos_ficha` (una vez) | Semanal / mensual             | Bajo: 4 columnas y una fila por mes                                         |
| RR. HH.                             | `rrhh_personal`, `rrhh_costo_proyecto`, `rrhh_planilla`, `rrhh_marcaciones`, `rrhh_obligaciones`             | Mensual (marcaciones semanal) | Bajo: reordenar columnas, categoría y código de proyecto                    |
| Logística                           | Requerimientos, órdenes, facturas                                                                            | Semanal                       | Mínimo: ya son exportaciones                                                |
| Contabilidad / Finanzas / Tesorería | `compras_comprobantes`                                                                                       | Semanal                       | Medio: unificar en una tabla y llenar solo los campos propios               |
| Préstamos                           | `prestamos_catalogo`, `prestamos_cuotas`, `prestamos_pagos`                                                  | Mensual (pagos semanal)       | Medio: convertir las hojas a tabla larga; el pago real lo toma de Tesorería |
| Transversal                         | `cat_empresa`, `cat_centro_costo`, `cat_categoria`, `cat_partida_cc1`, `cat_estado`, `cat_tc`                | Una vez y actualización       | Medio la primera vez, luego casi nulo                                       |

## 9. Validaciones al cargar

Cada archivo pasa por reglas automáticas antes de entrar al cuadro de mando; los errores se devuelven a la oficina con el número de fila:

- Código de proyecto, categoría, empresa y partida existen en su catálogo.
- Llaves únicas (`id_gasto`, `RUC + serie-número`, `id_prestamo + n_cuota`).
- Importes numéricos; fechas reales y razonables (la de 2024 en un archivo de 2026 se marca).
- Estados dentro del catálogo.
- Totales de control: cantidad de filas e importe total declarado por la oficina coinciden con lo cargado.
- Reglas de [05_arbol_y_modelo_datos.md](05_arbol_y_modelo_datos.md), sección 4.
