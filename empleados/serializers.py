# empleados/serializers.py
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from .models import Empleado


class EmpleadoSerializer(serializers.ModelSerializer):
    departamento_nombre = serializers.ReadOnlyField(source="departamento.nombre")
    puesto_nombre = serializers.ReadOnlyField(source="puesto.nombre")
    genero_display = serializers.CharField(source="get_genero_display", read_only=True)
    estado_civil_display = serializers.CharField(
        source="get_estado_civil_display", read_only=True
    )
    foto_url = serializers.SerializerMethodField()

    class Meta:
        model = Empleado
        fields = [
            "id",
            "num_empleado",
            "nombres",
            "apellido_paterno",
            "apellido_materno",
            "fecha_nacimiento",
            "genero",
            "genero_display",
            "estado_civil",
            "estado_civil_display",
            "curp",
            "rfc",
            "nss",
            "telefono",
            "email",
            "departamento",
            "departamento_nombre",
            "puesto",
            "puesto_nombre",
            "fecha_ingreso",
            "activo",
            "foto",
            "foto_url",
            "created_at",
            "updated_at",
            "deleted_at",
        ]
        read_only_fields = [
            "departamento_nombre",
            "puesto_nombre",
            "genero_display",
            "estado_civil_display",
            "foto_url",
            "created_at",
            "updated_at",
            "deleted_at",
        ]

    @extend_schema_field(OpenApiTypes.URI)
    def get_foto_url(self, obj) -> str | None:
        if obj.foto:
            request = self.context.get("request")
            url = obj.foto.url
            return request.build_absolute_uri(url) if request else url
        return None
