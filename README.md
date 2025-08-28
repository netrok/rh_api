# GV-RH API (Backend)  Django REST

API de Recursos Humanos para **nueva versión proyecto RH**.  
Incluye **empleados** (con foto y datos completos), **catálogos** (departamentos, puestos, turnos, horarios), **soft-delete**, **historial**, **exportación a Excel**, **JWT** y **RBAC** por grupos.

---

##  Stack
- Django 5 + Django REST Framework
- PostgreSQL
- Simple JWT
- django-filters
- drf-spectacular (OpenAPI/Swagger)
- django-simple-history
- Soft-delete casero (`core.models.SoftDeleteModel`)

---

##  Quickstart

```bash
# 1) venv (Windows PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1

# 2) Dependencias
pip install -r requirements.txt

# 3) Variables de entorno
copy NUL .env

# 4) Migraciones y superusuario
python manage.py migrate
python manage.py createsuperuser

# 5) Arrancar
python manage.py runserver
Semillas mínimas (grupos y catálogos):

py
Copiar código
from django.contrib.auth.models import Group
for g in ["SuperAdmin","Admin","RRHH","Gerente","Supervisor","Usuario"]:
    Group.objects.get_or_create(name=g)

from catalogos.models import Departamento, Puesto, Turno, Horario
Departamento.objects.get_or_create(nombre="Sistemas")
Puesto.objects.get_or_create(nombre="Dev Senior")
Turno.objects.get_or_create(nombre="Matutino")
Horario.objects.get_or_create(nombre="L-V 9:00-18:00")
Docs: /api/docs/ (Swagger) y /api/redoc/

Admin: /admin/

 .env (ejemplo)
env
Copiar código
DJANGO_SECRET_KEY=dev-change-me
DJANGO_DEBUG=1
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# PostgreSQL
DB_NAME=rh_db
DB_USER=rh_user
DB_PASSWORD=yourpass
DB_HOST=localhost
DB_PORT=5432
DB_SEARCH_PATH=public
DB_SSLMODE=

# API
API_PAGE_SIZE=10
JWT_ACCESS_MIN=60
JWT_REFRESH_DAYS=7
Media: MEDIA_URL=/media/, MEDIA_ROOT=media/. En prod usar S3/MinIO o Nginx para servir /media/.

 Autenticación (JWT)
POST /api/token/

POST /api/token/refresh/

POST /api/token/verify/

POST /api/token/blacklist/

Ejemplo:

bash
Copiar código
http POST :8000/api/token/ username=admin password=*****
# Luego usa el token en Swagger (Authorize  Bearer <token>)
 RBAC (grupos)
Grupos: SuperAdmin, Admin, RRHH, Gerente, Supervisor, Usuario.

Catálogos: lectura autenticada; escritura Admin.

Empleados: lectura autenticada; escritura RRHH o Admin.

Soft-delete/restore: Admin.

Toggles en core/permissions.py:

py
Copiar código
READ_REQUIRES_AUTH = True   # lecturas públicas si False
ALLOW_STAFF_WRITE = True    # si True, is_staff también puede escribir
 Endpoints principales
Base: /api/v1/

Catálogos
GET/POST/PUT/PATCH/DELETE /departamentos/

GET/POST/PUT/PATCH/DELETE /puestos/

GET/POST/PUT/PATCH/DELETE /turnos/

GET/POST/PUT/PATCH/DELETE /horarios/

Extras: search=, ordering=, filter por activo, include_deleted=1 (soft-deleted).

Empleados
CRUD: /empleados/

Soft-delete: POST /empleados/{id}/soft-delete/

Restore: POST /empleados/{id}/restore/

Historial: GET /empleados/{id}/history/

Export: GET /empleados/export/excel

Características:

Foto (multipart): foto y foto_url.

Relaciones por id: departamento_id, puesto_id, turno_id, horario_id.

Búsqueda: search= (nombre, num_empleado, curp, rfc, nss, email, depto/puesto).

Orden: ordering=num_empleado|fecha_ingreso|apellido_paterno|created_at.

Ejemplo creación (con foto opcional):

bash
Copiar código
http -f POST :8000/api/v1/empleados/ \
  num_empleado=E001 nombres=Juan apellido_paterno=Perez activo:=true \
  departamento_id:=1 puesto_id:=1 turno_id:=1 horario_id:=1 \
  email=juan.perez@example.com fecha_ingreso=2025-08-27 \
  foto@./ejemplo.jpg
 Modelo Empleado (resumen)
Básicos: num_empleado, nombres, apellido_{paterno,materno}, activo, foto

Personales: fecha_nacimiento, genero (M/F/O), estado_civil (soltero/casado/union_libre/divorciado/viudo), curp, rfc, nss, telefono, celular, email

Domicilio: calle, numero, colonia, municipio, estado, cp

Laboral: departamento, puesto, fecha_ingreso, sueldo, tipo_contrato, tipo_jornada, turno, horario

Bancario: banco, clabe, cuenta

Emergencia/Otros: contacto_emergencia_*, escolaridad, notas

Soft-delete: deleted_at + managers .objects (vivos) y .all_objects (todos).
Unicidad condicional (solo vivos): num_empleado, curp, rfc, nss.

 Admin
Empleados: miniatura de foto, autocomplete en FKs, acciones de restaurar y hard delete.

Catálogos: búsqueda, soft-delete/restore/hard delete; autocomplete en Puesto.departamento.

 Troubleshooting
admin.E039  registra Turno/Horario en admin (listo en catalogos/admin.py).

CORS  añade tu frontend a CORS_ALLOWED_ORIGINS en .env.

Pylance tipos  usamos Union["AbstractBaseUser","AnonymousUser",None] y forward refs.

No changes detected al makemigrations  verifica models.py guardados y el repo correcto.

Unicidad condicional  corrige duplicados vivos antes de migrar.

 Enlaces útiles
Swagger: /api/docs/

ReDoc: /api/redoc/

Health: /api/ping/

Me: /api/me/
