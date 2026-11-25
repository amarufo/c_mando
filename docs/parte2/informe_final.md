# Informe final: cuadro de mando de De Peru Construcción SAC

## 1. Alcance y cómo leer este informe

Este informe resume lo construido en la Parte 2, lo que muestra el cuadro de mando con **datos de ejemplo** y las recomendaciones para pasar a producción.

| Fuente de las cifras                   | Qué es                                                                                                       | Cómo tomarlas                                                                            |
| -------------------------------------- | ------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------- |
| **Parte 1** (`docs/parte1`)            | Hallazgos del análisis de los archivos reales de octubre-noviembre de 2026 (agregados, sin datos personales) | Reales, pero parciales: cubren unas 5 semanas en Logística y datos de ejemplo en RR. HH. |
| **Datos de ejemplo** (secciones 3 y 4) | Datos aleatorios y reproducibles generados con `cargar_demo`, calibrados con las proporciones de la Parte 1  | **Simulados.** Demuestran el funcionamiento; no describen la empresa                     |

Fecha de corte de los resultados de ejemplo: **12/11/2026**.

## 2. Qué se construyó

- Una aplicación web (Django, Python y PostgreSQL) con **resumen gerencial** y **una pestaña por área**: Proyectos, Logística y pagos, Préstamos y deuda, Recursos humanos y Calidad de datos.
- **Más de 50 indicadores** (53 con cálculo automático) definidos en `apps/*/kpis.py`, con fórmula, fuente, frecuencia, prioridad y semáforo editable. Listado en [diccionario_kpi.md](diccionario_kpi.md).
- **Actualización manual** con archivos limpios (20 tablas, validación estricta y registro de cada carga), con una **API** lista para automatizar después.
- Datos de ejemplo, 58 pruebas automáticas, configuración para Railway y una [guía](guia_estructura_escalamiento.md) de estructura, funcionamiento y escalamiento.
- Paleta de colores propia (azul petróleo, ámbar y semáforo verde/ámbar/rojo) usada en pantallas y gráficos.

Los indicadores de la Parte 1 que no se implementaron necesitan datos que hoy no existen: ahorro frente al precio del RQ (L20), cobertura del servicio de deuda (F12), costo financiero por proyecto (F13), rotación (H9) y valorización de almacén (P14).

## 3. Resultados del ejemplo (simulados)

### 3.1 Resumen por área

| Área      | Indicador                                             | Valor                     | Estado      |
| --------- | ----------------------------------------------------- | ------------------------- | ----------- |
| Proyectos | SPI de la cartera                                     | 0.85                      | Atención    |
| Proyectos | CPI (costo)                                           | 1.04                      | En meta     |
| Proyectos | Margen esperado al cierre                             | 32.9 %                    | En meta     |
| Proyectos | Flujo neto acumulado                                  | −S/ 2.76 M                | Crítico     |
| Logística | Deuda vencida (sobre lo por pagar)                    | 84.2 % de S/ 1.34 M       | Crítico     |
| Logística | RQ de emergencia y regularización                     | 82.6 %                    | Crítico     |
| Logística | Comprobantes con diferencia Logística vs Contabilidad | 11.4 %                    | Crítico     |
| Préstamos | Deuda vigente (capital)                               | S/ 10.50 M                | Informativo |
| Préstamos | Vencimientos a 90 días                                | S/ 3.86 M                 | Informativo |
| Préstamos | Cuotas vencidas sin pago                              | S/ 5,833                  | Atención    |
| RR. HH.   | Dotación / costo bruto del mes                        | 112 personas / S/ 515,500 | Informativo |
| RR. HH.   | Contratos por firmar o vencer                         | 14                        | Crítico     |
| RR. HH.   | Tardanzas                                             | 1.3 %                     | En meta     |
| Calidad   | Cargas rechazadas (30 días)                           | 25 %                      | Atención    |

De 53 indicadores: 15 en meta, 10 en atención, 8 críticos y el resto informativos.

### 3.2 Cartera de proyectos (ejemplo)

| Proyecto                      | Avance real | Avance plan | SPI  | CPI  | Margen esperado |
| ----------------------------- | ----------- | ----------- | ---- | ---- | --------------- |
| Polideportivo Ccollana        | 45.8 %      | 81.1 %      | 0.56 | 1.30 | 46.2 %          |
| Mejoramiento carretera JU-104 | 84.0 %      | 91.3 %      | 0.92 | 1.06 | 34.2 %          |
| Reservorio Iguain             | 84.0 %      | 97.8 %      | 0.86 | 0.99 | 29.4 %          |
| Puente Chacarilla Mencia      | 93.3 %      | 97.8 %      | 0.95 | 1.17 | 40.3 %          |
| Defensa ribereña Cherrelique  | 71.1 %      | 91.3 %      | 0.78 | 0.91 | 23.5 %          |
| Canal de riego Mochumi        | 81.2 %      | 81.1 %      | 1.00 | 1.03 | 32.2 %          |
| Defensa ribereña río Chochope | 88.3 %      | 93.8 %      | 0.94 | 1.02 | 31.4 %          |
| Canal Taymi 2                 | 61.1 %      | 70.0 %      | 0.87 | 0.87 | 19.7 %          |

### 3.3 Lectura de ejemplo

- **Atraso generalizado con costos bajo control**: SPI 0.85 con CPI 1.04. El problema es de ritmo, no de gasto. Collana (SPI 0.56) es el caso más grave; Taymi 2 y Cherrelique tienen además CPI menor a 1 (gasto superior al avance).
- **El flujo de caja de los proyectos es negativo** (−S/ 2.76 M): se paga más de lo que se cobra, lo que presiona la deuda.
- **Las compras no se planifican**: más de 8 de cada 10 requerimientos son de emergencia o regularización.
- **La deuda con proveedores está vencida casi en su totalidad**, con más de la mitad con más de 30 días.
- **La deuda financiera es de S/ 10.5 M** con un pico de vencimientos en diciembre (≈ 23 % de lo pendiente en un solo mes).

## 4. Lo que ya se sabe de los datos reales (Parte 1)

| Hallazgo                                                         | Cifra                            | Documento                                    |
| ---------------------------------------------------------------- | -------------------------------- | -------------------------------------------- |
| RQ de emergencia o regularización                                | 85 % de 396 RQ                   | [03_logistica.md](../parte1/03_logistica.md) |
| Ítems de RQ con precio                                           | 19 %                             | 03_logistica.md                              |
| Comprobantes no pagados ya vencidos                              | 144 de 200 (≈ S/ 2.3 M)          | 03_logistica.md                              |
| Comprobantes con importe distinto entre Logística y Contabilidad | 35 de 281                        | 03_logistica.md                              |
| Deuda financiera por pagar / mes más cargado                     | S/ 9.3 M / diciembre (S/ 4.87 M) | [02_prestamos.md](../parte1/02_prestamos.md) |
| Gastos del proyecto con vínculo a orden                          | 0 de 386 (columna `RQ` vacía)    | [01_proyectos.md](../parte1/01_proyectos.md) |
| EVM de Collana con alcances mezclados                            | CPI 1.19 o 2.08 según el alcance | 01_proyectos.md                              |

El ejemplo reproduce estos patrones a propósito, para que los indicadores muestren alertas parecidas a las esperadas con los datos reales.

## 5. Supuestos asumidos y qué hay que validar

| Supuesto implementado                                                                         | Pregunta pendiente (Parte 1, `08_preguntas_clave.md`) |
| --------------------------------------------------------------------------------------------- | ----------------------------------------------------- |
| El valor ganado se mide sin IGV, con base de costo meta (70 %) y solo componentes 01, 02 y 05 | P-01, P-02, P-03, P-04                                |
| El avance usa solo meses cerrados (anteriores al mes del corte)                               | P-06                                                  |
| Un gasto cuenta como real y pagado si su estado es PAGADO y no es "proyectado"                | P-12                                                  |
| Préstamos y reembolsos cargados al proyecto se tratan como costo no operativo                 | P-10                                                  |
| Una cuota solo está pagada si existe pago registrado                                          | F-04                                                  |
| Los dólares se convierten con el tipo de cambio de la tabla diaria                            | F-09, C-10                                            |
| La deuda personal del gerente se incluye por defecto (hay un filtro para excluirla)           | G-03                                                  |
| Entrada a las 08:00 con 10 minutos de tolerancia; la primera marca del día es la entrada      | H-06                                                  |
| El código del reloj se relaciona con la persona por el DNI sin ceros                          | H-05                                                  |
| El costo de personal es bruto, sin cargas sociales ni provisiones                             | H-10                                                  |
| Una orden tiene un solo centro de costo                                                       | L-06                                                  |
| Estados y condiciones de pago normalizados a catálogos cerrados                               | L-02, L-07, C-04                                      |

## 6. Recomendaciones

### 6.1 Para la toma de decisiones (con lo que ya muestra la Parte 1)

1. **Regularizar la deuda con proveedores.** Cada comprobante vencido es riesgo de desabastecimiento y de recargos. Establecer un calendario de pagos semanal y priorizar los vencidos de más de 30 días.
2. **Reducir las compras de emergencia.** Un 85 % de emergencias indica falta de planificación. Fijar una meta (por ejemplo, 40 %) y obligar a un plan de compras mensual por proyecto.
3. **Aliviar la concentración de vencimientos de diciembre.** Evaluar refinanciar o escalonar el pagaré mayor antes de diciembre; revisar el calendario de caja de los proyectos que lo respaldan.
4. **Medir los proyectos con una sola definición de valor ganado.** Aprobar el alcance (sin IGV, base de costo, componentes) y usarla en todos los informes.
5. **Registrar el pago real de las cuotas.** Hoy se asume que lo vencido está pagado; sin el registro no se puede conocer la mora.

### 6.2 Para los datos

1. Adoptar el **código de centro de costo (CC2)** como identificador único de proyecto en todas las áreas.
2. Incluir el **N.º de orden** en cada gasto de proyecto y el **código de proyecto** en la planilla de RR. HH.
3. Entregar los **archivos limpios** de `docs/parte1/07_archivos_limpios.md` (el sistema ya valida su estructura).
4. Unificar Contabilidad, Finanzas y Tesorería en **una sola tabla** de comprobantes.
5. Completar el **precio en los requerimientos** (hoy 19 %); sin él no se mide el ahorro.
6. Definir **dueño y fecha límite** de cada archivo (pregunta T-01).

### 6.3 Para el sistema

1. **Piloto por áreas**: empezar con Proyectos y Logística (tienen datos estructurados) y sumar Préstamos y RR. HH. cuando se confirmen los archivos reales.
2. Validar con cada responsable los umbrales de semáforo; hoy son propuestas. Se cambian en el administrador sin tocar código.
3. Antes de cargar datos reales: política de acceso, lugar autorizado de alojamiento y copias de seguridad (ver `GUIA_TRABAJO.md`).
4. Automatizar la carga por API cuando un archivo ya llegue estable dos o tres meses seguidos.
5. Mantener el historial (`calcular_kpis`) para ver tendencias: un valor aislado dice poco, la evolución sí.

## 7. Plan de siguientes pasos

| Fase                       | Contenido                                                                             | Condición                                 |
| -------------------------- | ------------------------------------------------------------------------------------- | ----------------------------------------- |
| 1. Validar definiciones    | Responder las preguntas bloqueantes de la Parte 1 y confirmar KPI y umbrales por área | Respuestas de los responsables            |
| 2. Piloto con datos reales | Cargar catálogos y los archivos de Proyectos y Logística en un entorno autorizado     | Aprobación de seguridad                   |
| 3. Ampliar                 | Préstamos y RR. HH. con datos reales; ajustes de pantallas                            | Archivos entregados con el formato limpio |
| 4. Automatizar             | Cargas programadas por API y alertas                                                  | Datos estables                            |
| 5. Nuevas oficinas         | Aplicar la receta de la sección 7.1 de la guía                                        | Decisión de gerencia                      |

## 8. Riesgos

- **Datos incompletos o inconsistentes**: la mayor parte de las alertas de calidad del archivo real se verán de inmediato. Se espera un periodo de depuración.
- **Definiciones sin validar**: un indicador mal definido es peor que ninguno; por eso cada KPI muestra su fórmula y su fuente.
- **Información sensible**: planillas, deuda y cuentas deben quedarse en ubicaciones autorizadas y con acceso por perfil.
- **Dependencia de pocas personas** para cargar archivos: documentar el proceso y definir suplentes.
