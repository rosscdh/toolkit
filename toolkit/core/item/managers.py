# -*- coding: UTF-8 -*-
import operator

from django.db import models

from toolkit.core.mixins import IsDeletedManager

from .query import ItemQuerySet


class ItemManager(IsDeletedManager):
    def get_queryset(self):
        return ItemQuerySet(self.model, using=self._db).filter(is_deleted=False).select_related('matter', 'latest_revision')

    def requested(self, **kwargs):
        return self.get_queryset().requested(**kwargs)

    def my_requests(self, user, completed=False):
        queries = []

        compl_operator = operator.or_ if completed else operator.and_

        # document request
        queries += [
            models.Q(is_complete=completed) &
            models.Q(responsible_party=user) &
            models.Q(is_requested=True)
        ]

        # review requests
        queries += [
            models.Q(revision__is_current=True) &
            models.Q(revision__reviewdocument__reviewers__in=[user]) &
            reduce(compl_operator, [
                models.Q(is_complete=completed),
                models.Q(revision__reviewdocument__is_complete=completed)
            ])
        ]

        # signing requests
        queries += [
            models.Q(revision__is_current=True) &
            models.Q(revision__signdocument__signers__in=[user]) &
            reduce(compl_operator, [
                models.Q(is_complete=completed),
                models.Q(revision__signdocument__is_complete=completed)
            ])
        ]

        return self.get_queryset().filter(reduce(operator.or_, queries))
