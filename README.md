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
