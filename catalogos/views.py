# catalogos/views.py
from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import filters, permissions, viewsets

from .models import Departamento, Puesto
from .serializers import DepartamentoSerializer, PuestoSerializer


class BaseViewSet(viewsets.ModelViewSet):
    """Base con permisos, filtros y orden por defecto."""

    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    ordering = ["id"]


@extend_schema(tags=["Catálogos"])
class DepartamentoViewSet(BaseViewSet):
    """
    CRUD de departamentos.
    Por defecto muestra solo registros activos (no borrados lógicamente).
    Usa `?include_deleted=1` para incluir también los borrados.
    """

    serializer_class = DepartamentoSerializer
    search_fields = ["nombre", "clave"]
    filterset_fields = ["activo"]
    ordering_fields = ["id", "nombre", "clave", "created_at", "updated_at"]

    def get_queryset(self) -> QuerySet[Departamento]:
        include_deleted = self.request.query_params.get("include_deleted")
        qs = (
            Departamento.all_objects.all()
            if include_deleted
            else Departamento.objects.all()
        )
        return qs


@extend_schema(tags=["Catálogos"])
class PuestoViewSet(BaseViewSet):
    """
    CRUD de puestos.
    Por defecto muestra solo registros activos (no borrados lógicamente).
    Usa `?include_deleted=1` para incluir también los borrados.
    """

    serializer_class = PuestoSerializer
    search_fields = ["nombre", "clave", "departamento__nombre"]
    filterset_fields = ["activo", "departamento"]
    ordering_fields = [
        "id",
        "nombre",
        "clave",
        "departamento",
        "created_at",
        "updated_at",
    ]

    def get_queryset(self) -> QuerySet[Puesto]:
        include_deleted = self.request.query_params.get("include_deleted")
        base = Puesto.all_objects if include_deleted else Puesto.objects
        return base.select_related("departamento").all()
