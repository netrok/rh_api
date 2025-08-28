# catalogos/admin.py
from __future__ import annotations

from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import Departamento, Puesto, Turno, Horario


class SoftDeleteAdminMixin:
    """Acciones comunes para modelos con SoftDeleteModel."""
    actions = ("soft_delete_selected", "restore_selected", "hard_delete_selected")

    def soft_delete_selected(self, request, queryset):
        # Soft delete en lote (usa SoftDeleteQuerySet.delete)
        count = queryset.delete()
        self.message_user(request, f"Registros marcados como borrados: {count}")
    soft_delete_selected.short_description = "Borrar lógicamente seleccionados"

    def restore_selected(self, request, queryset):
        # Restaura en lote (usa SoftDeleteQuerySet.restore)
        count = queryset.restore()
        self.message_user(request, f"Registros restaurados: {count}")
    restore_selected.short_description = "Restaurar seleccionados"

    def hard_delete_selected(self, request, queryset):
        # Borrado físico en lote (usa SoftDeleteQuerySet.hard_delete)
        count = queryset.hard_delete()
        self.message_user(request, f"Registros eliminados físicamente: {count}")
    hard_delete_selected.short_description = "Eliminar físicamente seleccionados"


@admin.register(Departamento)
class DepartamentoAdmin(SoftDeleteAdminMixin, SimpleHistoryAdmin):
    list_display = ("id", "nombre", "clave", "activo", "deleted_at")
    search_fields = ("nombre", "clave")
    list_filter = ("activo",)
    ordering = ("nombre",)

    # Mostrar vivos y borrados
    def get_queryset(self, request):
        return Departamento.all_objects.all()


@admin.register(Puesto)
class PuestoAdmin(SoftDeleteAdminMixin, SimpleHistoryAdmin):
    list_display = ("id", "nombre", "clave", "departamento", "activo", "deleted_at")
    search_fields = ("nombre", "clave", "departamento__nombre")
    list_filter = ("activo", "departamento")
    ordering = ("nombre",)
    autocomplete_fields = ("departamento",)
    list_select_related = ("departamento",)

    def get_queryset(self, request):
        return Puesto.all_objects.select_related("departamento").all()


@admin.register(Turno)
class TurnoAdmin(SoftDeleteAdminMixin, SimpleHistoryAdmin):
    list_display = ("id", "nombre", "clave", "activo", "deleted_at")
    search_fields = ("nombre", "clave")  # necesario para autocomplete
    list_filter = ("activo",)
    ordering = ("nombre",)

    def get_queryset(self, request):
        return Turno.all_objects.all()


@admin.register(Horario)
class HorarioAdmin(SoftDeleteAdminMixin, SimpleHistoryAdmin):
    list_display = ("id", "nombre", "clave", "activo", "deleted_at")
    search_fields = ("nombre", "clave")  # necesario para autocomplete
    list_filter = ("activo",)
    ordering = ("nombre",)

    def get_queryset(self, request):
        return Horario.all_objects.all()
