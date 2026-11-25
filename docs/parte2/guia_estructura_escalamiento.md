# Guía del cuadro de mando: estructura, funcionamiento y escalamiento

Esta guía explica cómo está construido el cuadro de mando de De Peru Construcción SAC, cómo se calculan los indicadores (KPI), cómo se actualizan los datos y cómo se agrega una oficina nueva o se despliega en Railway. Está escrita para poder mantener el sistema sin conocer Django a fondo.

> **Importante.** Los datos que trae el sistema son **simulados** (se generan con `cargar_demo`). Sirven para ver el funcionamiento; las cifras no describen la empresa. Los archivos reales no deben subirse a Git (ver `GUIA_TRABAJO.md`).

## 1. Puesta en marcha local

Desde `c_mando/`, con el entorno `.venv`:

```bash
.venv/bin/python3 scripts/pg_local.py start          # PostgreSQL local (solo la primera vez de cada sesión)
.venv/bin/python3 manage.py migrate                  # crea las tablas
.venv/bin/python3 manage.py cargar_demo --limpiar    # datos de ejemplo + usuarios de prueba + historial de KPI
.venv/bin/python3 manage.py runserver 8000           # http://127.0.0.1:8000
.venv/bin/python3 manage.py test apps                # pruebas automáticas (58)
```

Usuarios de ejemplo (clave `demo1234`, solo se crean con `DEBUG` o `DEMO_USUARIOS=1`): `gerencia` (ve todo), `proyectos`, `logistica`, `prestamos`, `rrhh` (cada uno ve solo su área).

La configuración vive en variables de entorno (archivo `.env`, modelo en `.env.example`). Sin `DATABASE_URL` se usa el PostgreSQL local; con `DATABASE_URL` (Railway) se usa esa base.

## 2. Estructura del proyecto

```text
c_mando/
├── config/                 Configuración de Django (settings, urls, wsgi)
├── apps/
│   ├── core/               Lo compartido: catálogos, motor de KPI, cargas, pantallas, API
│   │   ├── kpi.py              Motor: define, registra, calcula y evalúa KPI
│   │   ├── importers.py        Cargador de archivos limpios (CSV/Excel) con validación
│   │   ├── dashboard.py        Registro de pantallas por área y permisos
│   │   ├── theme.py            Paleta de colores y estilo de gráficos
│   │   ├── views.py, api.py    Pantallas web y API REST
│   │   └── management/commands/  Comandos (cargar_demo, calcular_kpis, importar_archivo, ...)
│   ├── proyectos/          Una carpeta por área, todas con el mismo molde:
│   │   ├── models.py           Tablas del área
│   │   ├── services.py         Cálculos reutilizables (p. ej. valor ganado)
│   │   ├── kpis.py             Indicadores del área (@kpi)
│   │   ├── dashboard.py        Gráficos y tablas de la pestaña
│   │   ├── importers.py        Archivos limpios que carga el área
│   │   ├── demo.py             Datos de ejemplo
│   │   └── apps.py             Registra KPI y pestaña al iniciar
│   ├── logistica/  prestamos/  rrhh/   (mismo molde)
├── templates/  static/     Pantallas (Bootstrap), estilos y paleta
├── scripts/pg_local.py     PostgreSQL embebido para desarrollo
├── docs/parte2/            Esta guía, el diccionario de KPI y el informe final
├── railway.json  Procfile  Configuración de despliegue
└── requirements.txt        Dependencias (requirements-dev.txt añade el PostgreSQL local)
```

Se sigue el criterio de la contrapropuesta de RR. HH.: **una aplicación por área**, cada una dueña de sus tablas; lo compartido está en `core`; las áreas se enlazan por **códigos estables** (RUC, centro de costo CC2, DNI, N.º de orden), no por claves foráneas entre áreas.

## 3. Cómo se arma una pantalla

```mermaid
flowchart LR
    A[Archivo limpio<br/>CSV/Excel] -->|importers.py<br/>valida y guarda| B[(PostgreSQL)]
    M[manage.py cargar_demo] --> B
    B --> S[services.py<br/>cálculos del área]
    S --> K[kpis.py<br/>@kpi]
    K --> R[REGISTRO de KPI]
    R --> V[Resumen y pestaña de área]
    R --> D[Diccionario de KPI]
    R --> API[API /api/v1/kpis/]
    R --> SN[(Historial KPISnapshot)]
    B --> G[dashboard.py<br/>gráficos Plotly]
    G --> V
```

1. Al iniciar, cada app ejecuta `ready()` y **registra** sus KPI y su pestaña.
2. Cuando el usuario abre `/area/proyectos/`, la vista lee los filtros (fecha de corte, empresa, proyecto), calcula los KPI del área con esos filtros y pide al área sus gráficos.
3. La plantilla pinta las tarjetas de KPI (con semáforo) y los gráficos. Todo el HTML sale de plantillas genéricas: **el área solo entrega datos**.

## 4. Cómo se calcula un KPI

Un KPI es una función decorada con `@kpi(...)`. Ejemplo real (`apps/proyectos/kpis.py`):

```python
@kpi(codigo="P3", area="proyectos", nombre="SPI (cronograma)", unidad="ratio", direccion="mayor",
     umbral_alerta=0.90, umbral_critico=0.75, resumen=True,
     formula="EV / PV = avance real / avance planificado", fuente="Valorizacion")
def spi(ctx: Contexto) -> Valor:
    _, total = _total(ctx)
    return Valor(total.spi, f"EV {total.ev:,.0f} / PV {total.pv:,.0f}")
```

- `ctx` (`Contexto`) trae la **fecha de corte** y los filtros de empresa y proyecto. Todo KPI se calcula "a la fecha de corte"; por eso se puede recalcular el pasado.
- La función devuelve un `Valor` (número y una nota corta). Si devuelve `None`, la pantalla muestra "sin datos".
- `direccion` y los umbrales definen el semáforo: con `mayor`, un valor `>= umbral_alerta` está **en meta**, entre ambos umbrales está en **atención** y por debajo del crítico está **crítico**. Con `menor` es al revés. Con `ninguna` es informativo.
- Los umbrales se pueden cambiar sin tocar código en el administrador de Django (**Configuración de KPI**).
- Si un KPI falla por un dato inesperado, la tarjeta muestra "Error" y el resto de la pantalla sigue funcionando; el detalle queda en el registro del servidor.
- `resumen=True` hace que el KPI aparezca también en la pestaña de Resumen.

### Ejemplo trazado: SPI y CPI de un proyecto

Definiciones (todo en soles **sin IGV**; ver `apps/proyectos/services.py`):

| Concepto               | Cálculo                                                                                  |
|------------------------|------------------------------------------------------------------------------------------|
| BAC de costo           | Costo de obra del escenario *Meta 70 %* sin IGV                                          |
| % planificado / % real | Valorización planificada / real **acumulada de los meses cerrados** ÷ monto del contrato |
| PV, EV                 | % planificado × BAC, % real × BAC                                                        |
| AC                     | Gastos reales y pagados de los componentes 01, 02 y 05, sin IGV, hasta la fecha de corte |
| SPI, CPI               | EV ÷ PV, EV ÷ AC                                                                         |
| EAC y margen           | EAC = BAC ÷ CPI; margen = (contrato sin IGV − EAC) ÷ contrato sin IGV                    |

Con un contrato de 1,180,000 (1,000,000 sin IGV), BAC = 700,000, avance real 33.9 % y gasto de 200,000: EV = 237,288 y CPI = 1.19. Esta prueba está en `apps/core/tests/test_kpis_areas.py`.

Estas definiciones son **supuestos** (preguntas P-01 a P-04 de `docs/parte1/08_preguntas_clave.md`); al cambiarlas basta editar `services.py` y las pruebas.

El listado completo de indicadores, con fórmula, fuente y umbrales, está en [diccionario_kpi.md](diccionario_kpi.md) y en la pantalla **Diccionario de KPI**. Se regenera con `python manage.py generar_diccionario_kpi`.

## 5. Cómo se actualizan los datos

Hoy la actualización es **manual**; está diseñada para pasar a automática sin cambiar nada más.

| Vía                       | Quién                        | Cómo                                                                                           |
|---------------------------|------------------------------|------------------------------------------------------------------------------------------------|
| Pantalla **Cargar datos** | Cada oficina                 | Elige la tabla, sube el archivo limpio (`.csv`/`.xlsx`), marca *Solo validar* si quiere probar |
| Comando                   | Equipo del cuadro de mando   | `python manage.py importar_archivo proyectos_gastos archivo.csv`                               |
| API                       | Un script o sistema (futuro) | `POST /api/v1/cargas/<tabla>/` con el archivo o con filas JSON                                 |

Las tres usan la misma función (`importers.procesar`), así que las reglas son idénticas:

1. Se leen **todas** las filas y se validan: tipos, listas cerradas (estados, monedas), claves foráneas por código (centro de costo, proveedor, DNI), claves repetidas.
2. Si hay **un solo error no se guarda nada** y se devuelve la lista (fila, columna, problema).
3. Si todo está bien, se guarda en una transacción: inserta las filas nuevas y **actualiza** las existentes (misma clave), por lo que se puede volver a cargar un archivo corregido sin duplicar.
4. Queda registrada la carga (quién, cuándo, cuántas filas, errores) y se muestra en **Calidad de datos**.

Las 20 tablas de carga y sus columnas están en `apps/*/importers.py` y corresponden a `docs/parte1/07_archivos_limpios.md`. Las plantillas se generan con `python manage.py exportar_plantillas` (carpeta `exports/`, ignorada por Git) o se descargan en la pantalla de carga.

Después de cargar datos se recalcula el historial con `python manage.py calcular_kpis --corte AAAA-MM-DD --historial 6`, que guarda el valor de cada KPI por fecha de corte (tabla `KPISnapshot`) y alimenta los gráficos de evolución.

Orden recomendado de carga: catálogos (`cat_*`) → proveedores → proyectos y presupuestos → resto.

## 6. Seguridad y accesos

- Todas las pantallas exigen iniciar sesión. Cada área la ve el grupo con su nombre; el grupo `gerencia` ve todo. Los grupos se crean con `python manage.py crear_grupos` (se ejecuta en cada despliegue).
- La pantalla de RR. HH. muestra solo **agregados** (sin nombres ni sueldos individuales). Los datos personales (nombre, DNI) existen en la base solo porque la planilla los necesita; el diseño no exige cuentas bancarias ni datos familiares.
- Producción: `DJANGO_DEBUG=0`, clave secreta propia, HTTPS forzado, cookies seguras. Los usuarios de ejemplo **no** se crean en producción.
- La API usa token por usuario (`python manage.py crear_token usuario`) y respeta los mismos permisos por área.

## 7. Cómo escalar

### 7.1 Agregar una oficina nueva (por ejemplo, Almacén)

1. `mkdir apps/almacen` y copiar el molde de otra app (`apps.py`, `models.py`, `kpis.py`, `dashboard.py`, `importers.py`).
2. **Modelos**: definir las tablas. Para enlazar con otras áreas, usar el **código** (CC2, RUC, N.º de orden) y, si hace falta, una clave foránea a los catálogos de `core` (`Empresa`, `CentroCosto`, `Categoria`).
3. **KPI**: escribir funciones con `@kpi(area="almacen", ...)` (sección 4).
4. **Pestaña**: en `dashboard.py` una función `construir(ctx)` que devuelva `ContenidoArea(graficos=[...], tablas=[...])`.
5. **Cargas**: en `importers.py` declarar `Importador(...)` con sus columnas.
6. **Registro**: en `apps.py`, dentro de `ready()`, importar `kpis` y llamar a `registrar_area(AreaDashboard(slug="almacen", ...))`.
7. Agregar `"apps.almacen"` a `INSTALLED_APPS`, ejecutar `makemigrations almacen` y `migrate`, y `crear_grupos` (crea el grupo `almacen`).

No hay que tocar plantillas, URLs, menú, permisos, API ni diccionario de KPI: aparecen solos. Las pruebas de un área nueva siguen el patrón de `apps/core/tests/test_kpis_areas.py`.

### 7.2 Agregar o cambiar un KPI

- Nuevo: una función `@kpi` en `kpis.py` del área, más una prueba con datos que se puedan calcular a mano. Regenerar el diccionario.
- Cambiar umbrales o metas: administrador → *Configuración de KPI* (no requiere despliegue).
- Cambiar una definición (por ejemplo, el alcance del costo real): `services.py` del área y, para parámetros de negocio, `settings.CUADRO_MANDO` (IGV, componentes de obra, hora de entrada, tolerancia).

### 7.3 Pasar de carga manual a automática

| Etapa     | Qué cambia                                                                                                                                           |
|-----------|------------------------------------------------------------------------------------------------------------------------------------------------------|
| Hoy       | Una persona sube el archivo en **Cargar datos**                                                                                                      |
| Siguiente | Un script (cron local o *cron job* de Railway) lee la carpeta compartida y llama a la API o al comando `importar_archivo`, y luego a `calcular_kpis` |
| Después   | Un conector por oficina (consulta a su sistema o base) genera el mismo DataFrame y llama a `importers.procesar`. El resto del sistema no cambia      |

Las reglas de validación, el registro de cargas y los KPI son los mismos en cualquier etapa.

### 7.4 Si crecen los datos o los usuarios

- Los índices ya cubren los filtros más usados; si una consulta se vuelve lenta, revisar con `EXPLAIN` y añadir índices en `Meta.indexes`.
- Los KPI se calculan al abrir la pantalla; si tardan, usar `KPISnapshot` (ya existe) para mostrar el último cálculo guardado y recalcular solo con `calcular_kpis`.
- Los cálculos pesados pueden pasar a vistas materializadas de PostgreSQL o a tareas en segundo plano (Celery/cron) sin cambiar las pantallas.
- Cuando haya más de un módulo operativo (como el de RR. HH. de la contrapropuesta), cada app puede ir a **su propia base** en el mismo servidor y comunicarse por la API v1; los códigos estables ya están previstos para eso.

## 8. Despliegue en Railway

1. Subir el código (sin datos reales) a un repositorio y crear un proyecto en Railway desde él.
2. Agregar el plugin **PostgreSQL**; Railway inyecta `DATABASE_URL`.
3. Definir variables del servicio: `DJANGO_DEBUG=0`, `DJANGO_SECRET_KEY` (valor largo y aleatorio), `DJANGO_ALLOWED_HOSTS` (el dominio asignado; `RAILWAY_PUBLIC_DOMAIN` se agrega solo).
4. `railway.json` ya define la construcción (`collectstatic`), el arranque (`migrate`, `crear_grupos`, `gunicorn`) y la verificación de salud en `/salud/`.
5. Crear el primer usuario desde la consola de Railway: `python manage.py createsuperuser`, y luego los usuarios por área desde el administrador (`/admin/`).
6. Cargar los catálogos y archivos limpios reales con la pantalla de carga o la API. **No** ejecutar `cargar_demo` en producción.

Pendiente antes de producción: política de acceso aprobada por la empresa, confirmación de dónde pueden almacenarse datos de planillas y deuda, y copia de seguridad periódica de la base.

## 9. Datos de ejemplo y límites actuales

- `cargar_demo` genera 8 proyectos, 1,648 requerimientos, 1,144 órdenes, 1,119 comprobantes, 21 préstamos, 117 personas y 1,559 marcaciones, con proporciones tomadas del análisis de la Parte 1 (por ejemplo, 55 % de RQ de emergencia, 19 % de ítems con precio, pagarés grandes en diciembre). Se reproducen con `--semilla`.
- Supuestos que faltan validar: ver [informe_final.md](informe_final.md), sección 5.
- No incluido: detalle por partida de presupuesto y valorización (solo totales por escenario y mes), ingresos distintos de las valorizaciones, parámetros legales de planilla por vigencia y el formato de PLAME.

## 10. Paleta de colores

Definida en `static/css/dph.css` (variables CSS) y en `apps/core/theme.py` (gráficos).

| Uso                                        | Color                 |
|--------------------------------------------|-----------------------|
| Primario (encabezados, series principales) | `#0B3C5D`             |
| Secundario                                 | `#1D6FA5`             |
| Acento (resalte, atención leve)            | `#F2A900`             |
| Fondo                                      | `#F4F6F8`             |
| En meta                                    | `#2E9E6B`             |
| Atención                                   | `#F2A900`             |
| Crítico                                    | `#D64545`             |
| Informativo / sin datos                    | `#6B7785` / `#B8C0CC` |
