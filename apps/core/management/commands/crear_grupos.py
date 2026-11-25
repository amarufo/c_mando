"""Crea los grupos de usuarios: `gerencia` (ve todo) y uno por área (ve solo su área)."""

from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

from apps.core.dashboard import AREAS, GRUPO_TOTAL


class Command(BaseCommand):
    help = "Crea los grupos de acceso por área. Es idempotente: se puede ejecutar en cada despliegue."

    def handle(self, *args, **opciones):
        nombres = [GRUPO_TOTAL, *AREAS.keys()]
        for nombre in nombres:
            _, creado = Group.objects.get_or_create(name=nombre)
            self.stdout.write(f"{'creado' if creado else 'existe'}: {nombre}")
