# -*- coding: utf-8 -*-
from django.db import models
from django.template import loader
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify

from uuidfield import UUIDField
from jsonfield import JSONField
from datetime import datetime, timedelta

from .markers import EightyThreeBSignalMarkers
EIGHTYTHREEB_STATUS = EightyThreeBSignalMarkers().named_tuple(name='EIGHTYTHREEB_STATUS')

from .mixins import StatusMixin
from .managers import EightyThreeBManager


class EightyThreeB(StatusMixin, models.Model):
    """
    83b Form to be associated with a Workspace and a particular user
    """
    STATUS_83b = EIGHTYTHREEB_STATUS
    template_name = 'eightythreeb/eightythreeb.html'

    slug = UUIDField(auto=True, db_index=True)
    workspace = models.ForeignKey('workspace.Workspace')
    user = models.ForeignKey('auth.User')
    data = JSONField(default={})

    status = models.IntegerField(choices=EIGHTYTHREEB_STATUS.get_choices(), default=EIGHTYTHREEB_STATUS.lawyer_complete_form, db_index=True)

    objects = EightyThreeBManager()

    def __unicode__(self):
        return u'83(b) for %s' % self.client_name

    @property
    def tool_slug(self):
        return '83b-election-letters'

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
    def tracking_code(self):
        return self.data.get('tracking_code')

    @tracking_code.setter
    def tracking_code(self, value):
        self.data['tracking_code'] = value

    @property
    def filename(self):
        return slugify('83b-{company}-{user}'.format(company=self.workspace, user=self.user.get_full_name() or self.user.username))

    @property
    def template(self):
        return loader.get_template(self.template_name)

    @property
    def base_signal(self):
        from .signals import base_83b_signal
        return base_83b_signal

    def get_absolute_url(self):
        return reverse('workspace:tool_object_preview', kwargs={'workspace': self.workspace.slug, 'tool': self.workspace.tools.filter(slug=self.tool_slug).first().slug, 'slug': self.slug})

    def html(self):
        context = loader.Context(self.data)
        source = self.template.render(context)
        # doc = Lenker(source=source)
        return source  # doc.render(context=self.data)
