# core/views.py
from __future__ import annotations

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from .serializers import PingSerializer


@extend_schema(
    summary="Health check",
    description='Devuelve `{ "status": "ok" }` para confirmar que el servicio está arriba.',
    responses={200: OpenApiResponse(response=PingSerializer, description="Service is healthy")},
    examples=[OpenApiExample("OK", value={"status": "ok"})],
    tags=["Core"],
    operation_id="ping",
)
@api_view(["GET"])
@permission_classes([AllowAny])
def ping(request: Request) -> Response:
    """Endpoint de salud simple."""
    return Response({"status": "ok"})


@extend_schema(
    summary="Quién soy",
    description="Devuelve información básica del usuario autenticado y sus grupos.",
    responses={
        200: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Usuario autenticado",
            examples=[
                OpenApiExample(
                    "Ejemplo",
                    value={
                        "id": 1,
                        "username": "admin",
                        "email": "admin@example.com",
                        "is_staff": True,
                        "is_superuser": True,
                        "groups": ["RH_ADMIN"],
                    },
                )
            ],
        )
    },
    tags=["Core"],
    operation_id="me",
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request: Request) -> Response:
    """Información del usuario autenticado."""
    user = request.user
    groups = list(user.groups.values_list("name", flat=True))
    return Response(
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,
            "groups": groups,
        }
    )
