"""Carga datos de ejemplo (aleatorios, reproducibles) en todas las áreas y calcula el historial de KPI.

Uso:  python manage.py cargar_demo [--semilla 2026] [--limpiar]
"""

import os
import random

import pandas as pd
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.core import importers
from apps.core.demo import CORTE_DEMO, generar_catalogos
from apps.core.models import (
    CargaArchivo,
    Categoria,
    CentroCosto,
    Empresa,
    KPIConfig,
    KPISnapshot,
    TipoCambio,
)
from apps.logistica import demo as demo_logistica
from apps.logistica.models import Comprobante, Orden, Proveedor, Requerimiento
from apps.prestamos import demo as demo_prestamos
from apps.prestamos.models import Cuota, PagoCuota, Prestamo
from apps.proyectos import demo as demo_proyectos
from apps.proyectos.models import Gasto, PresupuestoEscenario, Proyecto, Valorizacion
from apps.rrhh import demo as demo_rrhh
from apps.rrhh.models import (
    CostoProyectoMes,
    Marcacion,
    Obligacion,
    Persona,
    PlanillaMes,
)

# Orden de borrado: primero las tablas que dependen de otras.
TABLAS = [
    PagoCuota,
    Cuota,
    Prestamo,
    Comprobante,
    Orden,
    Requerimiento,
    Proveedor,
    Gasto,
    Valorizacion,
    PresupuestoEscenario,
    Proyecto,
    Marcacion,
    PlanillaMes,
    CostoProyectoMes,
    Obligacion,
    Persona,
    KPISnapshot,
    CargaArchivo,
    TipoCambio,
    Categoria,
    CentroCosto,
    Empresa,
]


class Command(BaseCommand):
    help = "Genera datos de ejemplo para todas las áreas (no son datos reales)."

    def add_arguments(self, parser):
        parser.add_argument("--semilla", type=int, default=2026)
        parser.add_argument(
            "--limpiar",
            action="store_true",
            help="Borra antes los datos de las áreas (no borra usuarios).",
        )

    @transaction.atomic
    def handle(self, *args, semilla, limpiar, **opciones):
        if Empresa.objects.exists():
            if not limpiar:
                self.stderr.write(
                    "Ya hay datos cargados. Use --limpiar para reemplazarlos por los de ejemplo."
                )
                return
            for modelo in TABLAS:
                modelo.objects.all().delete()
        rng = random.Random(semilla)
        est = generar_catalogos(rng)
        resumen = {}
        for nombre, modulo in (
            ("logistica", demo_logistica),
            ("proyectos", demo_proyectos),
            ("prestamos", demo_prestamos),
            ("rrhh", demo_rrhh),
        ):
            resumen[nombre] = modulo.generar(
                rng, est
            )  # logística va primero: los gastos referencian sus órdenes
            self.stdout.write(f"{nombre}: {resumen[nombre]}")
        self._cargas_de_ejemplo()
        self._metas_por_defecto()
        call_command("crear_grupos", stdout=self.stdout)
        self._usuarios_demo()
        call_command(
            "calcular_kpis",
            corte=CORTE_DEMO.isoformat(),
            historial=6,
            stdout=self.stdout,
        )
        self.stdout.write(self.style.SUCCESS("Datos de ejemplo cargados."))

    def _cargas_de_ejemplo(self):
        """Pasa algunas tablas por el cargador real para que la pestaña de calidad tenga historial (y probar el flujo)."""
        importers.descubrir()
        for slug, limite in (
            ("proyectos_gastos", 200),
            ("rrhh_planilla", 60),
            ("prestamos_pagos", 80),
        ):
            imp = importers.IMPORTADORES[slug]
            importers.procesar(
                imp,
                importers.exportar(imp, limite),
                nombre_archivo=f"{slug}_ejemplo.csv",
            )
        malo = importers.exportar(importers.IMPORTADORES["proyectos_gastos"], 5)
        malo.loc[0, "estado"] = "PAGADA"  # valor fuera del catálogo
        malo.loc[1, "monto"] = "abc"
        importers.procesar(
            importers.IMPORTADORES["proyectos_gastos"],
            malo,
            nombre_archivo="gastos_con_errores.csv",
        )

    def _metas_por_defecto(self):
        """Ejemplo de configuración editable: una meta para el SPI."""
        KPIConfig.objects.update_or_create(codigo="P3", defaults={"meta": 1.0})

    def _usuarios_demo(self):
        """Un usuario por perfil con clave 'demo1234'. Solo en local (DEBUG) o con DEMO_USUARIOS=1: nunca en producción por defecto."""
        if not (settings.DEBUG or os.environ.get("DEMO_USUARIOS") == "1"):
            self.stdout.write(
                "Usuarios de ejemplo no creados (producción). Cree usuarios reales con createsuperuser."
            )
            return
        User = get_user_model()
        for nombre, grupo in (
            ("gerencia", "gerencia"),
            ("rrhh", "rrhh"),
            ("logistica", "logistica"),
            ("proyectos", "proyectos"),
            ("prestamos", "prestamos"),
        ):
            u, creado = User.objects.get_or_create(username=nombre)
            if creado:
                u.set_password("demo1234")
                u.save()
            u.groups.set([Group.objects.get(name=grupo)])
