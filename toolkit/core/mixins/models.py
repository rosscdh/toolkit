# -*- coding: utf-8 -*-
from django.db import models
from django.db.models import signals

from .managers import IsDeletedManager


class IsDeletedMixin(models.Model):
    """
    Abstract model to handle soft deletion.
    """
    is_deleted = models.BooleanField(default=False)

    objects = IsDeletedManager()

    class Meta:
        abstract = True

    def delete(self, *args, **kwargs):
        signals.pre_delete.send(
            sender=self.__class__, instance=self, using=self.__class__.objects.using
        )

        self.is_deleted = True
        self.save(update_fields=['is_deleted'])

        signals.post_delete.send(
            sender=self.__class__, instance=self, using=self.__class__.objects.using
        )