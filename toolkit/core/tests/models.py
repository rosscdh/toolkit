from django.db import models

from toolkit.core.mixins import IsDeletedMixin


class Thing(IsDeletedMixin, models.Model):
    name = models.CharField(max_length=100)
