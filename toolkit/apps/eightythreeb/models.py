# -*- coding: utf-8 -*-
from django.db import models
from django.template import loader
from django.core.urlresolvers import reverse

#from lenker import Lenker

from jsonfield import JSONField


class EightyThreeB(models.Model):
    """
    83b Form to be associated with a Workspace and a particular user
    """
    template_name = 'eightythreeb/eightythreeb.html'

    workspace = models.ForeignKey('workspace.Workspace')
    user = models.ForeignKey('auth.User')
    data = JSONField(default={})

    def __unicode__(self):
        return u'83b for %s' % self.user.get_full_name()

    def get_absolute_url(self):
        return reverse('eightythreeb:view')

    @property
    def filename(self):
        return '{company}-{user}-83b.pdf'.format(company=self.workspace, user=self.user.get_full_name() or self.user.username)

    @property
    def template(self):
        return loader.get_template(self.template_name)

    def html(self):
        context = loader.Context(self.data)
        source = self.template.render(context)
        #doc = Lenker(source=source)
        return source #doc.render(context=self.data)