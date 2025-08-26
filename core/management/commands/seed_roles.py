# core/management/commands/seed_roles.py
from __future__ import annotations

from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.db import transaction

ROLES = ("SuperAdmin", "Admin", "RRHH", "Supervisor", "Gerente", "Usuario")


class Command(BaseCommand):
    help = "Crea (si no existen) los grupos base de roles."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Muestra lo que haría sin crear nada.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        dry = bool(options.get("dry_run"))
        created = 0
        existing = 0

        def log_ok(msg: str):
            self.stdout.write(self.style.SUCCESS(msg) if not dry else f"[DRY-RUN] {msg}")

        def log_info(msg: str):
            self.stdout.write(msg if not dry else f"[DRY-RUN] {msg}")

        for name in ROLES:
            if dry:
                # Simula el alta sin tocar la DB
                log_info(f"Crearía grupo: {name} (si no existe)")
                continue

            group, was_created = Group.objects.get_or_create(name=name)
            if was_created:
                created += 1
                log_ok(f"✓ Grupo creado: {name}")
            else:
                existing += 1
                log_info(f"• Grupo existente: {name}")

        if dry:
            self.stdout.write(self.style.NOTICE("No se realizaron cambios (dry-run)."))
        else:
            self.stdout.write(self.style.SUCCESS(
                f"Resumen → creados={created}, existentes={existing}, total={created + existing}"
            ))
