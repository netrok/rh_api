from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import Empleado


@admin.register(Empleado)
class EmpleadoAdmin(SimpleHistoryAdmin):
    list_display = (
        "id",
        "num_empleado",
        "apellido_paterno",
        "apellido_materno",
        "nombres",
        "departamento",
        "puesto",
        "activo",
        "deleted_at",
    )
    list_filter = ("departamento", "puesto", "activo", "genero", "estado_civil")
    search_fields = (
        "num_empleado",
        "nombres",
        "apellido_paterno",
        "apellido_materno",
        "email",
        "curp",
        "rfc",
        "nss",
    )
    ordering = ("num_empleado",)

    # Mostrar también registros con borrado lógico
    def get_queryset(self, request):
        return Empleado.all_objects.select_related("departamento", "puesto").all()

    # Acciones en admin
    actions = (
        "soft_delete_selected",
        "restore_selected",
        "hard_delete_selected",
    )

    def soft_delete_selected(self, request, queryset):
        for obj in queryset:
            obj.delete()

    soft_delete_selected.short_description = "Borrar lógicamente seleccionados"

    def restore_selected(self, request, queryset):
        for obj in queryset:
            obj.restore()

    restore_selected.short_description = "Restaurar seleccionados"

    def hard_delete_selected(self, request, queryset):
        for obj in queryset:
            obj.hard_delete()

    hard_delete_selected.short_description = "Eliminar definitivamente seleccionados"
