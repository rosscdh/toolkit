# -*- coding: utf-8 -*-
from django.db import models
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify

from uuidfield import UUIDField
from jsonfield import JSONField

from rulez import registry as rulez_registry

from toolkit.apps.workspace.mixins import WorkspaceToolModelMixin

from .markers import EngagementLetterMarkers
ENGAGEMENTLETTER_STATUS = EngagementLetterMarkers().named_tuple(name='ENGAGEMENTLETTER_STATUS')

from .mixins import (IsDeletedMixin,
                     StatusMixin,
                     HTMLMixin)


class EngagementLetter(StatusMixin, IsDeletedMixin, HTMLMixin, WorkspaceToolModelMixin, models.Model):
    """
    Enagement Letter model
    """
    STATUS = ENGAGEMENTLETTER_STATUS

    pdf_template_name = 'engageletter/engageletter.html'  # @TODO what is this doing here?

    slug = UUIDField(auto=True, db_index=True)
    workspace = models.ForeignKey('workspace.Workspace')
    user = models.ForeignKey('auth.User')

    data = JSONField(default={})

    filing_date = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True)  # remove the null=True after migrations 0002,0003 applied
    transfer_date = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True)  # remove the null=True after migrations 0002,0003 applied

    status = models.IntegerField(choices=ENGAGEMENTLETTER_STATUS.get_choices(), default=ENGAGEMENTLETTER_STATUS.lawyer_setup_template, db_index=True)

    _markers = None

    def __unicode__(self):
        return u'Engagement Letter for %s' % self.client_name

    @property
    def tool_slug(self):
        return 'engagement-letters'

    @property
    def markers(self):
        if self._markers is None:
            self._markers = EngagementLetterMarkers(tool=self)
        return self._markers

    @property
    def base_signal(self):
        from toolkit.apps.workspace.signals import base_signal
        return base_signal

    @property
    def is_complete(self):
        return self.status == self.STATUS.complete

    @property
    def client_name(self):
        return self.data.get('client_full_name', None)

    @property
    def filename(self):
        return slugify('engageletter-{company}-{user}'.format(company=self.workspace, user=self.user.get_full_name() or self.user.username))

    @property
    def company_name(self):
        return self.data.get('company_name', self.workspace.name)

    def get_absolute_url(self):
        return reverse('workspace:tool_object_preview', kwargs={'workspace': self.workspace.slug, 'tool': self.workspace.tools.filter(slug=self.tool_slug).first().slug, 'slug': self.slug})

    def get_edit_url(self):
        return reverse('workspace:tool_object_edit', kwargs={'workspace': self.workspace.slug, 'tool': self.workspace.tools.filter(slug=self.tool_slug).first().slug, 'slug': self.slug})

    def can_read(self, user):
        return user in self.workspace.participants.all()

    def can_edit(self, user):
        return user in self.workspace.participants.all()

    def can_delete(self, user):
        return user.profile.is_lawyer and user in self.workspace.participants.all()

rulez_registry.register("can_read", EngagementLetter)
rulez_registry.register("can_edit", EngagementLetter)
rulez_registry.register("can_delete", EngagementLetter)

from .signals import *
