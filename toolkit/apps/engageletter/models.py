# -*- coding: utf-8 -*-
from django.db import models
from django.template import loader
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify

from datetime import datetime
from jsonfield import JSONField
from uuidfield import UUIDField

from rulez import registry as rulez_registry

from toolkit.apps.workspace.signals import base_signal
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
    template_source_body = 'engageletter/doc/body.html' # used in override self.html

    slug = UUIDField(auto=True, db_index=True)
    workspace = models.ForeignKey('workspace.Workspace')
    user = models.ForeignKey('auth.User')

    # header = models.TextField(default='', blank=True)  # store an instance of the workspace.lawyer header template
    # letter = models.TextField(default='', blank=True)  # store the rendered html

    data = JSONField(default={})

    status = models.IntegerField(choices=ENGAGEMENTLETTER_STATUS.get_choices(), default=ENGAGEMENTLETTER_STATUS.lawyer_complete_form, db_index=True)

    def __unicode__(self):
        return u'Engagement Letter for %s' % self.signatory_name

    @property
    def tool_slug(self):
        return 'engagement-letters'

    @property
    def markers(self):
        return EngagementLetterMarkers(tool=self)

    @property
    def base_signal(self):
        return base_signal

    @property
    def is_complete(self):
        return self.status == self.STATUS.complete

    @property
    def file_number(self):
        return self.data.get('file_number', None)

    @property
    def signatory_name(self):
        return self.data.get('signatory_full_name', None)

    @property
    def signatory_title(self):
        return self.data.get('signatory_title', None)

    @property
    def date_of_letter(self):
        date = self.data.get('date_of_letter', None)
        return datetime.strptime(date, '%Y-%m-%d')

    @property
    def filename(self):
        return slugify('engageletter-{company}-{user}'.format(company=self.workspace, user=self.user.get_full_name() or self.user.username))

    @property
    def company_name(self):
        return self.data.get('company_name', self.workspace.name)

    def html(self, **kwargs):
        """
        Override the HTMLMixin html method
        """
        # get bas context_data
        context_data = self.get_context_data(**kwargs)
        # setup the context object for it
        context = loader.Context(context_data)
        # render the template_source_body with current set of context
        body = loader.render_to_string(self.template_source_body, context)
        # add the rendered body to the underlying wrapper template
        context_data = self.get_context_data(body=body)
        # rerender it
        context = loader.Context(context_data)
        return self.template.render(context)

    def get_absolute_url(self):
        return reverse('workspace:tool_object_overview', kwargs={'workspace': self.workspace.slug, 'tool': self.workspace.tools.filter(slug=self.tool_slug).first().slug, 'slug': self.slug})

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
