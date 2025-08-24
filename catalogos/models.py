from django.db import models
from simple_history.models import HistoricalRecords

from core.models import SoftDeleteModel


class Departamento(SoftDeleteModel):
    nombre = models.CharField(max_length=120, unique=True)
    clave = models.CharField(max_length=20, unique=True, blank=True, default="")
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    history = HistoricalRecords()

    class Meta:
        db_table = "cat_departamentos"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Puesto(SoftDeleteModel):
    nombre = models.CharField(max_length=120, unique=True)
    clave = models.CharField(max_length=20, unique=True, blank=True, default="")
    departamento = models.ForeignKey(
        "catalogos.Departamento",
        on_delete=models.PROTECT,
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

    def __str__(self):
        return self.nombre
