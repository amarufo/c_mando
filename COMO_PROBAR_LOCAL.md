# Guía de aprendizaje: ejecuta, entiende y escala el cuadro de mando

1. **Ejecutar** el cuadro de mando en tu computadora.
2. **Verlo funcionando** con datos simulados.
3. **Entender qué hace** cada pantalla, comando y carpeta.
4. **Probar** cargas de archivos, permisos, KPI y API.
5. **Aprender cómo escalarlo**: agregar KPI, agregar áreas, automatizar cargas y publicarlo en Railway.

> Los datos de ejemplo son simulados. Sirven para probar el sistema, pero no representan información real de la empresa.

## Estado verificado en esta computadora

La guía se probó el **13 de noviembre de 2026** con el entorno del workspace. Resultado:

- PostgreSQL local: **activo**.
- Migraciones: **aplicadas correctamente**.
- Datos de ejemplo: **cargados correctamente**.
- KPI registrados: **53**.
- Historial de KPI guardado: **371 valores**, equivalente a 53 KPI × 7 fechas de corte.
- Pruebas automáticas: **58 ejecutadas, 0 fallos y 0 errores**.
- Archivos estáticos: **generados correctamente**.
- API con token: **funciona** y devolvió los 53 KPI.
- API sin token: **rechaza correctamente con HTTP 401**.
- Todas las pantallas principales respondieron **HTTP 200**.

En esta sesión el servidor quedó ejecutándose en:

<http://127.0.0.1:8000/>

Usuario para ver todo: `gerencia`. Contraseña: `demo1234`.

## 1. Qué se va a probar

El cuadro de mando tiene:

- Una pantalla resumen para gerencia.
- Una pestaña para cada área: Proyectos, Logística, Préstamos, RRHH y Calidad de datos.
- Un diccionario con la definición, fórmula y fuente de cada KPI.
- Carga manual de archivos CSV/Excel.
- API REST para cargar información de forma automática.
- Usuarios y permisos por área.
- Base de datos PostgreSQL local, sin necesidad de instalar PostgreSQL manualmente.
- Pruebas automáticas del motor de KPI, importadores, pantallas y API.

### En una frase, ¿qué hace el sistema?

Recibe archivos limpios de las oficinas, los valida, los guarda en PostgreSQL, calcula indicadores y los muestra en pantallas con semáforos, gráficos y tablas para ayudar a gerencia a decidir.

### El viaje de un dato

```text
Archivo de una oficina
        ↓
Pantalla, comando o API
        ↓
Validador de columnas, tipos y códigos
        ↓
PostgreSQL: guarda todo o no guarda nada
        ↓
Funciones de cálculo del área
        ↓
KPI con valor y semáforo
        ↓
Pantalla web, diccionario, historial y API
```

Ejemplo: si Logística carga un comprobante, el sistema verifica que tenga fecha, proveedor, moneda y montos válidos. Si pasa la validación, se guarda. Luego los KPI de cuentas por pagar y deuda vencida lo toman en cuenta.

### Qué significa cada color del semáforo

| Estado      | Significado                                                                      |
|-------------|----------------------------------------------------------------------------------|
| En meta     | El valor cumple el objetivo.                                                     |
| Atención    | El valor todavía no es grave, pero hay que revisarlo.                            |
| Crítico     | El valor superó el límite aceptable.                                             |
| Informativo | El KPI informa un monto o cantidad; no tiene semáforo.                           |
| Sin datos   | No hay información suficiente para calcularlo.                                   |
| Error       | El cálculo falló por un dato inesperado; el resto del sistema sigue funcionando. |

## 2. Requisitos

Necesitas:

- Linux.
- Python 3.13. El archivo `.python-version` del proyecto indica esa versión.
- Acceso a una terminal.
- No necesitas instalar PostgreSQL: el proyecto usa `pixeltable-pgserver`, incluido en `requirements-dev.txt`.

En este workspace ya existe un entorno virtual funcional en:

```text
/home/amaru/dph_trabajo/.venv
```

Ese fue el entorno usado para ejecutar y validar esta guía.

## 3. Preparar el entorno

### Opción recomendada: usar el entorno ya instalado

Desde cualquier carpeta:

```bash
cd /home/amaru/dph_trabajo/c_mando
source /home/amaru/dph_trabajo/.venv/bin/activate
```

Comprueba que estás usando el entorno correcto:

```bash
which python
python --version
```

Debe mostrar algo parecido a:

```text
/home/amaru/dph_trabajo/.venv/bin/python
Python 3.13.5
```

El archivo `.env` ya fue creado para esta ejecución local. Si alguna vez falta, créalo así:

```bash
cp .env.example .env
```

El archivo `.env` queda con esta configuración mínima:

```dotenv
DJANGO_DEBUG=1
DJANGO_SECRET_KEY=desarrollo-local
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
```

En local no hace falta definir `DATABASE_URL`: Django se conectará al PostgreSQL local que levanta `scripts/pg_local.py`.

### Opción para empezar desde cero en otra computadora

Si el entorno compartido no existe, crea uno propio dentro del proyecto:

```bash
cd /home/amaru/dph_trabajo/c_mando
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
cp .env.example .env
```

A partir de ese momento, cuando la guía diga `python`, se refiere al Python del entorno activado.

### ¿Qué es un entorno virtual?

Es una carpeta con una instalación aislada de Python y las librerías del proyecto. Sirve para que este proyecto no mezcle sus dependencias con otros proyectos de tu computadora.

## 4. Levantar PostgreSQL local

Inicia la base de datos:

```bash
python scripts/pg_local.py start
```

La primera vez, el comando crea el directorio `.pgdata/` y la base `cuadro_mando`. En las siguientes ejecuciones reutiliza la información existente.

Para comprobar el estado:

```bash
python scripts/pg_local.py status
```

Si ves que ya existe `.pgdata/`, no lo borres como primer paso. Primero intenta `start` o `status`.

## 5. Crear las tablas y los grupos de acceso

Aplica las migraciones:

```bash
python3 manage.py migrate
```

Crea los grupos de usuarios:

```bash
python3 manage.py crear_grupos
```

Deberías ver los grupos:

- `gerencia`: ve todas las áreas.
- `proyectos`: ve solo Proyectos.
- `logistica`: ve solo Logística.
- `prestamos`: ve solo Préstamos.
- `rrhh`: ve solo RRHH.
- El área de Calidad de datos la ven gerencia y superusuarios.

### ¿Qué acabas de hacer?

- `migrate` creó o actualizó las tablas en PostgreSQL.
- `crear_grupos` creó los perfiles de acceso.
- Todavía no hay datos operativos; eso se resuelve en el siguiente paso.

Una **migración** es un archivo que describe cambios en la base de datos: crear una tabla, agregar una columna, crear un índice, etc. Django las aplica en orden para que el código y la base coincidan.

## 6. Cargar los datos de ejemplo

Ejecuta:

```bash
python3 manage.py cargar_demo --limpiar
```

Este comando hace varias cosas:

1. Borra los datos anteriores de las áreas, porque se pasó `--limpiar`.
2. Crea catálogos básicos.
3. Genera datos simulados de Proyectos, Logística, Préstamos y RRHH.
4. Registra cargas de ejemplo en la pantalla de Calidad de datos.
5. Crea usuarios de prueba.
6. Calcula el historial de KPI hasta el corte de demostración `2026-11-12`.

Usuarios creados por la carga de ejemplo:

| Usuario     | Contraseña | Qué puede ver   |
|-------------|------------|-----------------|
| `gerencia`  | `demo1234` | Todas las áreas |
| `proyectos` | `demo1234` | Solo Proyectos  |
| `logistica` | `demo1234` | Solo Logística  |
| `prestamos` | `demo1234` | Solo Préstamos  |
| `rrhh`      | `demo1234` | Solo RRHH       |

En la ejecución verificada se generaron, entre otros:

| Datos generados           | Cantidad |
|---------------------------|---------:|
| Empresas                  |        6 |
| Proyectos                 |        8 |
| Gastos de proyectos       |    2,069 |
| Requerimientos            |    1,648 |
| Órdenes                   |    1,144 |
| Comprobantes              |    1,127 |
| Préstamos                 |       21 |
| Personas                  |      117 |
| Marcaciones               |    1,559 |
| Valores históricos de KPI |      371 |
| Registros de carga        |        4 |

¿Por qué hay 371 valores históricos? Porque el sistema calculó **53 KPI** para **7 fechas de corte**: 53 × 7 = 371.

También puedes crear un superusuario para entrar al administrador de Django:

```bash
python manage.py createsuperuser
```

## 7. Ejecutar la aplicación

Levanta el servidor de desarrollo:

```bash
python manage.py runserver 127.0.0.1:8000
```

Abre en el navegador:

- Aplicación: <http://127.0.0.1:8000/>
- Inicio de sesión: <http://127.0.0.1:8000/ingresar/>
- Administración de Django: <http://127.0.0.1:8000/admin/>
- Verificación de salud: <http://127.0.0.1:8000/salud/>

La ruta `/salud/` no pide sesión y debe responder algo parecido a:

```json
{"estado": "ok"}
```

Esto confirma dos cosas: la aplicación está levantada y puede consultar PostgreSQL.

### Si el servidor ya estaba ejecutándose

No necesitas levantar otro. Abre directamente:

<http://127.0.0.1:8000/>

Si ves un error de conexión, vuelve a esta sección y ejecuta `runserver`.

## 8. Recorrido de prueba por las pantallas

### 8.1. Comprobar acceso de gerencia

1. Entra a <http://127.0.0.1:8000/ingresar/>.
2. Inicia sesión con `gerencia` / `demo1234`.
3. Debes ver el resumen general.
4. Revisa estas rutas:

| Ruta               | Qué debes comprobar                            |
|--------------------|------------------------------------------------|
| `/`                | Tarjetas de KPI, alertas y gráficos resumidos  |
| `/area/proyectos/` | Indicadores, gráficos y tablas de Proyectos    |
| `/area/logistica/` | Indicadores y tablas de Logística              |
| `/area/prestamos/` | Indicadores de deuda, cuotas y pagos           |
| `/area/rrhh/`      | Indicadores de personal, planilla y asistencia |
| `/area/calidad/`   | Historial de cargas, errores y completitud     |
| `/kpi/`            | Diccionario con fórmula, fuente y umbrales     |
| `/cargas/`         | Pantalla para subir y validar archivos         |

### 8.2. Comprobar permisos por área

Cierra sesión y entra con `rrhh` / `demo1234`.

Comprueba que:

- Puedes abrir `/area/rrhh/`.
- No puedes abrir `/area/prestamos/`; debe responder `403`.
- En el resumen solo aparecen KPI del área de RRHH.
- En `/cargas/` solo aparecen tablas permitidas para RRHH.

Repite la prueba con los usuarios `proyectos`, `logistica` y `prestamos` si quieres verificar cada área por separado.

### 8.3. Comprobar detalle e historial de un KPI

Con el usuario `gerencia`:

1. Abre `/kpi/`.
2. Busca un KPI, por ejemplo `P3`.
3. Entra al detalle del KPI.
4. Debes ver:
   - Nombre y descripción.
   - Fórmula.
   - Fuente de datos.
   - Valor actual.
   - Estado del semáforo.
   - Gráfico de evolución, porque `cargar_demo` ya generó varios cortes históricos.

### 8.4. Comprobar calidad de datos

Abre `/area/calidad/`.

La carga de ejemplo incluye registros correctos y también una carga llamada `gastos_con_errores.csv`, creada intencionalmente con errores. Esto permite comprobar que el sistema:

- Registra cada archivo cargado.
- Cuenta filas leídas, válidas y rechazadas.
- Muestra la fila y columna donde ocurrió cada error.
- No guarda un archivo completo cuando contiene errores graves.

### 8.5. Qué está pasando cuando abres una pantalla

Cuando entras a una pantalla, por ejemplo `/area/proyectos/`, Django ejecuta este recorrido:

1. **Comprueba sesión.** Si no iniciaste sesión, te envía a `/ingresar/`.
2. **Comprueba permisos.** Verifica si tu usuario es superusuario, pertenece a `gerencia` o pertenece al grupo del área.
3. **Lee filtros.** Toma la fecha de corte, empresa y proyecto seleccionados.
4. **Busca los KPI del área.** Cada área registra sus indicadores al iniciar la aplicación.
5. **Consulta PostgreSQL.** Los cálculos leen proyectos, gastos, órdenes, préstamos, planillas u otras tablas.
6. **Evalúa el semáforo.** Compara el valor con sus umbrales de atención y crítico.
7. **Construye gráficos y tablas.** Cada área entrega sus datos; las plantillas compartidas los dibujan.
8. **Devuelve HTML.** El navegador muestra la página.

Archivos principales de ese recorrido:

- [config/urls.py](config/urls.py): conecta las URLs principales.
- [apps/core/urls.py](apps/core/urls.py): define las rutas del cuadro de mando.
- [apps/core/views.py](apps/core/views.py): prepara las pantallas.
- [apps/core/dashboard.py](apps/core/dashboard.py): registra áreas y permisos.
- [apps/core/kpi.py](apps/core/kpi.py): motor de KPI y semáforos.
- [apps/proyectos/kpis.py](apps/proyectos/kpis.py): ejemplo de KPI de un área.
- [templates/dashboard/](templates/dashboard/): plantillas HTML compartidas.

### 8.6. Qué hace cada pantalla

| Pantalla           | Qué hace                                                     | Pregunta que ayuda a responder                                             |
|--------------------|--------------------------------------------------------------|----------------------------------------------------------------------------|
| Resumen            | Junta los KPI más importantes de las áreas visibles.         | ¿Dónde debo poner atención hoy?                                            |
| Proyectos          | Mide avance, costo, margen y valor ganado.                   | ¿La obra va según lo planificado y dentro del costo esperado?              |
| Logística y pagos  | Mide compras, tiempos, comprobantes y deuda con proveedores. | ¿Qué debemos pagar y qué procesos están demorando?                         |
| Préstamos y deuda  | Muestra capital vigente, vencimientos y pagos.               | ¿Qué deuda existe y qué vence pronto?                                      |
| Recursos humanos   | Muestra dotación, costos, asistencia y obligaciones.         | ¿Cuántas personas hay, cuánto cuestan y qué obligaciones están pendientes? |
| Calidad de datos   | Muestra cargas, errores y completitud.                       | ¿Puedo confiar en los datos cargados?                                      |
| Diccionario de KPI | Explica cada indicador, fórmula, fuente y umbrales.          | ¿Qué significa exactamente este número?                                    |
| Cargar datos       | Permite subir y validar archivos limpios.                    | ¿Este archivo puede entrar al sistema sin romper nada?                     |
| Administrador      | Permite editar usuarios, catálogos y configuración.          | ¿Cómo cambio un umbral o doy acceso a una persona?                         |

### 8.7. Qué hace cada carpeta

| Carpeta o archivo                                   | Qué contiene                                                                              |
|-----------------------------------------------------|-------------------------------------------------------------------------------------------|
| [config/](config/)                                  | Configuración central de Django, URLs principales y arranque WSGI.                        |
| [apps/core/](apps/core/)                            | Lo compartido: catálogos, motor KPI, validadores, pantallas, API, comandos y tema visual. |
| [apps/proyectos/](apps/proyectos/)                  | Tablas, cálculos, KPI, gráficos, importadores y datos demo de Proyectos.                  |
| [apps/logistica/](apps/logistica/)                  | Lo propio de Logística y pagos.                                                           |
| [apps/prestamos/](apps/prestamos/)                  | Lo propio de Préstamos y deuda.                                                           |
| [apps/rrhh/](apps/rrhh/)                            | Lo propio de Recursos Humanos.                                                            |
| [templates/](templates/)                            | HTML de las pantallas.                                                                    |
| [static/](static/)                                  | CSS, Bootstrap e íconos.                                                                  |
| [scripts/pg_local.py](scripts/pg_local.py)          | Levanta PostgreSQL local sin instalación manual.                                          |
| [docs/parte2/](docs/parte2/)                        | Guías, diccionario de KPI e informe final.                                                |
| [requirements.txt](requirements.txt)                | Dependencias necesarias en producción.                                                    |
| [requirements-dev.txt](requirements-dev.txt)        | Dependencias de producción más PostgreSQL embebido para desarrollo.                       |
| [railway.json](railway.json) y [Procfile](Procfile) | Instrucciones para desplegar en Railway.                                                  |

### 8.8. Conceptos básicos de Django usados aquí

| Concepto   | Explicación sencilla                                            | Dónde se ve                           |
|------------|-----------------------------------------------------------------|---------------------------------------|
| Proyecto   | El sistema completo.                                            | `config/`                             |
| Aplicación | Un módulo con una responsabilidad.                              | `apps/proyectos/`, `apps/rrhh/`, etc. |
| Modelo     | Una tabla de la base de datos escrita como clase Python.        | `models.py`                           |
| Migración  | Instrucción para crear o cambiar tablas.                        | `migrations/`                         |
| Vista      | Función que prepara una página o respuesta.                     | `views.py`, `api.py`                  |
| Plantilla  | HTML que muestra la información.                                | `templates/`                          |
| Comando    | Acción ejecutable desde terminal.                               | `management/commands/`                |
| API        | Puerta para que otro programa consulte o cargue datos.          | `api.py`                              |
| ORM        | Forma de consultar la base usando Python en vez de SQL directo. | `Modelo.objects...`                   |

### 8.9. Ejemplo de KPI explicado sin tecnicismos

Uno de los KPI de Proyectos es `P3`, llamado **SPI (cronograma)**.

La idea es comparar:

- **PV**: valor del trabajo que debía estar avanzado a la fecha de corte.
- **EV**: valor del trabajo realmente avanzado.

La fórmula es:

```text
SPI = EV / PV
```

Interpretación:

- `SPI = 1.00`: avanzaste exactamente lo planeado.
- `SPI > 1.00`: vas adelantado.
- `SPI < 1.00`: vas atrasado.

Otro KPI relacionado es `P5`, **CPI (costo)**:

```text
CPI = EV / AC
```

Aquí `AC` es el costo real incurrido. Si `CPI` es menor que 1, estás gastando más de lo que corresponde al avance logrado.

Estos cálculos usan importes **sin IGV** para comparar costos y avances de forma consistente.

### 8.10. Ruta de aprendizaje sugerida

| Nivel | Actividad                                               | Qué aprendes                                         |
|-------|---------------------------------------------------------|------------------------------------------------------|
| 1     | Ejecutar el proyecto y entrar con `gerencia`.           | Qué es el sistema y cómo se navega.                  |
| 2     | Entrar con `rrhh` y comparar menús y permisos.          | Seguridad por área.                                  |
| 3     | Abrir un KPI y leer fórmula, fuente y umbrales.         | Cómo se interpreta un indicador.                     |
| 4     | Descargar una plantilla y validar un archivo.           | Cómo entra información al sistema.                   |
| 5     | Probar un archivo con error.                            | Por qué el sistema protege la base de datos.         |
| 6     | Consultar la API con token.                             | Cómo se automatizará la carga en el futuro.          |
| 7     | Ejecutar pruebas automáticas.                           | Cómo se comprueba que un cambio no rompa el sistema. |
| 8     | Leer `kpis.py` de un área y compararlo con la pantalla. | Cómo una fórmula llega a una tarjeta visual.         |
| 9     | Cambiar un umbral desde el administrador.               | Cómo ajustar reglas sin tocar código.                |
| 10    | Leer la guía de escalamiento.                           | Cómo agregar áreas, KPI y automatización.            |

## 9. Probar la carga manual de archivos

### 9.1. Descargar una plantilla

Con sesión iniciada como `gerencia`, abre:

<http://127.0.0.1:8000/cargas/>

Descarga una plantilla desde la pantalla o entra directamente a:

<http://127.0.0.1:8000/cargas/plantilla/cat_empresa.csv>

También puedes generar todas las plantillas por terminal:

```bash
python manage.py exportar_plantillas
```

Quedarán en:

```text
exports/plantillas/
```

### 9.2. Validar un archivo pequeño

Crea un archivo de prueba, por ejemplo `/tmp/empresa_prueba.csv`, con este contenido:

```csv
ruc,razon_social,nombre_corto
20999999999,Empresa de Prueba SAC,PRUEBA
```

Valídalo sin guardar:

```bash
python manage.py importar_archivo cat_empresa /tmp/empresa_prueba.csv --validar
```

Debe indicar que la carga es una simulación y que la fila es válida.

Luego cárgalo de verdad:

```bash
python manage.py importar_archivo cat_empresa /tmp/empresa_prueba.csv
```

Después puedes comprobarlo en:

- La pantalla `/cargas/`, dentro del historial.
- El administrador de Django.
- Las consultas de la aplicación.

### 9.3. Probar un error de validación

Crea `/tmp/empresa_mala.csv`:

```csv
ruc,razon_social,nombre_corto
1,Empresa incompleta,
```

Ejecuta:

```bash
python manage.py importar_archivo cat_empresa /tmp/empresa_mala.csv --validar
```

Debe aparecer como rechazada o con error, indicando la fila y columna que debes corregir.

## 10. Probar la API REST

La API está pensada para que, más adelante, un script pueda cargar archivos automáticamente.

### 10.1. Crear un token

Con el usuario `gerencia` ya creado por la demo:

```bash
python manage.py crear_token gerencia
```

El comando devuelve una cadena larga. Guárdala en una variable:

```bash
TOKEN=$(python manage.py crear_token gerencia)
```

### 10.2. Consultar KPI

```bash
curl -H "Authorization: Token $TOKEN" \
  http://127.0.0.1:8000/api/v1/kpis/
```

Debes recibir un JSON con el corte y la lista de KPI visibles para el usuario.

### 10.3. Consultar el historial de un KPI

```bash
curl -H "Authorization: Token $TOKEN" \
  http://127.0.0.1:8000/api/v1/kpis/P3/historial/
```

### 10.4. Validar datos por API sin guardarlos

```bash
curl -X POST \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"filas":[{"ruc":"20888888888","razon_social":"Empresa API SAC","nombre_corto":"API"}]}' \
  "http://127.0.0.1:8000/api/v1/cargas/cat_empresa/?validar=1"
```

Debe responder con estado `SIMULACION`. Como está en modo validación, no guarda la fila.

### 10.5. Probar que la API exige autenticación

```bash
curl http://127.0.0.1:8000/api/v1/kpis/
```

Sin token debe responder `401 Unauthorized`.

### 10.6. Buenas prácticas y qué no hacer

Haz:

- Usa `--validar` antes de guardar un archivo nuevo.
- Corrige el archivo y vuelve a cargarlo; la misma clave actualiza en lugar de duplicar.
- Revisa **Calidad de datos** después de cada carga.
- Usa usuarios por área en vez de compartir el usuario de gerencia.
- Usa tokens distintos para cada script o persona.
- Ejecuta las pruebas antes de desplegar cambios.

No hagas:

- No edites la base de datos manualmente si existe un importador.
- No subas `.env`, archivos reales ni `exports/` a Git.
- No ejecutes `cargar_demo` en producción.
- No compartas tokens ni contraseñas.
- No uses el servidor de desarrollo como servidor público.
- No cambies una fórmula de KPI sin actualizar su prueba y su documentación.

## 11. Recalcular KPI

Los KPI principales se calculan al abrir las pantallas, pero el historial de evolución usa la tabla `KPISnapshot`.

Para guardar un corte específico y seis cierres mensuales anteriores:

```bash
python manage.py calcular_kpis --corte 2026-11-12 --historial 6
```

Para usar la fecha actual:

```bash
python manage.py calcular_kpis
```

Después de cargar archivos reales, el flujo recomendado es:

```bash
python manage.py importar_archivo <tabla> <archivo>
python manage.py calcular_kpis --historial 6
```

### 11.1. Flujo diario recomendado con datos reales

Cuando el sistema pase de demo a operación, el trabajo diario o semanal debería verse así:

1. **Recibir o generar el archivo limpio.** Cada oficina usa su plantilla.
2. **Validar primero.** Sube el archivo marcando *Solo validar* o usa `--validar`.
3. **Corregir errores.** Revisa fila, columna y motivo.
4. **Cargar.** Repite el archivo ya corregido sin modo validación.
5. **Revisar Calidad de datos.** Confirma cuántas filas entraron.
6. **Recalcular historial.** Ejecuta `calcular_kpis` si quieres guardar el corte.
7. **Revisar el resumen.** Atiende primero los KPI críticos y luego los de atención.

Orden recomendado de carga:

```text
Catálogos → proveedores → proyectos/presupuestos → movimientos de cada área
```

¿Por qué ese orden? Porque muchas filas hacen referencia a códigos ya existentes: empresa, centro de costo, categoría o proveedor.

## 12. Ejecutar las pruebas automáticas

La base PostgreSQL local debe estar levantada:

```bash
python scripts/pg_local.py status
```

Ejecuta la comprobación general de Django:

```bash
python manage.py check
```

Ejecuta todas las pruebas:

```bash
python manage.py test
```

También puedes ejecutar solo las pruebas del núcleo:

```bash
python manage.py test apps.core.tests
```

Las pruebas comprueban, entre otras cosas:

- Semáforos y formato de KPI.
- Registro de KPI sin códigos duplicados.
- Cálculo de KPI por área.
- Validación de columnas, fechas, números y listas cerradas.
- Que una carga con errores no guarde filas parciales.
- Que cargar dos veces la misma clave actualice en lugar de duplicar.
- Permisos de pantallas por grupo.
- Autenticación y permisos de la API.
- Modo de validación sin guardar.

### Cómo leer el resultado

Si todo está bien verás algo parecido a:

```text
Ran 58 tests
OK
```

Si algo falla, Django muestra:

- Nombre de la prueba.
- Archivo y línea aproximada.
- Valor esperado.
- Valor obtenido.

La idea de las pruebas es que puedas cambiar código con más seguridad: si un cambio rompe una regla importante, una prueba debería avisarte antes de que lo vea un usuario.

## 13. Cómo escalar el sistema

Escalar no significa solamente "que aguante más usuarios". En este proyecto significa cuatro cosas:

1. Agregar más indicadores.
2. Agregar más tablas o archivos de carga.
3. Agregar más áreas u oficinas.
4. Pasar de carga manual a carga automática.

### Agregar un KPI nuevo

Supongamos que Proyectos quiere medir "gasto sin orden de compra".

Flujo recomendado:

1. Identifica la tabla fuente, por ejemplo `Gasto`.
2. Escribe una prueba con datos pequeños calculables a mano.
3. Crea la función en [apps/proyectos/kpis.py](apps/proyectos/kpis.py).
4. Decórala con `@kpi(...)` indicando código, área, unidad, fórmula y umbrales.
5. Ejecuta `python manage.py test`.
6. Ejecuta `python manage.py generar_diccionario_kpi` para actualizar la documentación.
7. Revisa la pantalla del área y el diccionario.

Forma general:

```python
@kpi(
    codigo="PXX",
    area="proyectos",
    nombre="Gasto sin orden",
    unidad="pct",
    direccion="menor",
    umbral_alerta=10,
    umbral_critico=20,
    formula="Gastos sin orden / gastos totales",
    fuente="Gasto",
)
def gasto_sin_orden(ctx):
    ...
```

No necesitas crear una URL ni una plantilla nueva: el motor de KPI lo descubre y lo muestra.

### Agregar una tabla de carga nueva

1. Define el modelo en el `models.py` del área.
2. Crea la migración con `python manage.py makemigrations`.
3. Aplícala con `python manage.py migrate`.
4. Declara el importador en el `importers.py` del área.
5. Agrega columnas, tipos, obligatoriedad y clave única.
6. Genera la plantilla con `exportar_plantillas`.
7. Prueba con `importar_archivo --validar`.
8. Agrega pruebas automáticas.

El mismo importador queda disponible en la pantalla de carga, en el comando y en la API.

### Agregar un área nueva

Por ejemplo, para crear un área llamada Almacén:

1. Crea `apps/almacen/` copiando el molde de otra área.
2. Define sus modelos en `models.py`.
3. Define sus cálculos en `services.py` si necesita lógica reutilizable.
4. Define sus KPI en `kpis.py`.
5. Define gráficos y tablas en `dashboard.py`.
6. Define sus archivos limpios en `importers.py`.
7. Registra el área en `apps.py`.
8. Agrega `"apps.almacen"` a `INSTALLED_APPS`.
9. Ejecuta migraciones y `crear_grupos`.

Después aparecen automáticamente:

- Pestaña del área.
- Permiso por grupo.
- KPI en el diccionario.
- Tablas de carga permitidas.
- Acceso por API según permisos.

### Pasar de carga manual a carga automática

| Etapa          | Qué hace una persona                        | Qué hace el sistema                                                         |
|----------------|---------------------------------------------|-----------------------------------------------------------------------------|
| Manual actual  | Descarga una plantilla, la llena y la sube. | Valida, guarda y registra la carga.                                         |
| Semiautomática | Deja el archivo en una carpeta compartida.  | Un script programado lo envía a la API o al comando.                        |
| Automática     | La oficina actualiza su sistema origen.     | Un conector consulta el origen, transforma los datos y llama al importador. |

La regla importante es no saltarse el importador: aunque la carga sea automática, debe pasar por las mismas validaciones.

### Escalar el rendimiento

Si el sistema crece:

- Usa índices en columnas filtradas con frecuencia.
- Usa `KPISnapshot` para mostrar históricos sin recalcular todo.
- Programa `calcular_kpis` después de cargas masivas.
- Mueve cálculos pesados a tareas programadas.
- Considera vistas materializadas de PostgreSQL para reportes grandes.
- Revisa consultas lentas con `EXPLAIN` antes de agregar índices.

### Escalar el despliegue

Local usa PostgreSQL embebido. Railway usa PostgreSQL administrado:

1. Railway inyecta `DATABASE_URL`.
2. Django detecta esa variable y cambia la conexión.
3. `collectstatic` prepara CSS y JavaScript.
4. `migrate` actualiza la base.
5. `crear_grupos` asegura los perfiles.
6. `gunicorn` ejecuta la aplicación.
7. `/salud/` permite a Railway saber si el servicio está sano.

La guía detallada de arquitectura y despliegue está en [docs/parte2/guia_estructura_escalamiento.md](docs/parte2/guia_estructura_escalamiento.md).

## 14. Probar un arranque parecido a producción

Esto es opcional. Sirve para comprobar que los archivos estáticos y Gunicorn funcionan como en Railway, pero sin salir de tu computadora.

Con la base de datos activa:

```bash
DJANGO_DEBUG=0 \
DJANGO_SECRET_KEY=local-seguro \
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost \
DJANGO_SSL_REDIRECT=0 \
python manage.py collectstatic --noinput
```

Luego:

```bash
DJANGO_DEBUG=0 \
DJANGO_SECRET_KEY=local-seguro \
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost \
DJANGO_SSL_REDIRECT=0 \
gunicorn config.wsgi --bind 127.0.0.1:8001 --workers 2
```

Abre:

<http://127.0.0.1:8001/salud/>

Para volver al modo normal de desarrollo, detén Gunicorn con `Ctrl+C` y vuelve a usar `runserver` con `DJANGO_DEBUG=1` en `.env`.

## 15. Apagar todo

Detén el servidor web con:

```text
Ctrl+C
```

Detén PostgreSQL local:

```bash
python scripts/pg_local.py stop
```

Sal del entorno virtual:

```bash
deactivate
```

Si ya saliste del entorno, puedes detener PostgreSQL usando el Python real del workspace:

```bash
/home/amaru/dph_trabajo/.venv/bin/python scripts/pg_local.py stop
```

## 16. Reiniciar desde cero

Solo hazlo si quieres borrar todos los datos locales:

```bash
/home/amaru/dph_trabajo/.venv/bin/python scripts/pg_local.py stop
rm -rf .pgdata
source /home/amaru/dph_trabajo/.venv/bin/activate
python3 scripts/pg_local.py start
python3 manage.py migrate
python3 manage.py crear_grupos
python3 manage.py cargar_demo --limpiar
python3 manage.py runserver 127.0.0.1:8000
```

### 16.1. Autoevaluación rápida

Después de seguir la guía deberías poder responder:

1. ¿Qué comando levanta PostgreSQL local?
2. ¿Qué comando crea las tablas?
3. ¿Qué comando genera datos simulados?
4. ¿Qué usuario ve todas las áreas?
5. ¿Qué pasa si un usuario de RRHH intenta abrir Préstamos?
6. ¿Qué hace el modo `--validar`?
7. ¿Por qué una carga con errores no guarda filas parciales?
8. ¿Qué diferencia hay entre un KPI calculado al momento y un `KPISnapshot`?
9. ¿Qué archivo modificarías para agregar un KPI de Proyectos?
10. ¿Qué variable usa Railway para conectar la base de datos?

Si no puedes responder alguna, vuelve a la sección correspondiente y prueba el comando otra vez.

### 16.2. Glosario mínimo

| Palabra      | Significado sencillo                                                         |
|--------------|------------------------------------------------------------------------------|
| KPI          | Indicador clave de desempeño. Un número que resume una situación importante. |
| Corte        | Fecha hasta la cual se calcula la información.                               |
| Snapshot     | Fotografía guardada del valor de un KPI en una fecha.                        |
| Catálogo     | Tabla de códigos compartidos, como empresas, centros de costo o categorías.  |
| Importador   | Código que lee, valida y guarda un archivo limpio.                           |
| Plantilla    | Archivo CSV con las columnas exactas que debe entregar una oficina.          |
| Token        | Clave que permite a un script usar la API.                                   |
| Migración    | Cambio controlado de la estructura de la base de datos.                      |
| Semáforo     | Clasificación visual: en meta, atención, crítico o informativo.              |
| Valor ganado | Técnica que compara avance planificado, avance real y costo real.            |
| Railway      | Plataforma donde se puede publicar la aplicación y su base PostgreSQL.       |

## 17. Problemas frecuentes

### `python3.13: command not found`

No está instalado Python 3.13 o no está en el `PATH`. Instálalo y vuelve a crear `.venv`.

### Django no puede conectarse a PostgreSQL

Comprueba que la base esté activa:

```bash
python scripts/pg_local.py status
```

Si no está activa:

```bash
python scripts/pg_local.py start
```

### `No se encontró pg_ctl`

Las dependencias de desarrollo no están completas. Instala de nuevo:

```bash
pip install -r requirements-dev.txt
```

### El puerto 8000 está ocupado

Usa otro puerto:

```bash
python manage.py runserver 127.0.0.1:8001
```

### Veo `403 Forbidden`

El usuario no pertenece al grupo del área. Para verificar todo, entra con `gerencia` / `demo1234` o con un superusuario.

### No aparecen gráficos históricos

Calcula el historial:

```bash
python manage.py calcular_kpis --corte 2026-11-12 --historial 6
```

### Quiero datos nuevos de ejemplo

```bash
python manage.py cargar_demo --limpiar --semilla 2027
```

Cambiar la semilla genera otro conjunto de datos reproducible.

## 18. Comprobación rápida completa

Cuando el entorno ya esté creado, esta es la secuencia mínima:

```bash
cd /home/amaru/dph_trabajo/c_mando
source /home/amaru/dph_trabajo/.venv/bin/activate
python scripts/pg_local.py start
python manage.py migrate
python manage.py check
python manage.py test
python manage.py cargar_demo --limpiar
python manage.py runserver 127.0.0.1:8000
```

Luego entra a <http://127.0.0.1:8000/> con `gerencia` / `demo1234`.

## 19. Siguiente lectura recomendada

Cuando ya lo hayas visto funcionando, sigue este orden:

1. [Guía de estructura y escalamiento](docs/parte2/guia_estructura_escalamiento.md): arquitectura completa.
2. [Diccionario de KPI](docs/parte2/diccionario_kpi.md): fórmulas, fuentes y umbrales.
3. [Informe final](docs/parte2/informe_final.md): resultados, límites y recomendaciones.
4. [Preguntas clave](docs/parte1/08_preguntas_clave.md): supuestos pendientes de confirmar con cada área.

La mejor forma de aprender el sistema es elegir un KPI en la pantalla, leer su fórmula en el diccionario, buscar su función en el archivo `kpis.py` del área y comparar el resultado con las tablas de la base de datos.
