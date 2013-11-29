# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from jsonfield import JSONField

from django.db import models
from django.core.urlresolvers import reverse


class EightyThreeB(models.Model):
    """
    83b Form to be associated with a Workspace and a particular user
    """
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

    def get_absolute_url(self):
        return reverse('eightythreeb:view')