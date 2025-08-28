from __future__ import annotations

from django.db import models
from django.utils import timezone


class SoftDeleteQuerySet(models.QuerySet):
    """QuerySet con soporte para soft-delete/bulk."""

    def delete(self):
        """Soft-delete en lote (marca deleted_at)."""
        return super().update(deleted_at=timezone.now())

    def hard_delete(self):
        """Borrado físico en lote."""
        return super().delete()

    def restore(self):
        """Restauración en lote."""
        return super().update(deleted_at=None)

    def alive(self):
        """Solo registros no borrados."""
        return self.filter(deleted_at__isnull=True)

    def dead(self):
        """Solo registros marcados como borrados."""
        return self.filter(deleted_at__isnull=False)


class SoftDeleteManager(models.Manager):
    """Manager por defecto: solo vivos (alive)."""

    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).alive()

    # Atajos útiles
    def with_deleted(self):
        return SoftDeleteQuerySet(self.model, using=self._db)

    def only_deleted(self):
        return SoftDeleteQuerySet(self.model, using=self._db).dead()


class AllObjectsManager(models.Manager):
    """Manager alterno sin filtro (incluye vivos y borrados)."""

    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db)


class SoftDeleteModel(models.Model):
    """Mixin abstracto para soft-delete con helpers y dos managers."""
    deleted_at = models.DateTimeField(null=True, blank=True)

    # Manager por defecto: solo vivos
    objects = SoftDeleteManager()
    # Manager alterno: incluye borrados
    all_objects = AllObjectsManager()

    class Meta:
        abstract = True

    # Métodos de instancia
    def delete(self, using=None, keep_parents=False):
        """Soft-delete (marca deleted_at)."""
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at"])

    def restore(self):
        """Restaurar registro borrado lógicamente."""
        self.deleted_at = None
        self.save(update_fields=["deleted_at"])

    def hard_delete(self, using=None, keep_parents=False):
        """Borrado físico del registro."""
        return super().delete(using=using, keep_parents=keep_parents)
