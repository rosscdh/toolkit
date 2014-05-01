# -*- coding: UTF-8 -*-
from django.db import models
from django.db.models.query import QuerySet

from .query import IsDeletedQuerySet


class IsDeletedManager(models.Manager):
    """
    Manager mixin to handle soft deleted objects.
    """
    def get_queryset(self):
        return IsDeletedQuerySet(self.model, using=self._db).filter(is_deleted=False)

    def all_with_deleted(self):
        return QuerySet(self.model, using=self._db)

    def deleted(self, **kwargs):
        return super(IsDeletedManager, self).get_query_set().filter(is_deleted=True).filter(**kwargs)
