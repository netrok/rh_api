# catalogos/models.py
from __future__ import annotations

from django.db import models
from simple_history.models import HistoricalRecords

from core.models import SoftDeleteModel


class Departamento(SoftDeleteModel):
    nombre = models.CharField(max_length=120, unique=True)
    clave = models.CharField(max_length=20, unique=True, null=True, blank=True)  # opcional, único
    activo = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    class Meta:
        db_table = "cat_departamentos"
        ordering = ["nombre"]
        indexes = [
            models.Index(fields=["nombre"]),
            models.Index(fields=["activo"]),
        ]

    def __str__(self) -> str:
        return self.nombre


class Puesto(SoftDeleteModel):
    nombre = models.CharField(max_length=120, unique=True)
    clave = models.CharField(max_length=20, unique=True, null=True, blank=True)  # opcional, único
    departamento = models.ForeignKey(
        "catalogos.Departamento",
        on_delete=models.PROTECT,  # evita borrar depto con puestos vinculados
        related_name="puestos",
        null=True,
        blank=True,
    )
    activo = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    class Meta:
        db_table = "cat_puestos"
        ordering = ["nombre"]
        indexes = [
            models.Index(fields=["nombre"]),
            models.Index(fields=["departamento"]),
            models.Index(fields=["activo"]),
        ]

    def __str__(self) -> str:
        return self.nombre


class Turno(SoftDeleteModel):
    nombre = models.CharField(max_length=120, unique=True)
    clave = models.CharField(max_length=20, unique=True, null=True, blank=True)
    activo = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    class Meta:
        db_table = "cat_turnos"
        ordering = ["nombre"]
        indexes = [
            models.Index(fields=["nombre"]),
            models.Index(fields=["activo"]),
        ]

    def __str__(self) -> str:
        return self.nombre


class Horario(SoftDeleteModel):
    nombre = models.CharField(max_length=120, unique=True)
    clave = models.CharField(max_length=20, unique=True, null=True, blank=True)
    activo = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    class Meta:
        db_table = "cat_horarios"
        ordering = ["nombre"]
        indexes = [
            models.Index(fields=["nombre"]),
            models.Index(fields=["activo"]),
        ]

    def __str__(self) -> str:
        return self.nombre
