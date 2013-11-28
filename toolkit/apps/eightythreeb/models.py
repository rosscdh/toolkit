# -*- coding: utf-8 -*-
from django.db import models
from django.core.urlresolvers import reverse

from jsonfield import JSONField


class EightyThreeB(models.Model):
    """
    83b Form to be associated with a Workspace and a particular user
    """
    workspace = models.ForeignKey('workspace.Workspace')
    user = models.ForeignKey('auth.User')
    data = JSONField(default={})

    def __unicode__(self):
        return u'83b for %s' % self.user.get_full_name()

    def get_absolute_url(self):
        return reverse('eightythreeb:view')