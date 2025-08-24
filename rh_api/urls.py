# rh_api/urls.py
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView  # <-- IMPORT AL TOPE
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from catalogos.views import DepartamentoViewSet, PuestoViewSet
from core.views import ping
from empleados.views import EmpleadoViewSet

router = routers.DefaultRouter()
router.register(r"v1/departamentos", DepartamentoViewSet, basename="departamento")
router.register(r"v1/puestos", PuestoViewSet, basename="puesto")
router.register(r"v1/empleados", EmpleadoViewSet, basename="empleado")

urlpatterns = [
    path("", RedirectView.as_view(url="/api/docs/", permanent=False)),
    path("admin/", admin.site.urls),
    # Auth (JWT)
    path("api/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # OpenAPI / Swagger
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    # Healthcheck
    path("ping/", ping, name="ping"),
    # API
    path("api/", include(router.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
