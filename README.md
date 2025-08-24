# GV-RH API  Django + DRF

`	ext
   ____ ____     ____  _   _        _     
  / ___|  _ \   |  _ \| | | |  __ _| |__  
 | |  _| |_) |  | |_) | |_| | / _ | '_ \ 
 | |_| |  _ <   |  _ <|  _  || (_| | | | |
  \____|_| \_\  |_| \_\_| |_(_)__, |_| |_|
                             |___/         
Backend de Recursos Humanos con Django 5, DRF, JWT, OpenAPI (Swagger), PostgreSQL, soft delete, auditoría de cambios, filtros/paginación y exportación a Excel.

Tabla de contenidos
Stack

Estructura del proyecto

Requisitos

Configuración rápida (Windows 11)

Base de datos (PostgreSQL 17)

Variables de entorno

Comandos clave

Documentación y Auth

Endpoints principales

Filtros y ejemplos prácticos

Soft delete & Auditoría

Exportación a Excel

Admin de Django

Producción (seguridad y estáticos)

VS Code (debug)

Recomendaciones

Stack
 Python 3.13.3

 Django 5.2.5  DRF  drf-spectacular (Swagger)

 JWT (djangorestframework-simplejwt)

 PostgreSQL 17

 django-filter, Pillow, openpyxl (Excel), django-simple-history (auditoría)

Diagrama rápido:

text
Copiar código
[Cliente]  [JWT Auth]  [DRF ViewSets]  [Models c/SoftDelete + History]  [ORM]  [PostgreSQL]
                              |                       |
                               Swagger (/api/docs)  Export Excel
Estructura del proyecto
text
Copiar código
rh_api/
 rh_api/
   settings.py         # settings (CORS/CSRF, JWT, DRF, seguridad prod)
   urls.py             # rutas: /api/docs, /api/auth, /api/v1/*
   wsgi.py
 core/
   models.py           # SoftDeleteModel + managers
 catalogos/
   models.py           # Departamento, Puesto (soft delete + history)
   admin.py            # Admin con acciones (soft/restore/hard delete)
 empleados/
   models.py           # Empleado (FKs a catálogos, soft + history)
   serializers.py
   views.py            # Filtros, export-excel, history, restore, soft-delete
   admin.py
 media/                 # uploads (fotos)
 staticfiles/           # collectstatic
 .env                   # variables local (no commitear)
 .env.example           # plantilla sin secretos
 .gitignore
 manage.py
Requisitos
Windows 11 x64

Python 3.13.3

PostgreSQL 17 (psql en PATH)

VS Code (recomendado)

Configuración rápida (Windows 11)
powershell
Copiar código
# 1) Clonar el repo (ajusta la URL si usas otra)
cd C:\Proyectos
git clone https://github.com/netrok/rh_api.git
cd .\rh_api

# 2) Crear venv e instalar dependencias
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip

# Requisitos (si no tienes requirements.txt)
pip install Django==5.2.5 djangorestframework drf-spectacular 
  djangorestframework-simplejwt django-filter python-dotenv 
  psycopg[binary] Pillow openpyxl django-simple-history

# 3) Copiar variables de entorno
copy .\.env.example .\.env
# (Edita .env con tus credenciales; abajo hay referencia)
Base de datos (PostgreSQL 17)
powershell
Copiar código
# Entrar a psql como postgres
psql -U postgres -h localhost
sql
Copiar código
-- Crea db, rol y permisos (ajusta contraseña y esquema si quieres usar 'rh')
CREATE ROLE rh_user LOGIN PASSWORD 'tu_password_segura';
CREATE DATABASE rh_db OWNER rh_user;

-- (Opcional) Esquema dedicado:
CREATE SCHEMA rh AUTHORIZATION rh_user;
GRANT USAGE, CREATE ON SCHEMA rh TO rh_user;

-- Permisos básicos
GRANT ALL PRIVILEGES ON DATABASE rh_db TO rh_user;

-- (Opcional) Zona horaria por comodidad
ALTER ROLE rh_user SET timezone TO 'America/Mexico_City';
\q
Si usas un esquema propio, pon en .env:

ini
Copiar código
DB_SEARCH_PATH=rh,public
Variables de entorno
./.env (desarrollo):

dotenv
Copiar código
# Django
DJANGO_SECRET_KEY=CAMBIA_ESTA_CLAVE_EN_PROD
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost

# DRF
API_PAGE_SIZE=10

# JWT
JWT_ACCESS_MIN=60
JWT_REFRESH_DAYS=7

# TZ
TZ=America/Mexico_City

# PostgreSQL
DB_NAME=rh_db
DB_USER=rh_user
DB_PASSWORD=tu_password_segura
DB_HOST=localhost
DB_PORT=5432
DB_SEARCH_PATH=rh,public
DB_SSLMODE=disable

# CORS (tu frontend)
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
No subas .env al repo (ya viene ignorado en .gitignore).
Mantén un .env.example sin secretos.

Comandos clave
powershell
Copiar código
# Activar venv
.\.venv\Scripts\Activate.ps1

# Migraciones
python manage.py makemigrations
python manage.py migrate

# Superusuario (para /admin)
python manage.py createsuperuser

# Correr el server
python manage.py runserver 8000

# Chequeo general
python manage.py check

# (Prod) recopilar estáticos
python manage.py collectstatic
Documentación y Auth
Swagger UI: http://127.0.0.1:8000/api/docs/

OpenAPI JSON: http://127.0.0.1:8000/api/schema/

Ping: http://127.0.0.1:8000/ping/

JWT Endpoints:

POST /api/auth/token/ (user+pass  access+refresh)

POST /api/auth/refresh/ (refresh  access)

Ejemplo (PowerShell/cURL):

powershell
Copiar código
curl -X POST http://127.0.0.1:8000/api/auth/token/ 
  -H "Content-Type: application/json" 
  -d "{\"username\":\"admin\",\"password\":\"TU_PASS\"}"
Copia access  en Swagger presiona Authorize  Bearer <access>.

Endpoints principales
Catálogos

GET/POST /api/v1/departamentos/

GET/POST /api/v1/puestos/
Filtros: q, activo, departamento (en puestos)

Empleados

GET/POST /api/v1/empleados/

Acciones:

POST /api/v1/empleados/{id}/soft-delete/

POST /api/v1/empleados/{id}/restore/

GET /api/v1/empleados/{id}/history/

GET /api/v1/empleados/export-excel

Campos clave en Empleado:

Identidad: num_empleado, nombres, apellidos, email

MX: curp, rfc, nss (con validaciones)

Organización: departamento (FK), puesto (FK)

Estados: activo, deleted_at (soft delete)

Auditoría: histórico de cambios con django-simple-history

Multimedia: foto (ImageField  /media/empleados/fotos/)

Filtros y ejemplos prácticos
Parámetros soportados en GET /api/v1/empleados/:

Búsqueda general: ?q=texto

Estado: ?activo=true|false

Por FK (ID): ?departamento=1, ?puesto=3

Por nombre (catálogo): ?departamento_nombre=ti, ?puesto_nombre=analista

Soft delete:

?include_deleted=1  incluye vivos + borrados

?deleted=true  sólo borrados

Orden: ?ordering=-fecha_ingreso (ver ordering_fields)

Ejemplos:

powershell
Copiar código
# Búsqueda general + orden
curl -H "Authorization: Bearer ACCESS" "http://127.0.0.1:8000/api/v1/empleados/?q=garcia&ordering=-fecha_ingreso"

# Filtrar por departamento (ID=1) y sólo activos
curl -H "Authorization: Bearer ACCESS" "http://127.0.0.1:8000/api/v1/empleados/?departamento=1&activo=true"

# Ver sólo borrados
curl -H "Authorization: Bearer ACCESS" "http://127.0.0.1:8000/api/v1/empleados/?deleted=true"
Soft delete & Auditoría
Soft delete: no elimina físicamente; marca deleted_at y el registro deja de aparecer por defecto.

Restauración: restore limpia deleted_at.

Listado con borrados: ?include_deleted=1 (vivos + borrados) o ?deleted=true (sólo borrados).

Historial de cambios: GET /api/v1/empleados/{id}/history/ muestra auditoría: fecha, usuario, tipo de cambio y campos clave.

Acciones rápidas:

powershell
Copiar código
# Borrar lógicamente
curl -X POST -H "Authorization: Bearer ACCESS" 
  "http://127.0.0.1:8000/api/v1/empleados/1/soft-delete/"

# Restaurar
curl -X POST -H "Authorization: Bearer ACCESS" 
  "http://127.0.0.1:8000/api/v1/empleados/1/restore/"

# Historial
curl -H "Authorization: Bearer ACCESS" 
  "http://127.0.0.1:8000/api/v1/empleados/1/history/"
Exportación a Excel
GET /api/v1/empleados/export-excel respalda el listado filtrado actual en empleados.xlsx:

powershell
Copiar código
curl -L -H "Authorization: Bearer ACCESS" 
  "http://127.0.0.1:8000/api/v1/empleados/export-excel" --output empleados.xlsx
Incluye columnas: datos personales, catálogos, estado, timestamps y marca de borrado.

Admin de Django
/admin/

Acciones en lista: Borrar lógicamente, Restaurar, Eliminar definitivamente.

Historial por registro (via SimpleHistoryAdmin).

Listados muestran también borrados (usamos all_objects en get_queryset del admin).

Crea tu superusuario con python manage.py createsuperuser.

Producción (seguridad y estáticos)
En settings.py ya viene activado cuando DJANGO_DEBUG=False:

Cookies Secure, HSTS, SECURE_SSL_REDIRECT, X_FRAME_OPTIONS=DENY, REFERRER_POLICY, SECURE_PROXY_SSL_HEADER.

DRF sin Browsable API (solo JSON).

collectstatic:

powershell
Copiar código
set DJANGO_DEBUG=False
python manage.py collectstatic
Asegura tu ALLOWED_HOSTS, CORS, y DB_SSLMODE=require si tu proveedor lo pide.

Usa WSGI/ASGI de producción (uWSGI, gunicorn, Daphne, etc.) detrás de Nginx/Apache.

VS Code (debug)
.vscode/launch.json (opcional):

json
Copiar código
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Django: runserver",
      "type": "python",
      "request": "launch",
      "program": "\\manage.py",
      "args": ["runserver", "8000"],
      "django": true,
      "envFile": "\\.env",
      "console": "integratedTerminal",
      "justMyCode": true
    }
  ]
}
Recomendaciones
 Mantén migraciones limpias (no generes duplicados innecesarios).

 Evita imports circulares (usa referencias por cadena en FKs: 'catalogos.Departamento').

 Aísla dependencias en .venv y congela versiones si necesitas reproducibilidad:

powershell
Copiar código
pip freeze > requirements.lock.txt
 No subas secretos. Usa .env, .env.prod y vaults en tus pipelines.
