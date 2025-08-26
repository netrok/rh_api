from typing import Optional

from django.db import models
from django.http import HttpResponse
from django_filters import rest_framework as filters
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from openpyxl import Workbook
from openpyxl.styles import Font
from rest_framework import permissions, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response

from core.permissions import IsEmpleadoEditorOrReadOnly, IsRHAdmin  # <- NUEVO
from .models import Empleado
from .serializers import EmpleadoSerializer


# -----------------------
# Filtros
# -----------------------
class EmpleadoFilter(filters.FilterSet):
    """
    Filtros combinables para Empleado.
    - q: búsqueda amplia (num_empleado, nombre, apellidos, email, curp, rfc, nss, depto, puesto)
    - activo: bool
    - departamento/puesto: por ID
    - departamento_nombre/puesto_nombre: búsqueda por nombre (icontains)
    - genero: 'M' | 'F' | 'O'
    - deleted: True -> solo borrados, False -> solo vivos, None -> sin alterar queryset base
    """

    q = filters.CharFilter(method="filter_q")
    activo = filters.BooleanFilter()
    departamento = filters.NumberFilter(field_name="departamento_id")
    puesto = filters.NumberFilter(field_name="puesto_id")
    departamento_nombre = filters.CharFilter(
        field_name="departamento__nombre", lookup_expr="icontains"
    )
    puesto_nombre = filters.CharFilter(
        field_name="puesto__nombre", lookup_expr="icontains"
    )
    genero = filters.CharFilter(lookup_expr="iexact")
    deleted = filters.BooleanFilter(method="filter_deleted")

    class Meta:
        model = Empleado
        fields = [
            "activo",
            "departamento",
            "puesto",
            "genero",
            "departamento_nombre",
            "puesto_nombre",
            "deleted",
        ]

    def filter_q(self, queryset, name, value):
        return queryset.filter(
            models.Q(num_empleado__icontains=value)
            | models.Q(nombres__icontains=value)
            | models.Q(apellido_paterno__icontains=value)
            | models.Q(apellido_materno__icontains=value)
            | models.Q(email__icontains=value)
            | models.Q(curp__icontains=value)
            | models.Q(rfc__icontains=value)
            | models.Q(nss__icontains=value)
            | models.Q(departamento__nombre__icontains=value)
            | models.Q(puesto__nombre__icontains=value)
        )

    def filter_deleted(self, queryset, name, value: Optional[bool]):
        # No rompemos el queryset base (que puede venir con include_deleted=1)
        if value is True:
            return queryset.filter(deleted_at__isnull=False)
        if value is False:
            return queryset.filter(deleted_at__isnull=True)
        return queryset


# -----------------------
# ViewSet
# -----------------------
@extend_schema(tags=["Empleados"])
class EmpleadoViewSet(viewsets.ModelViewSet):
    """
    CRUD de Empleados con:
    - soft delete / restore
    - history (django-simple-history)
    - exportación a Excel
    - filtros/ordenación/búsqueda
    """

    serializer_class = EmpleadoSerializer
    # Lectura: autenticado; Escritura: RRHH/Admin (controlado por IsEmpleadoEditorOrReadOnly)
    permission_classes = [IsEmpleadoEditorOrReadOnly]
    filterset_class = EmpleadoFilter
    search_fields = [
        "num_empleado",
        "nombres",
        "apellido_paterno",
        "apellido_materno",
        "email",
        "departamento__nombre",
        "puesto__nombre",
    ]
    ordering_fields = [
        "num_empleado",
        "fecha_ingreso",
        "apellido_paterno",
        "created_at",
    ]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        """
        Por defecto devuelve solo registros vivos (excluye soft delete).
        Si pasas ?include_deleted=1, parte de todos (vivos + borrados).
        Combina con ?deleted=true|false para filtrar explícitamente.
        """
        include_deleted = self.request.query_params.get("include_deleted")
        base = Empleado.all_objects if include_deleted else Empleado.objects
        return (
            base.select_related("departamento", "puesto").all().order_by("num_empleado")
        )

    # ── Permisos finos por método/acción ──────────────────────────────────────
    def get_permissions(self):
        # DELETE solo Admin (o superuser)
        if self.request.method == "DELETE":
            return [IsRHAdmin()]
        return super().get_permissions()

    # ---------- Acciones personalizadas ----------

    @extend_schema(
        summary="Soft delete",
        description="Marca el empleado como eliminado lógicamente (no se borra físicamente).",
        responses={204: OpenApiResponse(description="Eliminado lógicamente")},
    )
    @action(detail=True, methods=["post"], url_path="soft-delete", permission_classes=[IsRHAdmin])  # <- SOLO ADMIN
    def soft_delete(self, request: Request, pk: str | None = None) -> Response:
        obj = self.get_object()
        obj.delete()  # soft delete
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        summary="Restaurar",
        description="Restaura un empleado previamente eliminado lógicamente.",
        responses={200: EmpleadoSerializer},
        examples=[OpenApiExample("Restaurado", value={"detail": "ok"})],
    )
    @action(detail=True, methods=["post"], url_path="restore", permission_classes=[IsRHAdmin])  # <- SOLO ADMIN
    def restore(self, request: Request, pk: str | None = None) -> Response:
        obj = self.get_object()
        obj.restore()
        return Response(self.get_serializer(obj).data, status=status.HTTP_200_OK)

    # Serializer para el historial (inline para documentar OpenAPI)
    class _HistoryRecordSerializer(serializers.Serializer):
        history_id = serializers.IntegerField()
        history_date = serializers.DateTimeField()
        history_user = serializers.CharField(allow_null=True)
        history_type = serializers.CharField()  # '+', '~', '-'
        num_empleado = serializers.CharField()
        nombres = serializers.CharField()
        apellidos = serializers.CharField()
        departamento_id = serializers.IntegerField(allow_null=True)
        puesto_id = serializers.IntegerField(allow_null=True)
        activo = serializers.BooleanField()
        deleted_at = serializers.DateTimeField(allow_null=True)

    @extend_schema(
        summary="Historial de cambios",
        description="Devuelve el historial auditado del empleado (django-simple-history).",
        responses={200: OpenApiResponse(response=_HistoryRecordSerializer(many=True))},
        examples=[
            OpenApiExample(
                "Ejemplo",
                value=[
                    {
                        "history_id": 1,
                        "history_date": "2025-08-24T18:00:00Z",
                        "history_user": "admin",
                        "history_type": "+",
                        "num_empleado": "E001",
                        "nombres": "Juan",
                        "apellidos": "Pérez López",
                        "departamento_id": 1,
                        "puesto_id": 2,
                        "activo": True,
                        "deleted_at": None,
                    }
                ],
            )
        ],
    )
    @action(detail=True, methods=["get"], url_path="history")
    def history(self, request: Request, pk: str | None = None) -> Response:
        obj = self.get_object()
        records: list[dict] = []
        for h in obj.history.select_related("history_user").order_by("-history_date"):
            records.append(
                {
                    "history_id": h.pk,
                    "history_date": h.history_date.isoformat(),
                    "history_user": str(h.history_user) if h.history_user else None,
                    "history_type": h.history_type,  # '+' creado, '~' modificado, '-' borrado
                    "num_empleado": h.num_empleado,
                    "nombres": h.nombres,
                    "apellidos": f"{h.apellido_paterno} {h.apellido_materno}".strip(),
                    "departamento_id": h.departamento_id,
                    "puesto_id": h.puesto_id,
                    "activo": h.activo,
                    "deleted_at": h.deleted_at.isoformat() if h.deleted_at else None,
                }
            )
        return Response(records)

    @extend_schema(
        summary="Exportación a Excel",
        description="Descarga un XLSX con el resultado filtrado/ordenado actual.",
        responses={
            (
                200,
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ): OpenApiTypes.BINARY
        },
    )
    @action(detail=False, methods=["get"], url_path="export-excel")
    def export_excel(self, request: Request) -> HttpResponse:
        qs = self.filter_queryset(self.get_queryset())

        wb = Workbook()
        ws = wb.active
        ws.title = "Empleados"

        headers = [
            "ID",
            "Num Empleado",
            "Nombres",
            "Apellido Paterno",
            "Apellido Materno",
            "Email",
            "Género",
            "Estado Civil",
            "Departamento",
            "Puesto",
            "Fecha Nacimiento",
            "Fecha Ingreso",
            "Activo",
            "Eliminado",
            "Creado",
            "Actualizado",
        ]
        ws.append(headers)
        # Estilo cabecera
        for cell in ws[1]:
            cell.font = Font(bold=True)
        ws.freeze_panes = "A2"

        for e in qs:
            ws.append(
                [
                    e.id,
                    e.num_empleado,
                    e.nombres,
                    e.apellido_paterno,
                    e.apellido_materno,
                    e.email,
                    e.get_genero_display(),
                    e.get_estado_civil_display(),
                    e.departamento.nombre if e.departamento else "",
                    e.puesto.nombre if e.puesto else "",
                    e.fecha_nacimiento.isoformat() if e.fecha_nacimiento else "",
                    e.fecha_ingreso.isoformat() if e.fecha_ingreso else "",
                    "Sí" if e.activo else "No",
                    e.deleted_at.isoformat() if e.deleted_at else "",
                    e.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    e.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
                ]
            )

        resp = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        resp["Content-Disposition"] = 'attachment; filename="empleados.xlsx"'
        wb.save(resp)
        return resp
