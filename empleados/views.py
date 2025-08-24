from django.db import models
from django.http import HttpResponse
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from django_filters import rest_framework as filters
from openpyxl import Workbook

from .models import Empleado
from .serializers import EmpleadoSerializer


class EmpleadoFilter(filters.FilterSet):
    q = filters.CharFilter(method='filter_q')
    activo = filters.BooleanFilter()
    # Filtros por FK (id) y por nombre del catálogo
    departamento = filters.NumberFilter(field_name='departamento_id')
    puesto = filters.NumberFilter(field_name='puesto_id')
    departamento_nombre = filters.CharFilter(field_name='departamento__nombre', lookup_expr='icontains')
    puesto_nombre = filters.CharFilter(field_name='puesto__nombre', lookup_expr='icontains')
    genero = filters.CharFilter(lookup_expr='iexact')
    # Mostrar solo borrados lógicos si deleted=true
    deleted = filters.BooleanFilter(method='filter_deleted')

    class Meta:
        model = Empleado
        fields = [
            'activo', 'departamento', 'puesto', 'genero',
            'departamento_nombre', 'puesto_nombre', 'deleted'
        ]

    def filter_q(self, queryset, name, value):
        return queryset.filter(
            models.Q(num_empleado__icontains=value) |
            models.Q(nombres__icontains=value) |
            models.Q(apellido_paterno__icontains=value) |
            models.Q(apellido_materno__icontains=value) |
            models.Q(email__icontains=value) |
            models.Q(curp__icontains=value) |
            models.Q(rfc__icontains=value) |
            models.Q(nss__icontains=value) |
            models.Q(departamento__nombre__icontains=value) |
            models.Q(puesto__nombre__icontains=value)
        )

    def filter_deleted(self, queryset, name, value: bool):
        # Preserva el queryset base (que puede incluir vivos+muertos si include_deleted=1)
        if value is True:
            return queryset.filter(deleted_at__isnull=False)
        if value is False:
            return queryset.filter(deleted_at__isnull=True)
        return queryset


class EmpleadoViewSet(viewsets.ModelViewSet):
    serializer_class = EmpleadoSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = EmpleadoFilter
    search_fields = [
        'num_empleado', 'nombres', 'apellido_paterno', 'apellido_materno',
        'email', 'departamento__nombre', 'puesto__nombre'
    ]
    ordering_fields = ['num_empleado', 'fecha_ingreso', 'apellido_paterno', 'created_at']
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        """
        Por default devuelve solo registros vivos (soft delete excluido).
        Si pasas ?include_deleted=1 entonces parte de todos (vivos + borrados).
        Luego puedes combinar con ?deleted=true para ver solo borrados.
        """
        include_deleted = self.request.query_params.get('include_deleted')
        base = Empleado.all_objects if include_deleted else Empleado.objects
        return base.select_related('departamento', 'puesto').all().order_by('num_empleado')

    # ----- Acciones personalizadas -----

    @action(detail=True, methods=['post'], url_path='soft-delete')
    def soft_delete(self, request, pk=None):
        obj = self.get_object()
        obj.delete()  # soft delete
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'], url_path='restore')
    def restore(self, request, pk=None):
        obj = self.get_object()
        obj.restore()
        return Response(self.get_serializer(obj).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='history')
    def history(self, request, pk=None):
        obj = self.get_object()
        records = []
        for h in obj.history.select_related('history_user').order_by('-history_date'):
            records.append({
                'history_id': h.pk,
                'history_date': h.history_date.isoformat(),
                'history_user': str(h.history_user) if h.history_user else None,
                'history_type': h.history_type,  # '+' creado, '~' modificado, '-' borrado
                'num_empleado': h.num_empleado,
                'nombres': h.nombres,
                'apellidos': f'{h.apellido_paterno} {h.apellido_materno}'.strip(),
                'departamento_id': h.departamento_id,
                'puesto_id': h.puesto_id,
                'activo': h.activo,
                'deleted_at': h.deleted_at.isoformat() if h.deleted_at else None,
            })
        return Response(records)

    @action(detail=False, methods=['get'], url_path='export-excel')
    def export_excel(self, request):
        qs = self.filter_queryset(self.get_queryset())

        wb = Workbook()
        ws = wb.active
        ws.title = 'Empleados'

        headers = [
            'ID', 'Num Empleado', 'Nombres', 'Apellido Paterno', 'Apellido Materno',
            'Email', 'Género', 'Estado Civil', 'Departamento', 'Puesto',
            'Fecha Nacimiento', 'Fecha Ingreso', 'Activo', 'Eliminado', 'Creado', 'Actualizado'
        ]
        ws.append(headers)

        for e in qs:
            ws.append([
                e.id, e.num_empleado, e.nombres, e.apellido_paterno, e.apellido_materno,
                e.email, e.get_genero_display(), e.get_estado_civil_display(),
                e.departamento.nombre if e.departamento else '',
                e.puesto.nombre if e.puesto else '',
                e.fecha_nacimiento.isoformat() if e.fecha_nacimiento else '',
                e.fecha_ingreso.isoformat() if e.fecha_ingreso else '',
                'Sí' if e.activo else 'No',
                e.deleted_at.isoformat() if e.deleted_at else '',
                e.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                e.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            ])

        resp = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        resp['Content-Disposition'] = 'attachment; filename=empleados.xlsx'
        wb.save(resp)
        return resp
