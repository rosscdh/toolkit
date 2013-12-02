# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from django.db import models
from django.template import loader
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify

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
        return u'83(b) for %s' % self.client_name

    @property
    def client_name(self):
        return self.data.get('client_full_name', None)

    @property
    def filing_date(self):
        return self.transfer_date + timedelta(days=30)

    @property
    def transfer_date(self):
        return datetime.strptime(self.data.get('date_of_property_transfer', None), '%Y-%m-%d').date()

    @property
    def filename(self):
        return slugify('83b-{company}-{user}'.format(company=self.workspace, user=self.user.get_full_name() or self.user.username))

    @property
    def template(self):
        return loader.get_template(self.template_name)

    def get_absolute_url(self):
        return reverse('eightythreeb:view')

    def html(self):
        context = loader.Context(self.data)
        source = self.template.render(context)
        #doc = Lenker(source=source)
        return source #doc.render(context=self.data)
