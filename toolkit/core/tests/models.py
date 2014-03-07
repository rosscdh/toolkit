from django.db import models

from toolkit.core.mixins import IsDeletedMixin


class Thing(IsDeletedMixin, models.Model):
    name = models.CharField(max_length=100)


class ActivityTester(models.Model):
    name = models.CharField(max_length=100)
    type = models.PositiveSmallIntegerField(choices=((1, 'actor'), (2, 'action_object'), (3, 'target')))

    def __unicode__(self):
        return "%s - %s" % (self.type, self.name)
