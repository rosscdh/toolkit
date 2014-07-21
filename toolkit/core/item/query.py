# -*- coding: UTF-8 -*-
from django.db import models
from django.db.models.query import QuerySet


class ItemQuerySet(QuerySet):
    def mine(self, user, **kwargs):
        return self.filter(responsible_party=user, **kwargs)

    def requested(self, **kwargs):
        return self.filter(is_requested=True, **kwargs)
