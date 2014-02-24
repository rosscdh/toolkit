# -*- coding: UTF-8 -*-
from django.db import models

from .query import IsDeletedQuerySet


class IsDeletedManager(models.Manager):
    """
    Manager mixin to handle soft deleted objects.
    """
    def get_queryset(self):
        return IsDeletedQuerySet(self.model, using=self._db).filter(is_deleted=False)

    def deleted(self):
        return super(IsDeletedManager, self).get_query_set().filter(is_deleted=True)
