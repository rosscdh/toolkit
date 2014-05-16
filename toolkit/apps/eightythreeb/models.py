# -*- coding: utf-8 -*-
from django.db import models
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify

from toolkit.core import _managed_S3BotoStorage

from rulez import registry as rulez_registry

from toolkit.core.mixins import IsDeletedMixin

from toolkit.apps.workspace.signals import base_signal
from toolkit.apps.workspace.mixins import WorkspaceToolModelMixin

from .markers import EightyThreeBSignalMarkers
EIGHTYTHREEB_STATUS = EightyThreeBSignalMarkers().named_tuple(name='EIGHTYTHREEB_STATUS')

from .mixins import (StatusMixin,
                     IRSMixin,
                     HTMLMixin,
                     TransferAndFilingDatesMixin,
                     USPSReponseMixin)
from .managers import EightyThreeBManager

import os
import datetime
from uuidfield import UUIDField
from jsonfield import JSONField
from decimal import Decimal


def _upload_file(instance, filename):
    filename = os.path.split(filename)[-1]
    filename_no_ext, ext = os.path.splitext(filename)
    return '83b/%d-%s%s' % (instance.eightythreeb.user.pk, slugify(filename_no_ext), ext)


class EightyThreeB(StatusMixin, IRSMixin, HTMLMixin, USPSReponseMixin, TransferAndFilingDatesMixin, WorkspaceToolModelMixin, IsDeletedMixin, models.Model):
    """
    83b Form to be associated with a Workspace and a particular user
    """
    STATUS = EIGHTYTHREEB_STATUS
    INCOMPLETE_EXCLUDED_STATUS = [EIGHTYTHREEB_STATUS.complete, EIGHTYTHREEB_STATUS.irs_recieved]  # used in the manager to filter incomplete items

    pdf_template_name = 'eightythreeb/eightythreeb.html'  # @TODO what is this doing here?

    slug = UUIDField(auto=True, db_index=True)
    workspace = models.ForeignKey('workspace.Workspace')
    user = models.ForeignKey('auth.User')

    data = JSONField(default={})

    filing_date = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True)  # remove the null=True after migrations 0002,0003 applied
    transfer_date = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True)  # remove the null=True after migrations 0002,0003 applied

    status = models.IntegerField(choices=EIGHTYTHREEB_STATUS.get_choices(), default=EIGHTYTHREEB_STATUS.lawyer_complete_form, db_index=True)

    objects = EightyThreeBManager()

    def __unicode__(self):
        return u'83(b) for %s' % self.client_name

    @property
    def tool_slug(self):
        return '83b-election-letters'

    @property
    def markers(self):
        return EightyThreeBSignalMarkers(tool=self)

    @property
    def base_signal(self):
        return base_signal

    @property
    def is_complete(self):
        return self.status == self.STATUS.complete

    @property
    def has_expired(self):
        return not self.is_complete and self.filing_date < datetime.date.today()

    @property
    def client_name(self):
        return self.data.get('client_full_name', None)

    @property
    def filename(self):
        return slugify('83b-{company}-{user}'.format(company=self.workspace, user=self.user.get_full_name() or self.user.username))

    @property
    def company_name(self):
        return self.data.get('company_name', self.workspace.name)

    def get_context_data(self, **kwargs):
        """
        Append custom values to the HTMLMixin.get_context_data for the template
        """
        kwargs.update({
            'aggregate_share_value': Decimal(self.data.get('total_shares_purchased', 0)) * Decimal(self.data.get('transfer_value_share', 0)),
            'total_amount_paid': Decimal(self.data.get('total_shares_purchased', 0)) * Decimal(self.data.get('price_paid_per_share', 0)),
        })

        kwargs = super(EightyThreeB, self).get_context_data(**kwargs)

        return kwargs

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

rulez_registry.register("can_read", EightyThreeB)
rulez_registry.register("can_edit", EightyThreeB)
rulez_registry.register("can_delete", EightyThreeB)


class Attachment(IsDeletedMixin, models.Model):
    eightythreeb = models.ForeignKey('eightythreeb.EightyThreeB')
    attachment = models.FileField(upload_to=_upload_file, blank=True, storage=_managed_S3BotoStorage())

    def can_delete(self, user):
        return user == self.eightythreeb.user

rulez_registry.register("can_delete", Attachment)

from .signals import *  # noqa
