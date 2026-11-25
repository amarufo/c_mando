"""Crea (o muestra) el token de API de un usuario, para que un script programado pueda cargar archivos."""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from rest_framework.authtoken.models import Token


class Command(BaseCommand):
    help = "python manage.py crear_token <usuario>"

    def add_arguments(self, parser):
        parser.add_argument("usuario")

    def handle(self, *args, usuario, **opciones):
        try:
            u = get_user_model().objects.get(username=usuario)
        except get_user_model().DoesNotExist:
            raise CommandError(f"No existe el usuario {usuario}")
        token, _ = Token.objects.get_or_create(user=u)
        self.stdout.write(token.key)
