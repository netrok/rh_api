# GV-RH API (Backend)  Django REST

API de Recursos Humanos para **nueva versión proyecto RH**.  
Incluye **empleados** con foto y datos completos, **catálogos** (departamentos, puestos, turnos, horarios), **soft-delete**, **historial**, **exportación a Excel**, **JWT** y **RBAC** por grupos.

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

##  TL;DR (Quickstart)

```bash
# 1) Crear y activar venv (Windows PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1

# 2) Instalar dependencias
pip install -r requirements.txt

# 3) Configurar variables de entorno (.env en la raíz)
copy NUL .env

# 4) Migraciones y superusuario
python manage.py migrate
python manage.py createsuperuser

# 5) Semillas mínimas
python manage.py shell
py
Copiar código
# En el shell:
from django.contrib.auth.models import Group
for g in ["SuperAdmin","Admin","RRHH","Gerente","Supervisor","Usuario"]:
    Group.objects.get_or_create(name=g)

from catalogos.models import Departamento, Puesto, Turno, Horario
Departamento.objects.get_or_create(nombre="Sistemas")
Puesto.objects.get_or_create(nombre="Dev Senior")
Turno.objects.get_or_create(nombre="Matutino")
Horario.objects.get_or_create(nombre="L-V 9:00-18:00")
bash
Copiar código
# 6) Correr el server
python manage.py runserver
Docs: /api/docs/ (Swagger) y /api/redoc/

Admin: /admin/

 Variables de entorno (.env)
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
# Opcionales:
DB_SEARCH_PATH=public
DB_SSLMODE=

# API
API_PAGE_SIZE=10
JWT_ACCESS_MIN=60
JWT_REFRESH_DAYS=7
Media: MEDIA_URL=/media/, MEDIA_ROOT=media/ (ya configurado). En prod usa S3/MinIO o Nginx para servir /media/.

 Autenticación (JWT)
Endpoints:

POST /api/token/ (obtener)

POST /api/token/refresh/

POST /api/token/verify/

POST /api/token/blacklist/

Ejemplo:

bash
Copiar código
http POST :8000/api/token/ username=admin password=****
# Usa el access token en Swagger (Authorize  Bearer <token>)
 RBAC (Permisos por grupos)
Grupos estándar:
SuperAdmin, Admin, RRHH, Gerente, Supervisor, Usuario.

Catálogos: lectura autenticada; escritura Admin.

Empleados: lectura autenticada; escritura RRHH o Admin.

Acciones sensibles (soft-delete/restore): Admin.

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

Soportan:

search=... (por nombre/clave y depto en Puesto)

ordering=id|nombre|clave|created_at|updated_at

filter: activo=true|false

include_deleted=1 para incluir soft-deleted

Empleados
GET/POST/PUT/PATCH/DELETE /empleados/

POST /empleados/{id}/soft-delete/

POST /empleados/{id}/restore/

GET /empleados/{id}/history/

GET /empleados/export/excel (xlsx)

Características:

Foto (multipart)  campos foto y foto_url (read).

Relaciones por id: departamento_id, puesto_id, turno_id, horario_id.

Búsqueda: search= (nombres, num_empleado, curp, rfc, nss, email, depto/puesto).

Orden: ordering=num_empleado|fecha_ingreso|apellido_paterno|created_at.

Filtros extra:

q= (búsqueda amplia)

departamento, puesto, activo, genero, departamento_nombre, puesto_nombre

include_deleted=1 + deleted=true|false

Ejemplos:

bash
Copiar código
# Crear (foto opcional)
http -f POST :8000/api/v1/empleados/ \
  num_empleado=E001 nombres=Juan apellido_paterno=Perez activo:=true \
  departamento_id:=1 puesto_id:=1 turno_id:=1 horario_id:=1 \
  email=juan.perez@example.com fecha_ingreso=2025-08-27 \
  foto@./ejemplo.jpg

# Buscar y ordenar
http GET :8000/api/v1/empleados/?search=E001
http GET :8000/api/v1/empleados/?departamento=1&ordering=apellido_paterno

# Soft-delete y restore
http POST :8000/api/v1/empleados/1/soft-delete/
http POST :8000/api/v1/empleados/1/restore/

# Exportar
http GET :8000/api/v1/empleados/export/excel
 Modelos clave
Empleado (resumen)
Básicos: num_empleado, nombres, apellido_paterno, apellido_materno, activo, foto

Personales: fecha_nacimiento, genero (M/F/O), estado_civil (soltero/casado/union_libre/divorciado/viudo), curp, rfc, nss, telefono, celular, email

Domicilio: calle, numero, colonia, municipio, estado, cp

Laboral: departamento, puesto, fecha_ingreso, sueldo, tipo_contrato, tipo_jornada, turno, horario

Bancario: banco, clabe, cuenta

Emergencia/Otros: contacto_emergencia_*, escolaridad, notas

Soft-delete: deleted_at + managers: .objects (vivos), .all_objects (todos).
Unicidad condicional (solo vivos): num_empleado, curp, rfc, nss.

 Media
Dev: servido por Django (MEDIA_URL/MEDIA_ROOT).

Prod: usar S3/MinIO o Nginx para archivos estáticos y media.

Campo foto sube a media/empleados/ y se expone como foto_url.

 Excel Export
GET /api/v1/empleados/export/excel descarga un .xlsx con filtros y orden aplicados.
Incluye columnas: ID, Num. empleado, Nombre, Depto, Puesto, Fecha ingreso, Email, Teléfono, Activo.

 Soft-delete & History
Soft-delete/Restore: acciones en endpoints y en Admin.

Historial (django-simple-history): GET /empleados/{id}/history/ devuelve cambios auditados.

 Admin
Empleados: miniatura de foto, autocomplete en FKs, acciones de restaurar / hard delete.

Catálogos: listados con búsqueda, soft-delete/restore/hard delete; autocomplete en Puesto.departamento.

 Frontend (alineación rápida)
Enviar multipart con:

Copiar código
departamento_id, puesto_id, turno_id, horario_id,
contacto_emergencia_parentesco,  y el resto de campos
Previsualiza foto_url.

toFormData(values) para enviar (adjuntando foto si existe).

 Troubleshooting
admin.E039 Turno/Horario: registra sus Admins (ya incluido en catalogos/admin.py).

CORS: agrega tu frontend a CORS_ALLOWED_ORIGINS en .env.

Pylance Variable not allowed in type expression: usamos Union["AbstractBaseUser","AnonymousUser",None] y forward refs.

No changes detected al makemigrations: confirma que guardaste modelos correctos y que editas este repo.

Unicidad: si migrate falla por duplicados (vivos), corrige/marca como borrados antes de aplicar constraints.

 Licencia
Privado / Interno (ajústalo si necesitas MIT u otra).

 Contribuir
Crea rama: feat/<lo-que-haces>

Lint/tests (si aplica)

PR  main con checklist:

 Crear/editar empleado con foto

 Soft-delete/restore OK

 Export Excel OK

 Permisos RBAC OK

 Swagger actualizado

 Enlaces útiles
Swagger: /api/docs/

ReDoc: /api/redoc/

Health: /api/ping/

Me: /api/me/
