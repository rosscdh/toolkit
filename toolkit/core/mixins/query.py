# -*- coding: UTF-8 -*-
from django.db.models.query import QuerySet


class IsDeletedQuerySet(QuerySet):
    """
    Mixin to override the Queryset.delete() functionality of a manager
    """
    def delete(self, *args, **kwargs):
        if 'is_deleted' in self.model._meta.get_all_field_names():
            self.update(is_deleted=True)
        else:
            super(IsDeletedQuerySet, self).delete()
