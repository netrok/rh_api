# empleados/models.py
from __future__ import annotations

from django.core.validators import EmailValidator, MinLengthValidator, RegexValidator
from django.db import models
from django.db.models import Q, UniqueConstraint
from simple_history.models import HistoricalRecords

from catalogos.models import Departamento, Puesto
from core.models import SoftDeleteModel  # expone deleted_at, objects/all_objects

# ── Catálogos de opciones ─────────────────────────────────────────────────────
GENERO_CHOICES = [
    ("M", "Masculino"),
    ("F", "Femenino"),
    ("O", "Otro/No especifica"),
]

# Valores “largos” alineados al front/API
ESTADO_CIVIL_CHOICES = [
    ("soltero", "Soltero(a)"),
    ("casado", "Casado(a)"),
    ("union_libre", "Unión libre"),
    ("divorciado", "Divorciado(a)"),
    ("viudo", "Viudo(a)"),
]

# ── Validadores ───────────────────────────────────────────────────────────────
curp_validator = RegexValidator(r"^[A-Z]{4}\d{6}[HM][A-Z]{5}\d{2}$", "CURP inválida.")
rfc_validator = RegexValidator(r"^[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}$", "RFC inválido.")
nss_validator = RegexValidator(r"^\d{11}$", "NSS inválido (11 dígitos).")
clabe_validator = RegexValidator(r"^\d{18}$", "CLABE debe tener 18 dígitos.")
cuenta_validator = RegexValidator(r"^\d{10,20}$", "Cuenta bancaria entre 10 y 20 dígitos.")

# ── Modelo Empleado ──────────────────────────────────────────────────────────
class Empleado(SoftDeleteModel):
    # Básicos
    num_empleado = models.CharField(max_length=50)  # unicidad via constraint condicional
    nombres = models.CharField(max_length=150)
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(max_length=100, blank=True, null=True)

    # Personales
    fecha_nacimiento = models.DateField(blank=True, null=True)
    genero = models.CharField(max_length=1, choices=GENERO_CHOICES, blank=True, null=True)
    estado_civil = models.CharField(max_length=20, choices=ESTADO_CIVIL_CHOICES, blank=True, null=True)

    curp = models.CharField(
        max_length=18, blank=True, null=True,
        validators=[MinLengthValidator(18), curp_validator]
    )
    rfc = models.CharField(
        max_length=13, blank=True, null=True,
        validators=[MinLengthValidator(12), rfc_validator]
    )
    nss = models.CharField(max_length=11, blank=True, null=True, validators=[nss_validator])

    telefono = models.CharField(max_length=20, blank=True, null=True)
    celular = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True, validators=[EmailValidator()])

    # Domicilio
    calle = models.CharField(max_length=120, blank=True, null=True)
    numero = models.CharField(max_length=20, blank=True, null=True)
    colonia = models.CharField(max_length=120, blank=True, null=True)
    municipio = models.CharField(max_length=120, blank=True, null=True)
    estado = models.CharField(max_length=120, blank=True, null=True)
    cp = models.CharField(max_length=10, blank=True, null=True)

    # Laboral
    departamento = models.ForeignKey(
        Departamento, on_delete=models.SET_NULL, related_name="empleados", null=True, blank=True
    )
    puesto = models.ForeignKey(
        Puesto, on_delete=models.SET_NULL, related_name="empleados", null=True, blank=True
    )
    fecha_ingreso = models.DateField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    sueldo = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    tipo_contrato = models.CharField(
        max_length=20,
        choices=[("determinado", "Determinado"), ("indeterminado", "Indeterminado"), ("obra", "Obra o proyecto")],
        blank=True, null=True
    )
    tipo_jornada = models.CharField(
        max_length=20,
        choices=[("diurna", "Diurna"), ("mixta", "Mixta"), ("nocturna", "Nocturna")],
        blank=True, null=True
    )
    turno = models.ForeignKey("catalogos.Turno", on_delete=models.SET_NULL, null=True, blank=True)
    horario = models.ForeignKey("catalogos.Horario", on_delete=models.SET_NULL, null=True, blank=True)

    # Bancario
    banco = models.CharField(max_length=120, blank=True, null=True)
    clabe = models.CharField(max_length=18, blank=True, null=True, validators=[clabe_validator])
    cuenta = models.CharField(max_length=20, blank=True, null=True, validators=[cuenta_validator])

    # Emergencia / Otros
    contacto_emergencia_nombre = models.CharField(max_length=150, blank=True, null=True)
    contacto_emergencia_parentesco = models.CharField(max_length=60, blank=True, null=True)
    contacto_emergencia_telefono = models.CharField(max_length=20, blank=True, null=True)
    escolaridad = models.CharField(max_length=100, blank=True, null=True)
    notas = models.TextField(blank=True, null=True)

    # Foto
    foto = models.ImageField(upload_to="empleados/", null=True, blank=True)

    # Auditoría / timestamps (deleted_at viene de SoftDeleteModel)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    class Meta:
        db_table = "empleados"
        indexes = [
            models.Index(fields=["num_empleado"]),
            models.Index(fields=["apellido_paterno", "apellido_materno", "nombres"]),
            models.Index(fields=["departamento"]),
            models.Index(fields=["puesto"]),
            models.Index(fields=["activo"]),
        ]
        constraints = [
            # Unicidad solo para registros "vivos" (deleted_at IS NULL)
            UniqueConstraint(fields=["num_empleado"], condition=Q(deleted_at__isnull=True), name="uq_empleado_num_vivo"),
            UniqueConstraint(fields=["curp"],         condition=Q(deleted_at__isnull=True), name="uq_empleado_curp_vivo"),
            UniqueConstraint(fields=["rfc"],          condition=Q(deleted_at__isnull=True), name="uq_empleado_rfc_vivo"),
            UniqueConstraint(fields=["nss"],          condition=Q(deleted_at__isnull=True), name="uq_empleado_nss_vivo"),
        ]

    def __str__(self) -> str:
        return f"{self.num_empleado} - {self.nombres} {self.apellido_paterno}"
