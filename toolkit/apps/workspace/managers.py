# -*- coding: UTF-8 -*-
from django.db import models


class WorkspaceManager(models.Manager):
    def get_query_set(self):
        return super(WorkspaceManager, self).get_query_set().filter(is_deleted=False)

    def mine(self, user):
        if not user.is_authenticated():
            return []

        return self.get_query_set().filter(participants__in=[user])

    def deleted(self, **kwargs):
        return super(WorkspaceManager, self).get_query_set().filter(is_deleted=True, **kwargs)
