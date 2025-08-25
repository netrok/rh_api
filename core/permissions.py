# core/permissions.py
from __future__ import annotations

from typing import Set

from django.contrib.auth.models import AbstractBaseUser, AnonymousUser
from rest_framework.permissions import SAFE_METHODS, BasePermission
from rest_framework.request import Request

# Grupos estándar del proyecto
GROUP_RH_ADMIN = "RH_ADMIN"
GROUP_RH_EDITOR = "RH_EDITOR"


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
    True si el usuario es superuser o pertenece a cualquiera de los grupos dados.
    """
    if not user or isinstance(user, AnonymousUser):
        return False
    if getattr(user, "is_superuser", False):
        return True
    return bool(_group_names(user).intersection(names))


class _BaseRBAC(BasePermission):
    """
    Base para permisos de lectura/escritura con RBAC.
    - Lectura: requiere autenticación (SAFE_METHODS).
    - Escritura: la decide `can_write()`.
    """

    write_groups: tuple[str, ...] = ()

    def has_permission(self, request: Request, view) -> bool:  # type: ignore[override]
        user = request.user
        if request.method in SAFE_METHODS:
            return bool(user and user.is_authenticated)
        return self.can_write(user)

    # Mantén coherencia a nivel objeto (PUT/PATCH/DELETE detail)
    def has_object_permission(self, request: Request, view, obj) -> bool:  # type: ignore[override]
        return self.has_permission(request, view)

    def can_write(self, user: AbstractBaseUser | AnonymousUser) -> bool:
        return in_groups(user, *self.write_groups)


class IsCatalogAdminOrReadOnly(_BaseRBAC):
    """
    Catálogos:
      - Lectura: cualquier usuario autenticado.
      - Escritura: solo RH_ADMIN.
    """

    write_groups = (GROUP_RH_ADMIN,)


class IsEmpleadoEditorOrReadOnly(_BaseRBAC):
    """
    Empleados:
      - Lectura: autenticado.
      - Escritura (create/update): RH_EDITOR o RH_ADMIN.
      - Soft-delete/restore: protégelas adicionalmente con IsRHAdmin en las actions.
    """

    write_groups = (GROUP_RH_EDITOR, GROUP_RH_ADMIN)


class IsRHAdmin(BasePermission):
    """Solo RH_ADMIN (o superuser)."""

    def has_permission(self, request: Request, view) -> bool:  # type: ignore[override]
        return in_groups(request.user, GROUP_RH_ADMIN)

    def has_object_permission(self, request: Request, view, obj) -> bool:  # type: ignore[override]
        return self.has_permission(request, view)
