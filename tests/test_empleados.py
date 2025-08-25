import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient


@pytest.fixture
def user(db):
    return User.objects.create_user(username="tester", password="secret123")


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def auth_client(user):
    c = APIClient()
    c.force_authenticate(user=user)
    return c


@pytest.fixture
def cat_base(auth_client):
    # Crea catálogo base
    dep = auth_client.post(
        "/api/v1/departamentos/",
        {"nombre": "TI", "clave": "TI", "activo": True},
        format="json",
    ).json()
    pst = auth_client.post(
        "/api/v1/puestos/",
        {
            "nombre": "Analista",
            "clave": "ANL",
            "departamento": dep["id"],
            "activo": True,
        },
        format="json",
    ).json()
    return dep, pst


def test_empleado_crud_y_soft_restore(db, auth_client, cat_base):
    dep, pst = cat_base
    # Crear
    e = auth_client.post(
        "/api/v1/empleados/",
        {
            "num_empleado": "E001",
            "nombres": "Juan",
            "apellido_paterno": "Perez",
            "curp": "ABCD001231HDFLRN09",
            "rfc": "ABC010203XYZ",
            "nss": "12345678901",
            "email": "jp@example.com",
            "departamento": dep["id"],
            "puesto": pst["id"],
            "activo": True,
        },
        format="json",
    )
    assert e.status_code in (200, 201), e.content
    emp = e.json()

    # Listar
    lst = auth_client.get("/api/v1/empleados/")
    assert lst.status_code == 200
    assert any(x["id"] == emp["id"] for x in lst.json())

    # Soft delete
    sd = auth_client.post(f"/api/v1/empleados/{emp['id']}/soft-delete/")
    assert sd.status_code == 204

    # Por defecto no debe aparecer
    lst2 = auth_client.get("/api/v1/empleados/")
    assert all(x["id"] != emp["id"] for x in lst2.json())

    # Con include_deleted aparece
    lst3 = auth_client.get("/api/v1/empleados/?include_deleted=1")
    assert any(x["id"] == emp["id"] for x in lst3.json())

    # Restaurar
    rs = auth_client.post(f"/api/v1/empleados/{emp['id']}/restore/")
    assert rs.status_code == 200
    # Debe volver a aparecer en list
    lst4 = auth_client.get("/api/v1/empleados/")
    assert any(x["id"] == emp["id"] for x in lst4.json())


def test_export_excel(db, auth_client, cat_base):
    dep, pst = cat_base
    # Crear mínimo
    auth_client.post(
        "/api/v1/empleados/",
        {
            "num_empleado": "E002",
            "nombres": "Ana",
            "apellido_paterno": "Gomez",
            "curp": "WXYZ001231MDFLRN01",
            "rfc": "WXY010203ABC",
            "nss": "10987654321",
            "email": "ana@example.com",
            "departamento": dep["id"],
            "puesto": pst["id"],
            "activo": True,
        },
        format="json",
    )

    resp = auth_client.get("/api/v1/empleados/export-excel")
    assert resp.status_code == 200
    assert (
        resp["Content-Type"]
        == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    # Verifica que hay bytes (XLSX)
    content = (
        b"".join(resp.streaming_content)
        if hasattr(resp, "streaming_content")
        else resp.content
    )
    assert len(content) > 1000  # un XLSX mínimo debe pesar > 1KB
