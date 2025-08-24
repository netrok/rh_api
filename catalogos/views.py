from rest_framework import viewsets, permissions
from django_filters import rest_framework as filters
from .models import Departamento, Puesto
from .serializers import DepartamentoSerializer, PuestoSerializer

class DepartamentoFilter(filters.FilterSet):
    q = filters.CharFilter(method='filter_q')
    activo = filters.BooleanFilter()

    class Meta:
        model = Departamento
        fields = ['activo']

    def filter_q(self, queryset, name, value):
        return queryset.filter(nombre__icontains=value)

class PuestoFilter(filters.FilterSet):
    q = filters.CharFilter(method='filter_q')
    activo = filters.BooleanFilter()
    departamento = filters.NumberFilter(field_name='departamento_id')

    class Meta:
        model = Puesto
        fields = ['activo', 'departamento']

    def filter_q(self, queryset, name, value):
        return queryset.filter(nombre__icontains=value)

class DepartamentoViewSet(viewsets.ModelViewSet):
    queryset = Departamento.objects.all()
    serializer_class = DepartamentoSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = DepartamentoFilter
    search_fields = ['nombre','clave']
    ordering_fields = ['nombre','created_at','updated_at']
    ordering = ['nombre']

class PuestoViewSet(viewsets.ModelViewSet):
    queryset = Puesto.objects.select_related('departamento').all()
    serializer_class = PuestoSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = PuestoFilter
    search_fields = ['nombre','clave','departamento__nombre']
    ordering_fields = ['nombre','created_at','updated_at']
    ordering = ['nombre']
