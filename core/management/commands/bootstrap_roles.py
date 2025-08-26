# core/management/commands/bootstrap_roles.py
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.db import transaction

"""
Crea/actualiza grupos y asigna permisos por modelo.

Incluye:
- Grupos legacy: RH_VIEWER, RH_EDITOR, RH_ADMIN
- Grupos actuales: SuperAdmin, Admin, RRHH, Gerente, Supervisor, Usuario

Permisos estándar que se intentan asignar por modelo:
- view_<model>, add_<model>, change_<model>, delete_<model>

Permisos opcionales (si existen en Meta.permissions):
- soft_delete_<model>, restore_<model>, export_<model>, export_excel_<model>

Ejecuta después de migraciones:
    python manage.py migrate
    python manage.py bootstrap_roles
"""

# Modelos objetivo (app_label, model in lowercase)
MODELS = [
    ("catalogos", "departamento"),
    ("catalogos", "puesto"),
    ("empleados", "empleado"),
]

# Matriz de grupos → acciones estándar
GROUP_MATRIX = {
    # Legacy
    "RH_VIEWER": ["view"],
    "RH_EDITOR": ["view", "add", "change"],  # sin delete
    "RH_ADMIN":  ["view", "add", "change", "delete"],

    # Actual (alineado con core.permissions)
    "SuperAdmin": ["view", "add", "change", "delete"],
    "Admin":      ["view", "add", "change", "delete"],
    "RRHH":       ["view", "add", "change"],
    "Gerente":    ["view"],
    "Supervisor": ["view"],
    "Usuario":    ["view"],
}

# Acciones opcionales por si definiste permisos custom en Meta.permissions
OPTIONAL_ACTIONS = ["soft_delete", "restore", "export", "export_excel"]


class Command(BaseCommand):
    help = "Crea/actualiza grupos y asigna permisos por modelo (legacy + actuales)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Muestra lo que haría sin modificar nada.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        dry = options.get("dry_run", False)

        created_groups = 0
        updated_links = 0
        warnings = 0

        def log(msg, style=None):
            if dry:
                msg = f"[DRY-RUN] {msg}"
            if style:
                self.stdout.write(style(msg))
            else:
                self.stdout.write(msg)

        # Crea/actualiza grupos
        for group_name, actions in GROUP_MATRIX.items():
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                created_groups += 1
                log(f"Grupo creado: {group_name}", self.style.SUCCESS)
            else:
                log(f"Grupo existente: {group_name}")

            # Por cada modelo, asigna permisos estándar y opcionales si existen
            for app_label, model in MODELS:
                try:
                    ct = ContentType.objects.get(app_label=app_label, model=model)
                except ContentType.DoesNotExist:
                    warnings += 1
                    log(
                        f"ContentType no encontrado: {app_label}.{model}. "
                        f"¿Ejecutaste 'migrate'?",
                        self.style.WARNING,
                    )
                    continue

                # Estándar
                wanted_codes = [f"{act}_{model}" for act in actions]

                # Opcionales si existen
                for opt in OPTIONAL_ACTIONS:
                    codename = f"{opt}_{model}"
                    if Permission.objects.filter(codename=codename, content_type=ct).exists():
                        wanted_codes.append(codename)

                for code in wanted_codes:
                    try:
                        perm = Permission.objects.get(codename=code, content_type=ct)
                    except Permission.DoesNotExist:
                        # No hacemos ruido por opcionales; avisamos por estándar faltante
                        if code.split("_", 1)[0] in {"view", "add", "change", "delete"}:
                            warnings += 1
                            log(
                                f"Permiso estándar no encontrado: {code} ({app_label}.{model})",
                                self.style.WARNING,
                            )
                        continue

                    if not group.permissions.filter(pk=perm.pk).exists():
                        if not dry:
                            group.permissions.add(perm)
                        updated_links += 1
                        log(f"  + {group_name} ← {perm.codename} ({app_label}.{model})")

        # Resumen
        if created_groups == 0 and updated_links == 0 and warnings == 0:
            log("Nada que hacer. Grupos y permisos ya estaban al día.")

        log(
            f"Resumen → grupos_creados={created_groups}, permisos_asignados={updated_links}, advertencias={warnings}",
            self.style.SUCCESS,
        )

        if dry:
            log("No se realizaron cambios por --dry-run.", self.style.NOTICE)
