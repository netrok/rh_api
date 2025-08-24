from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Departamento, Puesto

@admin.register(Departamento)
class DepartamentoAdmin(SimpleHistoryAdmin):
    list_display = ('id', 'nombre', 'clave', 'activo', 'deleted_at')
    search_fields = ('nombre', 'clave')
    list_filter = ('activo',)
    ordering = ('nombre',)

    # Mostrar también los borrados lógicos en el admin
    def get_queryset(self, request):
        return Departamento.all_objects.all()

    # Acciones útiles
    actions = ('soft_delete_selected', 'restore_selected', 'hard_delete_selected',)

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

@admin.register(Puesto)
class PuestoAdmin(SimpleHistoryAdmin):
    list_display = ('id', 'nombre', 'clave', 'departamento', 'activo', 'deleted_at')
    search_fields = ('nombre', 'clave', 'departamento__nombre')
    list_filter = ('activo', 'departamento')
    ordering = ('nombre',)

    def get_queryset(self, request):
        return Puesto.all_objects.select_related('departamento').all()

    actions = ('soft_delete_selected', 'restore_selected', 'hard_delete_selected',)

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
