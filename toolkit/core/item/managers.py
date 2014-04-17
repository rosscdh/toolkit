# -*- coding: UTF-8 -*-
import operator

from django.db import models

from toolkit.core.mixins import IsDeletedManager

from .query import ItemQuerySet


class ItemManager(IsDeletedManager):
    def get_queryset(self):
        return ItemQuerySet(self.model, using=self._db).filter(is_deleted=False).select_related('latest_revision')

    def requested(self, **kwargs):
        return self.get_queryset().requested(**kwargs)

    def my_requests(self, user):
        queries = []

        # upload requests
        queries += [models.Q(responsible_party=user) & models.Q(is_requested=True)]
        # review requests
        queries += [models.Q(revision__is_current=True) & models.Q(revision__reviewers__in=[user])]
        # signing requests
        queries += [models.Q(revision__is_current=True) & models.Q(revision__signers__in=[user])]

        return self.get_queryset().filter(reduce(operator.or_, queries))
