# empleados/serializers.py
from __future__ import annotations

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from .models import Empleado
from catalogos.models import Puesto, Departamento, Turno, Horario


class EmpleadoSerializer(serializers.ModelSerializer):
    # ---- Relaciones (write) ----
    puesto_id = serializers.PrimaryKeyRelatedField(
        source="puesto", queryset=Puesto.objects.all(), required=False, allow_null=True
    )
    departamento_id = serializers.PrimaryKeyRelatedField(
        source="departamento", queryset=Departamento.objects.all(), required=False, allow_null=True
    )
    turno_id = serializers.PrimaryKeyRelatedField(
        source="turno", queryset=Turno.objects.all(), required=False, allow_null=True
    )
    horario_id = serializers.PrimaryKeyRelatedField(
        source="horario", queryset=Horario.objects.all(), required=False, allow_null=True
    )

    # ---- Derivados (read) ----
    departamento_nombre = serializers.ReadOnlyField(source="departamento.nombre")
    puesto_nombre = serializers.ReadOnlyField(source="puesto.nombre")
    turno_nombre = serializers.ReadOnlyField(source="turno.nombre")
    horario_nombre = serializers.ReadOnlyField(source="horario.nombre")

    genero_display = serializers.CharField(source="get_genero_display", read_only=True)
    estado_civil_display = serializers.CharField(source="get_estado_civil_display", read_only=True)

    foto_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Empleado
        fields = [
            # Base
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
            "celular",
            "email",
            # Domicilio
            "calle",
            "numero",
            "colonia",
            "municipio",
            "estado",
            "cp",
            # Relaciones (write IDs + read nombres)
            "departamento_id",
            "departamento_nombre",
            "puesto_id",
            "puesto_nombre",
            "turno_id",
            "turno_nombre",
            "horario_id",
            "horario_nombre",
            # Laboral
            "fecha_ingreso",
            "activo",
            "sueldo",
            "tipo_contrato",
            "tipo_jornada",
            # Bancario
            "banco",
            "clabe",
            "cuenta",
            # Emergencia / Otros
            "contacto_emergencia_nombre",
            "contacto_emergencia_parentesco",
            "contacto_emergencia_telefono",
            "escolaridad",
            "notas",
            # Archivos
            "foto",
            "foto_url",
            # Timestamps / soft delete
            "created_at",
            "updated_at",
            "deleted_at",
        ]
        read_only_fields = [
            "departamento_nombre",
            "puesto_nombre",
            "turno_nombre",
            "horario_nombre",
            "genero_display",
            "estado_civil_display",
            "foto_url",
            "created_at",
            "updated_at",
            "deleted_at",
        ]

    # ---- Helpers ----
    @extend_schema_field(OpenApiTypes.URI)
    def get_foto_url(self, obj) -> str | None:
        if obj.foto and hasattr(obj.foto, "url"):
            request = self.context.get("request")
            url = obj.foto.url
            return request.build_absolute_uri(url) if request else url
        return None

    # Normaliza a mayúsculas CURP/RFC; email en minúsculas
    def validate(self, attrs):
        curp = attrs.get("curp")
        rfc = attrs.get("rfc")
        email = attrs.get("email")
        if curp:
            attrs["curp"] = curp.strip().upper()
        if rfc:
            attrs["rfc"] = rfc.strip().upper()
        if email:
            attrs["email"] = email.strip().lower()
        return super().validate(attrs)

    def validate_clabe(self, v):
        if v and len(v) != 18:
            raise serializers.ValidationError("La CLABE debe tener 18 dígitos.")
        return v
