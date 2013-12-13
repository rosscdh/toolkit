from django.db import models


class WorkspaceManager(models.Manager):
    def mine(self, user):
        return super(WorkspaceManager, self).get_query_set().filter(participants=user)
