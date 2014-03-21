from django.db import models


class RevisionManager(models.Manager):
    def current(self):
        return self.filter(is_current=True)
