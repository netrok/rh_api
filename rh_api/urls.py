# rh_api/urls.py
from __future__ import annotations

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
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

from core.jwt import MyTokenObtainPairView
from core.views import ping, me

from catalogos.views import (
    DepartamentoViewSet,
    PuestoViewSet,
    TurnoViewSet,
    HorarioViewSet,
)
from empleados.views import EmpleadoViewSet

# ---------- Router /api/v1 ----------
router = DefaultRouter()
router.trailing_slash = "/?"  # diagonal final opcional
router.register(r"departamentos", DepartamentoViewSet, basename="departamento")
router.register(r"puestos", PuestoViewSet, basename="puesto")
router.register(r"turnos", TurnoViewSet, basename="turno")
router.register(r"horarios", HorarioViewSet, basename="horario")
router.register(r"empleados", EmpleadoViewSet, basename="empleado")

urlpatterns = [
    # Home -> Swagger
    path("", RedirectView.as_view(url="/api/docs/", permanent=False)),

    # Admin
    path("admin/", admin.site.urls),

    # OpenAPI / Swagger / ReDoc
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),

    # Core
    path("api/ping/", ping, name="ping"),
    path("api/me/", me, name="me"),

    # API v1 (router)
    path("api/v1/", include(router.urls)),

    # JWT (SimpleJWT)
    path("api/token/", MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("api/token/blacklist/", TokenBlacklistView.as_view(), name="token_blacklist"),

    # Aliases compatibles tipo Djoser (opcional)
    path("api/auth/jwt/create/", MyTokenObtainPairView.as_view(), name="jwt_create_compat"),
    path("api/auth/jwt/refresh/", TokenRefreshView.as_view(), name="jwt_refresh_compat"),
    path("api/auth/jwt/verify/", TokenVerifyView.as_view(), name="jwt_verify_compat"),
    path("api/auth/jwt/blacklist/", TokenBlacklistView.as_view(), name="jwt_blacklist_compat"),
]

# Media en DEBUG
if settings.DEBUG and settings.MEDIA_URL:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
