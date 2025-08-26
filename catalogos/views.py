# catalogos/views.py
from __future__ import annotations

from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import filters, permissions, viewsets

from core.permissions import IsCatalogAdminOrReadOnly
from .models import Departamento, Puesto
from .serializers import DepartamentoSerializer, PuestoSerializer


def _truthy(val: str | None) -> bool:
    """Convierte query params a booleano (1/true/yes/y/t)."""
    if val is None:
        return False
    return str(val).strip().lower() in {"1", "true", "t", "yes", "y"}


class BaseCatalogoViewSet(viewsets.ModelViewSet):
    """Base con permisos, filtros y orden por defecto."""
    # IsCatalogAdminOrReadOnly ya exige autenticación en lecturas
    permission_classes = [IsCatalogAdminOrReadOnly]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    ordering = ["id"]


@extend_schema(tags=["Catálogos"])
class DepartamentoViewSet(BaseCatalogoViewSet):
    """
    CRUD de departamentos.
    Por defecto muestra solo registros vivos (no borrados lógicamente).
    Usa `?include_deleted=1` para incluir también los borrados.
    """
    # Para documentación; el queryset real se construye en get_queryset
    queryset = Departamento.objects.all()
    serializer_class = DepartamentoSerializer

    search_fields = ["nombre", "clave"]
    filterset_fields = ["activo"]
    ordering_fields = ["id", "nombre", "clave", "created", "updated", "created_at", "updated_at"]

    def get_queryset(self) -> QuerySet[Departamento]:
        include_deleted = _truthy(self.request.query_params.get("include_deleted"))
        base = Departamento.all_objects if include_deleted else Departamento.objects
        return base.all()


@extend_schema(tags=["Catálogos"])
class PuestoViewSet(BaseCatalogoViewSet):
    """
    CRUD de puestos.
    Por defecto muestra solo registros vivos (no borrados lógicamente).
    Usa `?include_deleted=1` para incluir también los borrados.
    """
    # Para documentación; el queryset real se construye en get_queryset
    queryset = Puesto.objects.select_related("departamento").all()
    serializer_class = PuestoSerializer

    search_fields = ["nombre", "clave", "departamento__nombre"]
    filterset_fields = ["activo", "departamento"]
    ordering_fields = ["id", "nombre", "clave", "departamento", "created", "updated", "created_at", "updated_at"]

    def get_queryset(self) -> QuerySet[Puesto]:
        include_deleted = _truthy(self.request.query_params.get("include_deleted"))
        base = Puesto.all_objects if include_deleted else Puesto.objects
        return base.select_related("departamento").all()
