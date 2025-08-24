
# GV-RH API · Django + DRF

```text
   ____ ____     ____  _   _        _     
  / ___|  _ \   |  _ \| | | |  __ _| |__  
 | |  _| |_) |  | |_) | |_| | / _` | '_ \ 
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

🐍 Python 3.13.3

🧱 Django 5.2.5 · DRF · drf-spectacular (Swagger)

🔐 JWT (djangorestframework-simplejwt)

🐘 PostgreSQL 17

📁 django-filter, Pillow, openpyxl (Excel), django-simple-history (auditoría)

Diagrama rápido:

[Cliente] → [JWT Auth] → [DRF ViewSets] → [Models c/SoftDelete + History] → [ORM] → [PostgreSQL]
                              |                       |
                              └── Swagger (/api/docs) └── Export Excel


rh_api/
├─ rh_api/
│  ├─ settings.py         # settings (CORS/CSRF, JWT, DRF, seguridad prod)
│  ├─ urls.py             # rutas: /api/docs, /api/auth, /api/v1/*
│  └─ wsgi.py
├─ core/
│  └─ models.py           # SoftDeleteModel + managers
├─ catalogos/
│  ├─ models.py           # Departamento, Puesto (soft delete + history)
│  └─ admin.py            # Admin con acciones (soft/restore/hard delete)
├─ empleados/
│  ├─ models.py           # Empleado (FKs a catálogos, soft + history)
│  ├─ serializers.py
│  ├─ views.py            # Filtros, export-excel, history, restore, soft-delete
│  └─ admin.py
├─ media/                 # uploads (fotos)
├─ staticfiles/           # collectstatic
├─ .env                   # variables local (no commitear)
├─ .env.example           # plantilla sin secretos
├─ .gitignore
└─ manage.py

Requisitos

Windows 11 x64

Python 3.13.3

PostgreSQL 17 (psql en PATH)

VS Code (recomendado)

# 1) Clonar el repo (ajusta la URL si usas otra)
cd C:\Proyectos
git clone https://github.com/netrok/rh_api.git
cd .\rh_api

# 2) Crear venv e instalar dependencias
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip

# Requisitos (si no tienes requirements.txt)
pip install Django==5.2.5 djangorestframework drf-spectacular `
  djangorestframework-simplejwt django-filter python-dotenv `
  psycopg[binary] Pillow openpyxl django-simple-history

# 3) Copiar variables de entorno
copy .\.env.example .\.env
# (Edita .env con tus credenciales; abajo hay referencia)

# Entrar a psql como postgres
psql -U postgres -h localhost

DB_SEARCH_PATH=rh,public

Variables de entorno
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

POST /api/auth/token/ (user+pass → access+refresh)

POST /api/auth/refresh/ (refresh → access)

curl -X POST http://127.0.0.1:8000/api/auth/token/ `
  -H "Content-Type: application/json" `
  -d "{\"username\":\"admin\",\"password\":\"TU_PASS\"}"

Copia access → en Swagger presiona Authorize → Bearer <access>.

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

Multimedia: foto (ImageField → /media/empleados/fotos/)

Filtros y ejemplos prácticos

Parámetros soportados en GET /api/v1/empleados/:

Búsqueda general: ?q=texto

Estado: ?activo=true|false

Por FK (ID): ?departamento=1, ?puesto=3

Por nombre (catálogo): ?departamento_nombre=ti, ?puesto_nombre=analista

Soft delete:

?include_deleted=1 → incluye vivos + borrados

?deleted=true → sólo borrados

Orden: ?ordering=-fecha_ingreso (ver ordering_fields)

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

# Borrar lógicamente
curl -X POST -H "Authorization: Bearer ACCESS" `
  "http://127.0.0.1:8000/api/v1/empleados/1/soft-delete/"

# Restaurar
curl -X POST -H "Authorization: Bearer ACCESS" `
  "http://127.0.0.1:8000/api/v1/empleados/1/restore/"

# Historial
curl -H "Authorization: Bearer ACCESS" `
  "http://127.0.0.1:8000/api/v1/empleados/1/history/"

Exportación a Excel

GET /api/v1/empleados/export-excel respalda el listado filtrado actual en empleados.xlsx:
curl -L -H "Authorization: Bearer ACCESS" `
  "http://127.0.0.1:8000/api/v1/empleados/export-excel" --output empleados.xlsx

Recomendaciones

✅ Mantén migraciones limpias (no generes duplicados innecesarios).

✅ Evita imports circulares (usa referencias por cadena en FKs: 'catalogos.Departamento').

✅ Aísla dependencias en .venv y congela versiones si necesitas reproducibilidad:

pip freeze > requirements.lock.txt

✅ No subas secretos. Usa .env, .env.prod y vaults en tus pipelines.