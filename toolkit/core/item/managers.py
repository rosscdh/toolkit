# -*- coding: UTF-8 -*-
from toolkit.core.mixins import IsDeletedManager

from .query import ItemQuerySet


class ItemManager(IsDeletedManager):
    def mine(self, user, **kwargs):
        return self.get_queryset().mine(user, **kwargs)

    def requested(self, **kwargs):
        return self.get_queryset().requested(**kwargs)

    def get_queryset(self):
        return ItemQuerySet(self.model, using=self._db).filter(is_deleted=False)
