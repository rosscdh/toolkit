from django.db import models

from toolkit.apps.eightythreeb.managers import isDeletedQuerySet


class WorkspaceManager(models.Manager):
    def get_query_set(self):
        return isDeletedQuerySet(self.model, using=self._db).filter(is_deleted=False)

    def mine(self, user):
        if not user.is_authenticated():
            return []

        return self.get_query_set().filter(participants__in=[user])

    def deleted(self):
        return super(WorkspaceManager, self).get_query_set().filter(is_deleted=True)