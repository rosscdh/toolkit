# -*- coding: UTF-8 -*-
from itertools import chain
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
        # queries = []

        compl_operator = operator.or_ if completed else operator.and_

        # document request
        document_requests = self.get_queryset().filter(
            models.Q(is_complete=completed) &
            models.Q(responsible_party=user) &
            models.Q(is_requested=True)
        )

        # review requests
        review_requests = self.get_queryset().filter(
            models.Q(revision__is_current=True) &
            models.Q(revision__reviewers__in=[user]) &
            models.Q(revision__reviewdocument__reviewers__in=[user]) &
            reduce(compl_operator, [
                models.Q(is_complete=completed),
                models.Q(revision__reviewdocument__is_complete=completed)
            ])
        )

        # signing requests
        signing_queries = []
        signing_queries += [models.Q(revision__is_current=True)]
        signing_queries += [models.Q(revision__signers__in=[user])]
        if not completed:
            signing_queries += [
                reduce(compl_operator, [
                    models.Q(is_complete=completed),
                    models.Q(revision__signdocument__is_complete=completed)
                ])
            ]

        signing_requests = []
        for item in self.get_queryset().filter(reduce(operator.and_, signing_queries)):
            if completed:
                if item.latest_revision.primary_signdocument and item.latest_revision.primary_signdocument.has_signed(user):
                    signing_requests.append(item)
                elif item.is_complete:
                    signing_requests.append(item)
            else:
                if item.latest_revision.primary_signdocument and not item.latest_revision.primary_signdocument.has_signed(user):
                    signing_requests.append(item)

        return list(chain(document_requests, review_requests, signing_requests))
