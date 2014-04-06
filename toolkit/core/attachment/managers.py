# -*- coding: utf-8 -*-
from django.db import models


class RevisionManager(models.Manager):
    def get_query_set(self):
        qs = super(RevisionManager, self).get_query_set()
        return qs.prefetch_related('reviewers', 'signers').select_related('uploaded_by')

    def current(self):
        return self.filter(is_current=True)
