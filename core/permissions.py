# core/permissions.py
from __future__ import annotations

from typing import Iterable, Set, Optional, Union

from django.contrib.auth.models import AbstractBaseUser, AnonymousUser
from rest_framework.permissions import SAFE_METHODS, BasePermission
from rest_framework.request import Request

# ──────────────────────────────────────────────────────────────────────────────
READ_REQUIRES_AUTH = True
ALLOW_STAFF_WRITE = True

# ──────────────────────────────────────────────────────────────────────────────
GROUP_SUPERADMIN = "SuperAdmin"
GROUP_ADMIN = "Admin"
GROUP_RRHH = "RRHH"
GROUP_GERENTE = "Gerente"
GROUP_SUPERVISOR = "Supervisor"
GROUP_USUARIO = "Usuario"

ALIAS_PAIRS = {
    "RH_ADMIN": GROUP_ADMIN,
    "RH_EDITOR": GROUP_RRHH,
}

def _with_aliases(names: Iterable[str]) -> Set[str]:
    expanded: Set[str] = set(names)
    for n in list(expanded):
        if n in ALIAS_PAIRS:
            expanded.add(ALIAS_PAIRS[n])
        for k, v in ALIAS_PAIRS.items():
            if v == n:
                expanded.add(k)
    return expanded

def _group_names(user: "AbstractBaseUser") -> Set[str]:
    cache_attr = "_group_names_cache"
    names = getattr(user, cache_attr, None)
    if names is None:
        names = set(user.groups.values_list("name", flat=True))
        setattr(user, cache_attr, names)
    return names

def in_groups(user: Union["AbstractBaseUser", "AnonymousUser", None], *names: str) -> bool:
    if not user or isinstance(user, AnonymousUser):
        return False
    if getattr(user, "is_superuser", False):
        return True
    target = _with_aliases(names)
    return bool(_group_names(user).intersection(target))

# ──────────────────────────────────────────────────────────────────────────────
class IsReadOnly(BasePermission):
    def has_permission(self, request: Request, view) -> bool:
        return request.method in SAFE_METHODS

class _BaseRBAC(BasePermission):
    write_groups: tuple[str, ...] = ()

    def has_permission(self, request: Request, view) -> bool:  # type: ignore[override]
        user = request.user
        if request.method in SAFE_METHODS:
            return bool(user and user.is_authenticated) if READ_REQUIRES_AUTH else True
        return self.can_write(user)

    def has_object_permission(self, request: Request, view, obj) -> bool:  # type: ignore[override]
        return self.has_permission(request, view)

    def can_write(self, user: Union["AbstractBaseUser", "AnonymousUser", None]) -> bool:
        if ALLOW_STAFF_WRITE and getattr(user, "is_staff", False):
            return True
        return in_groups(user, *self.write_groups)

class IsCatalogAdminOrReadOnly(_BaseRBAC):
    write_groups = (GROUP_ADMIN,)

class IsEmpleadoEditorOrReadOnly(_BaseRBAC):
    write_groups = (GROUP_RRHH, GROUP_ADMIN)

class IsRHAdmin(BasePermission):
    def has_permission(self, request: Request, view) -> bool:  # type: ignore[override]
        return in_groups(request.user, GROUP_ADMIN)
    def has_object_permission(self, request: Request, view, obj) -> bool:  # type: ignore[override]
        return self.has_permission(request, view)

class IsRRHHOrAdmin(BasePermission):
    def has_permission(self, request: Request, view) -> bool:
        return in_groups(request.user, GROUP_SUPERADMIN, GROUP_ADMIN, GROUP_RRHH)

class IsManagerOrAbove(BasePermission):
    def has_permission(self, request: Request, view) -> bool:
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
