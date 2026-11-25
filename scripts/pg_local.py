"""PostgreSQL local sin instalación ni permisos de administrador (solo desarrollo).

Usa el paquete `pixeltable-pgserver`, que trae los binarios de PostgreSQL 16 y
levanta un servidor con socket Unix en `c_mando/.pgdata`. En Railway no se usa:
allí la base la provee el plugin PostgreSQL y se lee de `DATABASE_URL`.

Uso (desde `c_mando/`):
    .venv/bin/python3 scripts/pg_local.py start    # inicia (y crea la base la primera vez)
    .venv/bin/python3 scripts/pg_local.py status
    .venv/bin/python3 scripts/pg_local.py stop
"""

import subprocess
import sys
from pathlib import Path

import pixeltable_pgserver as pgserver

PGDATA = Path(__file__).resolve().parent.parent / ".pgdata"
BASE_DATOS = "cuadro_mando"


def iniciar():
    # cleanup_mode=None: el servidor sigue vivo cuando termina este script.
    servidor = pgserver.get_server(PGDATA, cleanup_mode=None)
    existe = servidor.psql(f"select 1 from pg_database where datname = '{BASE_DATOS}';")
    if "1 row" not in str(existe):
        servidor.psql(f'create database "{BASE_DATOS}";')
        print(f"Base '{BASE_DATOS}' creada.")
    print(f"PostgreSQL activo. Socket: {PGDATA}")


def detener():
    ejecutable = Path(pgserver.__file__).parent / "pginstall" / "bin" / "pg_ctl"
    if not ejecutable.exists():
        sys.exit("No se encontró pg_ctl dentro del paquete pgserver.")
    subprocess.run(
        [str(ejecutable), "-D", str(PGDATA), "stop", "-m", "fast"], check=False
    )


def estado():
    ejecutable = Path(pgserver.__file__).parent / "pginstall" / "bin" / "pg_ctl"
    subprocess.run([str(ejecutable), "-D", str(PGDATA), "status"], check=False)


if __name__ == "__main__":
    accion = sys.argv[1] if len(sys.argv) > 1 else "start"
    {"start": iniciar, "stop": detener, "status": estado}.get(accion, iniciar)()
