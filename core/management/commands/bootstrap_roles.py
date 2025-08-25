# core/management/commands/bootstrap_roles.py
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

MODELS = [
    ("catalogos", "departamento"),
    ("catalogos", "puesto"),
    ("empleados", "empleado"),
]

GROUPS = {
    "RH_VIEWER": ["view"],
    "RH_EDITOR": ["view", "add", "change"],  # sin delete
    "RH_ADMIN": ["view", "add", "change", "delete"],
}


class Command(BaseCommand):
    help = "Crea grupos (RH_VIEWER, RH_EDITOR, RH_ADMIN) y asigna permisos por modelo."

    def handle(self, *args, **options):
        created_any = False
        for group_name, actions in GROUPS.items():
            group, g_created = Group.objects.get_or_create(name=group_name)
            if g_created:
                self.stdout.write(self.style.SUCCESS(f"Grupo creado: {group_name}"))
                created_any = True
            for app_label, model in MODELS:
                ct = ContentType.objects.get(app_label=app_label, model=model)
                for act in actions:
                    codename = f"{act}_{model}"
                    try:
                        perm = Permission.objects.get(
                            codename=codename, content_type=ct
                        )
                    except Permission.DoesNotExist:
                        self.stdout.write(
                            self.style.WARNING(
                                f"Permiso no encontrado: {codename} ({app_label}.{model})"
                            )
                        )
                        continue
                    group.permissions.add(perm)
        if not created_any:
            self.stdout.write("Grupos ya existentes; permisos actualizados.")
        self.stdout.write(self.style.SUCCESS("Bootstrap de roles completado."))
