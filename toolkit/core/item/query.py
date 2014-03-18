# -*- coding: UTF-8 -*-
from django.db import models
from django.db.models.query import QuerySet


class ItemQuerySet(QuerySet):
    def mine(self, user, **kwargs):
        return self.filter(responsible_party=user, **kwargs)

    def needs_review(self, user):
        return self.filter(models.Q(revision__is_current=True) & models.Q(revision__reviewers__in=[user]))

    def needs_signature(self, user):
        return self.filter(models.Q(revision__is_current=True) & models.Q(revision__signatories__in=[user]))

    def needs_upload(self, user):
        return self.filter(models.Q(responsible_party=user) & models.Q(is_requested=True))

    def requested(self, **kwargs):
        return self.filter(is_requested=True, **kwargs)
