from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()

class Command(BaseCommand):
    help = "Asigna un rol (grupo) a un usuario. Crea el grupo si no existe."

    def add_arguments(self, parser):
        parser.add_argument("username", help="Nombre de usuario")
        parser.add_argument("role", help="Nombre del grupo/rol (e.g., Admin, RRHH, Gerente)")

    def handle(self, *args, **opts):
        username = opts["username"]
        role = opts["role"]

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError(f"Usuario no encontrado: {username}")

        group, _ = Group.objects.get_or_create(name=role)
        user.groups.add(group)
        self.stdout.write(self.style.SUCCESS(f"✓ {username} → rol '{role}' asignado"))
