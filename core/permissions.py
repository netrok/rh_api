# core/permissions.py
from __future__ import annotations

from typing import Iterable, Set

from django.contrib.auth.models import AbstractBaseUser, AnonymousUser
from rest_framework.permissions import SAFE_METHODS, BasePermission
from rest_framework.request import Request

# ──────────────────────────────────────────────────────────────────────────────
# Roles/Grupos estándar del proyecto
GROUP_SUPERADMIN = "SuperAdmin"
GROUP_ADMIN = "Admin"
GROUP_RRHH = "RRHH"
GROUP_GERENTE = "Gerente"
GROUP_SUPERVISOR = "Supervisor"
GROUP_USUARIO = "Usuario"

# Alias legacy para mantener compatibilidad con nombres antiguos
#   RH_ADMIN  ≈ Admin
#   RH_EDITOR ≈ RRHH
ALIAS_PAIRS = {
    "RH_ADMIN": GROUP_ADMIN,
    "RH_EDITOR": GROUP_RRHH,
}

# ──────────────────────────────────────────────────────────────────────────────
def _with_aliases(names: Iterable[str]) -> Set[str]:
    """
    Devuelve el conjunto de nombres + sus alias (en ambos sentidos).
    Si pasas 'RH_ADMIN', incluye también 'Admin', y viceversa.
    """
    expanded: Set[str] = set(names)
    for n in list(expanded):
        # Directo: clave -> valor
        if n in ALIAS_PAIRS:
            expanded.add(ALIAS_PAIRS[n])
        # Inverso: valor -> clave
        for k, v in ALIAS_PAIRS.items():
            if v == n:
                expanded.add(k)
    return expanded


def _group_names(user: AbstractBaseUser) -> Set[str]:
    """
    Devuelve los nombres de grupos del usuario con caché simple en el objeto.
    Evita hits repetidos a la BD dentro del mismo request.
    """
    cache_attr = "_group_names_cache"
    names = getattr(user, cache_attr, None)
    if names is None:
        names = set(user.groups.values_list("name", flat=True))
        setattr(user, cache_attr, names)
    return names


def in_groups(user: AbstractBaseUser | AnonymousUser, *names: str) -> bool:
    """
    True si el usuario es superuser o pertenece a cualquiera de los grupos dados
    (considerando alias legacy).
    """
    if not user or isinstance(user, AnonymousUser):
        return False
    if getattr(user, "is_superuser", False):
        return True
    target = _with_aliases(names)
    return bool(_group_names(user).intersection(target))


# ──────────────────────────────────────────────────────────────────────────────
# Permisos base y compuestos

class IsReadOnly(BasePermission):
    """Permite sólo métodos de lectura (GET/HEAD/OPTIONS)."""
    def has_permission(self, request: Request, view) -> bool:
        return request.method in SAFE_METHODS


class _BaseRBAC(BasePermission):
    """
    Base para permisos de lectura/escritura con RBAC.
    - Lectura: requiere autenticación (SAFE_METHODS).
    - Escritura: la decide `can_write()` con base en `write_groups`.
    """
    write_groups: tuple[str, ...] = ()

    def has_permission(self, request: Request, view) -> bool:  # type: ignore[override]
        user = request.user
        if request.method in SAFE_METHODS:
            return bool(user and user.is_authenticated)
        return self.can_write(user)

    # Coherencia a nivel objeto (PUT/PATCH/DELETE detail)
    def has_object_permission(self, request: Request, view, obj) -> bool:  # type: ignore[override]
        return self.has_permission(request, view)

    def can_write(self, user: AbstractBaseUser | AnonymousUser) -> bool:
        return in_groups(user, *self.write_groups)


# ── Catálogos ─────────────────────────────────────────────────────────────────
class IsCatalogAdminOrReadOnly(_BaseRBAC):
    """
    Catálogos:
      - Lectura: cualquier usuario autenticado.
      - Escritura: sólo Admin (o superuser).
    *Si quieres que RRHH también edite, añade GROUP_RRHH a write_groups.
    """
    write_groups = (GROUP_ADMIN,)


# ── Empleados ─────────────────────────────────────────────────────────────────
class IsEmpleadoEditorOrReadOnly(_BaseRBAC):
    """
    Empleados:
      - Lectura: autenticado.
      - Escritura: RRHH o Admin (o superuser).
      - Para acciones sensibles (soft-delete/restore), combina con IsRHAdmin.
    """
    write_groups = (GROUP_RRHH, GROUP_ADMIN)


class IsRHAdmin(BasePermission):
    """Sólo Admin (o superuser)."""
    def has_permission(self, request: Request, view) -> bool:  # type: ignore[override]
        return in_groups(request.user, GROUP_ADMIN)

    def has_object_permission(self, request: Request, view, obj) -> bool:  # type: ignore[override]
        return self.has_permission(request, view)


# ── Atajos compuestos usados en tus ViewSets ──────────────────────────────────
class IsRRHHOrAdmin(BasePermission):
    """SuperAdmin/Admin/RRHH."""
    def has_permission(self, request, view):
        return in_groups(request.user, GROUP_SUPERADMIN, GROUP_ADMIN, GROUP_RRHH)


class IsManagerOrAbove(BasePermission):
    """SuperAdmin/Admin/RRHH/Gerente."""
    def has_permission(self, request, view):
        return in_groups(request.user, GROUP_SUPERADMIN, GROUP_ADMIN, GROUP_RRHH, GROUP_GERENTE)


__all__ = [
    "IsReadOnly",
    "IsCatalogAdminOrReadOnly",
    "IsEmpleadoEditorOrReadOnly",
    "IsRHAdmin",
    "IsRRHHOrAdmin",
    "IsManagerOrAbove",
    "in_groups",
    "GROUP_SUPERADMIN",
    "GROUP_ADMIN",
    "GROUP_RRHH",
    "GROUP_GERENTE",
    "GROUP_SUPERVISOR",
    "GROUP_USUARIO",
]
