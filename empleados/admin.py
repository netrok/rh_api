# empleados/admin.py
from __future__ import annotations

from django.contrib import admin
from django.utils.html import format_html
from simple_history.admin import SimpleHistoryAdmin

from .models import Empleado


@admin.register(Empleado)
class EmpleadoAdmin(SimpleHistoryAdmin):
    # Listado
    list_display = (
        "thumb",
        "num_empleado",
        "apellidos",
        "nombres",
        "departamento",
        "puesto",
        "activo",
        "deleted_at",
    )
    list_filter = (
        "activo",
        "departamento",
        "puesto",
        "genero",
        "estado_civil",
    )
    search_fields = (
        "num_empleado",
        "nombres",
        "apellido_paterno",
        "apellido_materno",
        "curp",
        "rfc",
        "nss",
        "email",
        "telefono",
        "celular",
    )
    ordering = ("-created_at",)
    list_select_related = ("departamento", "puesto", "turno", "horario")
    autocomplete_fields = ("departamento", "puesto", "turno", "horario")

    # Detalle/edición
    readonly_fields = ("created_at", "updated_at", "deleted_at", "preview_foto")
    fieldsets = (
        ("Básicos", {
            "fields": (
                "num_empleado", "nombres", "apellido_paterno", "apellido_materno",
                "activo", "foto", "preview_foto",
            )
        }),
        ("Personales", {
            "fields": (
                "fecha_nacimiento", "genero", "estado_civil",
                "curp", "rfc", "nss",
                "telefono", "celular", "email",
            )
        }),
        ("Domicilio", {
            "fields": ("calle", "numero", "colonia", "municipio", "estado", "cp")
        }),
        ("Laboral", {
            "fields": (
                "departamento", "puesto", "fecha_ingreso",
                "sueldo", "tipo_contrato", "tipo_jornada",
                "turno", "horario",
            )
        }),
        ("Bancario", {
            "fields": ("banco", "clabe", "cuenta")
        }),
        ("Emergencia / Otros", {
            "fields": (
                "contacto_emergencia_nombre", "contacto_emergencia_parentesco", "contacto_emergencia_telefono",
                "escolaridad", "notas",
            )
        }),
        ("Auditoría", {
            "fields": ("created_at", "updated_at", "deleted_at")
        }),
    )
    date_hierarchy = "created_at"

    # Actions
    actions = ("restore_selected", "hard_delete_selected")

    # Helpers visuales
    def apellidos(self, obj: Empleado) -> str:
        return f"{obj.apellido_paterno} {obj.apellido_materno or ''}".strip()
    apellidos.short_description = "Apellidos"

    def thumb(self, obj: Empleado):
        if obj.foto and hasattr(obj.foto, "url"):
            return format_html('<img src="{}" style="height:36px;width:36px;object-fit:cover;border-radius:50%;">', obj.foto.url)
        return "—"
    thumb.short_description = "Foto"

    def preview_foto(self, obj: Empleado):
        if obj.pk and obj.foto and hasattr(obj.foto, "url"):
            return format_html('<img src="{}" style="max-height:160px;border-radius:8px;">', obj.foto.url)
        return "—"
    preview_foto.short_description = "Vista previa"

    # Soft-delete y restore en lote (usa tu SoftDeleteQuerySet)
    def restore_selected(self, request, queryset):
        # nuestro SoftDeleteQuerySet define .restore()
        restored = queryset.restore()
        self.message_user(request, f"Registros restaurados: {restored}")
    restore_selected.short_description = "Restaurar seleccionados (soft-deleted)"

    def hard_delete_selected(self, request, queryset):
        count = queryset.hard_delete()
        self.message_user(request, f"Registros eliminados físicamente: {count}")
    hard_delete_selected.short_description = "Eliminar físicamente seleccionados"
