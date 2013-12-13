from django.db import models


class WorkspaceManager(models.Manager):
    def mine(self, user):
        if not user.is_authenticated():
            return []

        return super(WorkspaceManager, self).get_query_set().filter(participants__in=[user])
