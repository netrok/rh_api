# catalogos/serializers.py
from rest_framework import serializers

from .models import Departamento, Puesto


class DepartamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Departamento
        fields = [
            "id",
            "nombre",
            "clave",
            "activo",
            "created_at",
            "updated_at",
            "deleted_at",
        ]
        read_only_fields = ["created_at", "updated_at", "deleted_at"]


class PuestoSerializer(serializers.ModelSerializer):
    departamento_nombre = serializers.ReadOnlyField(source="departamento.nombre")

    class Meta:
        model = Puesto
        fields = [
            "id",
            "nombre",
            "clave",
            "departamento",
            "departamento_nombre",
            "activo",
            "created_at",
            "updated_at",
            "deleted_at",
        ]
        read_only_fields = [
            "departamento_nombre",
            "created_at",
            "updated_at",
            "deleted_at",
        ]
