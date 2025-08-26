# rh_api/urls.py
from __future__ import annotations

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path  # <- re_path
from django.views.generic import RedirectView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
    TokenBlacklistView,
)

from catalogos.views import DepartamentoViewSet, PuestoViewSet
from core.views import me, ping
from empleados.views import EmpleadoViewSet

router = DefaultRouter()
# ✅ Diagonal final OPCIONAL para TODAS las rutas del router (GET/POST/PUT/PATCH/DELETE)
router.trailing_slash = '/?'   # <- clave

router.register("departamentos", DepartamentoViewSet, basename="departamento")
router.register("puestos", PuestoViewSet, basename="puesto")
router.register("empleados", EmpleadoViewSet, basename="empleado")

urlpatterns = [
    # Home -> Swagger
    path("", RedirectView.as_view(url="/api/docs/", permanent=False)),

    path("admin/", admin.site.urls),

    # OpenAPI / Swagger / ReDoc
    path("api/schema/", SpectacularAPIView.as_view(), name="schema")
,
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),

    # Core
    path("api/ping/", ping, name="ping"),
    path("api/auth/me/", me, name="me"),

    # API v1 (router)
    path("api/v1/", include(router.urls)),
]

# ✅ JWT con diagonal final OPCIONAL (evita el error de APPEND_SLASH con POST)
urlpatterns += [
    re_path(r"^api/auth/jwt/create/?$", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    re_path(r"^api/auth/jwt/refresh/?$", TokenRefreshView.as_view(), name="token_refresh"),
    re_path(r"^api/auth/jwt/verify/?$", TokenVerifyView.as_view(), name="token_verify"),
    re_path(r"^api/auth/jwt/blacklist/?$", TokenBlacklistView.as_view(), name="token_blacklist"),
]

if settings.DEBUG and settings.MEDIA_URL:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
