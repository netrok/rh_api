# catalogos/views.py
from __future__ import annotations

from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import filters as drf_filters, viewsets

from core.permissions import IsCatalogAdminOrReadOnly
from .models import Departamento, Puesto, Turno, Horario
from .serializers import (
    DepartamentoSerializer,
    PuestoSerializer,
    TurnoSerializer,
    HorarioSerializer,
)


def _truthy(val: str | None) -> bool:
    """Convierte query params a booleano (1/true/yes/y/t)."""
    if val is None:
        return False
    return str(val).strip().lower() in {"1", "true", "t", "yes", "y"}


class BaseCatalogoViewSet(viewsets.ModelViewSet):
    """Base con permisos, filtros y orden por defecto."""
    permission_classes = [IsCatalogAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    ordering = ["id"]


# ──────────────────────────────────────────────────────────────────────────────
# Departamento
# ──────────────────────────────────────────────────────────────────────────────
@extend_schema(tags=["Catálogos"])
class DepartamentoViewSet(BaseCatalogoViewSet):
    serializer_class = DepartamentoSerializer
    search_fields = ["nombre", "clave"]
    filterset_fields = ["activo"]
    ordering_fields = ["id", "nombre", "clave", "created_at", "updated_at"]

    def get_queryset(self) -> QuerySet[Departamento]:
        include_deleted = _truthy(self.request.query_params.get("include_deleted"))
        base = getattr(Departamento, "all_objects", None) if include_deleted else Departamento.objects
        return (base or Departamento.objects).all()


# ──────────────────────────────────────────────────────────────────────────────
# Puesto
# ──────────────────────────────────────────────────────────────────────────────
@extend_schema(tags=["Catálogos"])
class PuestoViewSet(BaseCatalogoViewSet):
    serializer_class = PuestoSerializer
    search_fields = ["nombre", "clave", "departamento__nombre"]
    filterset_fields = ["activo", "departamento"]
    ordering_fields = ["id", "nombre", "clave", "departamento", "created_at", "updated_at"]

    def get_queryset(self) -> QuerySet[Puesto]:
        include_deleted = _truthy(self.request.query_params.get("include_deleted"))
        base = getattr(Puesto, "all_objects", None) if include_deleted else Puesto.objects
        return (base or Puesto.objects).select_related("departamento").all()


# ──────────────────────────────────────────────────────────────────────────────
# Turno
# ──────────────────────────────────────────────────────────────────────────────
@extend_schema(tags=["Catálogos"])
class TurnoViewSet(BaseCatalogoViewSet):
    serializer_class = TurnoSerializer
    search_fields = ["nombre", "clave"]
    filterset_fields = ["activo"]
    ordering_fields = ["id", "nombre", "clave", "created_at", "updated_at"]

    def get_queryset(self) -> QuerySet[Turno]:
        include_deleted = _truthy(self.request.query_params.get("include_deleted"))
        base = getattr(Turno, "all_objects", None) if include_deleted else Turno.objects
        return (base or Turno.objects).all()


# ──────────────────────────────────────────────────────────────────────────────
# Horario
# ──────────────────────────────────────────────────────────────────────────────
@extend_schema(tags=["Catálogos"])
class HorarioViewSet(BaseCatalogoViewSet):
    serializer_class = HorarioSerializer
    search_fields = ["nombre", "clave"]
    filterset_fields = ["activo"]
    ordering_fields = ["id", "nombre", "clave", "created_at", "updated_at"]

    def get_queryset(self) -> QuerySet[Horario]:
        include_deleted = _truthy(self.request.query_params.get("include_deleted"))
        base = getattr(Horario, "all_objects", None) if include_deleted else Horario.objects
        return (base or Horario.objects).all()
