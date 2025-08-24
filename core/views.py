# core/views.py
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from .serializers import PingSerializer


@extend_schema(
    summary="Health check",
    description="Devuelve `{ status: 'ok' }` para confirmar que el servicio está arriba.",
    responses={
        200: OpenApiResponse(response=PingSerializer, description="Service is healthy")
    },
    examples=[OpenApiExample("OK", value={"status": "ok"})],
    tags=["Core"],
    operation_id="ping",
)
@api_view(["GET"])
@permission_classes([AllowAny])
def ping(request: Request) -> Response:
    """Endpoint de salud simple."""
    return Response({"status": "ok"})
