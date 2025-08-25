# rh_api/urls.py
from __future__ import annotations

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from catalogos.views import DepartamentoViewSet, PuestoViewSet
from core.views import me, ping
from empleados.views import EmpleadoViewSet

router = routers.DefaultRouter()
router.register(r"v1/departamentos", DepartamentoViewSet, basename="departamento")
router.register(r"v1/puestos", PuestoViewSet, basename="puesto")
router.register(r"v1/empleados", EmpleadoViewSet, basename="empleado")

urlpatterns = [
    # Home -> Swagger
    path("", RedirectView.as_view(url="/api/docs/", permanent=False)),
    # Admin
    path("admin/", admin.site.urls),
    # Auth (JWT)
    path("api/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/auth/me/", me, name="me"),
    # OpenAPI / Swagger
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    # Healthcheck
    path("ping/", ping, name="ping"),
    # API v1
    path("api/", include(router.urls)),
]

# Media en desarrollo
if settings.DEBUG and settings.MEDIA_URL:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
