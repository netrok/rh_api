# rh_api/urls.py
from __future__ import annotations

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import RedirectView

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
    TokenBlacklistView,
)

from core.jwt import MyTokenObtainPairView  # tu serializer personalizado
from core.views import ping, me

from catalogos.views import DepartamentoViewSet, PuestoViewSet
from empleados.views import EmpleadoViewSet

# ---------- Router /api/v1 ----------
router = DefaultRouter()
router.trailing_slash = "/?"  # diagonal final opcional
router.register(r"departamentos", DepartamentoViewSet, basename="departamento")
router.register(r"puestos", PuestoViewSet, basename="puesto")
router.register(r"empleados", EmpleadoViewSet, basename="empleado")

urlpatterns = [
    # Home -> Swagger
    path("", RedirectView.as_view(url="/api/docs/", permanent=False)),

    path("admin/", admin.site.urls),

    # OpenAPI / Swagger / ReDoc
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),

    # Core
    re_path(r"^api/ping/?$", ping, name="ping"),
    re_path(r"^api/me/?$", me, name="me"),

    # API v1 (router)
    path("api/v1/", include(router.urls)),

    # JWT principal (SimpleJWT)
    re_path(r"^api/token/?$", MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    re_path(r"^api/token/refresh/?$", TokenRefreshView.as_view(), name="token_refresh"),
    re_path(r"^api/token/verify/?$", TokenVerifyView.as_view(), name="token_verify"),
    re_path(r"^api/token/blacklist/?$", TokenBlacklistView.as_view(), name="token_blacklist"),

    # Aliases compatibles tipo Djoser (opcional)
    re_path(r"^api/auth/jwt/create/?$", MyTokenObtainPairView.as_view(), name="jwt_create_compat"),
    re_path(r"^api/auth/jwt/refresh/?$", TokenRefreshView.as_view(), name="jwt_refresh_compat"),
    re_path(r"^api/auth/jwt/verify/?$", TokenVerifyView.as_view(), name="jwt_verify_compat"),
    re_path(r"^api/auth/jwt/blacklist/?$", TokenBlacklistView.as_view(), name="jwt_blacklist_compat"),
]

if settings.DEBUG and settings.MEDIA_URL:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
