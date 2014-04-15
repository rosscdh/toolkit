# -*- coding: UTF-8 -*-
from django.db.models.query import QuerySet
from django.db.models import signals


class IsDeletedQuerySet(QuerySet):
    """
    Mixin to override the Queryset.delete() functionality of a manager
    """
    def delete(self, *args, **kwargs):
        if 'is_deleted' in self.model._meta.get_all_field_names():
            signals.pre_delete.send(
                sender=self.__class__, instance=self, using=self.using
            )
    
            self.update(is_deleted=True)

            signals.post_delete.send(
                sender=self.__class__, instance=self, using=self.using
            )

        else:
            super(IsDeletedQuerySet, self).delete()
