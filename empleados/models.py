from django.core.validators import EmailValidator, MinLengthValidator, RegexValidator
from django.db import models
from simple_history.models import HistoricalRecords

from catalogos.models import Departamento, Puesto
from core.models import SoftDeleteModel

GENERO_CHOICES = [
    ("M", "Masculino"),
    ("F", "Femenino"),
    ("O", "Otro/No especifica"),
]

ESTADO_CIVIL_CHOICES = [
    ("S", "Soltero(a)"),
    ("C", "Casado(a)"),
    ("D", "Divorciado(a)"),
    ("V", "Viudo(a)"),
    ("U", "Unión libre"),
]

curp_validator = RegexValidator(r"^[A-Z]{4}\d{6}[HM][A-Z]{5}\d{2}$", "CURP inválida.")
rfc_validator = RegexValidator(r"^[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}$", "RFC inválido.")
nss_validator = RegexValidator(r"^\d{11}$", "NSS inválido (11 dígitos).")


class Empleado(SoftDeleteModel):
    num_empleado = models.CharField(max_length=20, unique=True)
    nombres = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(max_length=100, blank=True, default="")

    fecha_nacimiento = models.DateField(null=True, blank=True)
    genero = models.CharField(max_length=1, choices=GENERO_CHOICES, default="O")
    estado_civil = models.CharField(
        max_length=1, choices=ESTADO_CIVIL_CHOICES, default="S"
    )

    curp = models.CharField(
        max_length=18, unique=True, validators=[MinLengthValidator(18), curp_validator]
    )
    rfc = models.CharField(
        max_length=13, unique=True, validators=[MinLengthValidator(12), rfc_validator]
    )
    nss = models.CharField(max_length=11, unique=True, validators=[nss_validator])

    telefono = models.CharField(max_length=20, blank=True, default="")
    email = models.EmailField(unique=True, validators=[EmailValidator()])

    departamento = models.ForeignKey(
        Departamento,
        on_delete=models.PROTECT,
        related_name="empleados",
        null=True,
        blank=True,
    )
    puesto = models.ForeignKey(
        Puesto,
        on_delete=models.PROTECT,
        related_name="empleados",
        null=True,
        blank=True,
    )

    fecha_ingreso = models.DateField(null=True, blank=True)
    activo = models.BooleanField(default=True)
    foto = models.ImageField(upload_to="empleados/fotos/", null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Auditoría
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

    def __str__(self):
        return f"{self.num_empleado} - {self.apellido_paterno} {self.apellido_materno} {self.nombres}"
