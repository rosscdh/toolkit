# -*- coding: utf-8 -*-
from django.db import models
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify

from storages.backends.s3boto import S3BotoStorage

import os
from uuidfield import UUIDField
from jsonfield import JSONField

from rulez import registry as rulez_registry

from toolkit.apps.workspace.mixins import WorkspaceToolModelMixin

from .markers import EightyThreeBSignalMarkers
EIGHTYTHREEB_STATUS = EightyThreeBSignalMarkers().named_tuple(name='EIGHTYTHREEB_STATUS')

from .mixins import (IsDeletedMixin,
                     StatusMixin,
                     IRSMixin,
                     HTMLMixin,
                     TransferAndFilingDatesMixin,
                     USPSReponseMixin)
from .managers import EightyThreeBManager, AttachmentManger


def _83b_upload_file(instance, filename):
    filename = os.path.split(filename)[-1]
    filename_no_ext, ext = os.path.splitext(filename)
    return '83b/%d-%s%s' % (instance.eightythreeb.user.pk, slugify(filename_no_ext), ext)


class EightyThreeB(StatusMixin, IRSMixin, HTMLMixin, USPSReponseMixin, TransferAndFilingDatesMixin, WorkspaceToolModelMixin, models.Model):
    """
    83b Form to be associated with a Workspace and a particular user
    """
    STATUS_83b = EIGHTYTHREEB_STATUS
    INCOMPLETE_EXCLUDED_STATUS = [STATUS_83b.complete, STATUS_83b.irs_recieved]  # used in the manager to filter incomplete items

    pdf_template_name = 'eightythreeb/eightythreeb.html'  # @TODO what is this doing here?

    slug = UUIDField(auto=True, db_index=True)
    workspace = models.ForeignKey('workspace.Workspace')
    user = models.ForeignKey('auth.User')

    data = JSONField(default={})

    filing_date = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True)  # remove the null=True after migrations 0002,0003 applied
    transfer_date = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True)  # remove the null=True after migrations 0002,0003 applied

    status = models.IntegerField(choices=EIGHTYTHREEB_STATUS.get_choices(), default=EIGHTYTHREEB_STATUS.lawyer_complete_form, db_index=True)

    _markers = None

    objects = EightyThreeBManager()

    def __unicode__(self):
        return u'83(b) for %s' % self.client_name

    @property
    def tool_slug(self):
        return '83b-election-letters'

    @property
    def markers(self):
        if self._markers is None:
            self._markers = EightyThreeBSignalMarkers(tool=self)
        return self._markers

    @property
    def base_signal(self):
        from .signals import base_signal
        return base_signal

    @property
    def is_complete(self):
        return self.status == self.STATUS_83b.complete

    @property
    def client_name(self):
        return self.data.get('client_full_name', None)

    @property
    def filename(self):
        return slugify('83b-{company}-{user}'.format(company=self.workspace, user=self.user.get_full_name() or self.user.username))

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

rulez_registry.register("can_read", EightyThreeB)
rulez_registry.register("can_edit", EightyThreeB)
rulez_registry.register("can_delete", EightyThreeB)


class Attachment(IsDeletedMixin, models.Model):
    eightythreeb = models.ForeignKey('eightythreeb.EightyThreeB')
    attachment = models.FileField(upload_to=_83b_upload_file, blank=True, storage=S3BotoStorage())
    is_deleted = models.BooleanField(default=False)

    objects = AttachmentManger()

    def can_delete(self, user):
        return user == self.eightythreeb.user

rulez_registry.register("can_delete", Attachment)

from .signals import *
