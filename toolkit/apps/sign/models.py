# -*- coding: utf-8 -*-
from django.db import models
from django.core import signing
from django.conf import settings
from django.core.urlresolvers import reverse

from rulez import registry as rulez_registry

from hellosign_sdk import HSClient

# django wrapper hello_sign imports
from hello_sign.mixins import ModelContentTypeMixin, HelloSignModelMixin

from toolkit.core.mixins import IsDeletedMixin

from toolkit.apps.default.templatetags.toolkit_tags import ABSOLUTE_BASE_URL
from toolkit.apps.review.mixins import UserAuthMixin

from .managers import SignDocumentManager
from .mailers import SignerReminderEmail
from .mixins import HelloSignOverridesMixin

from uuidfield import UUIDField
from jsonfield import JSONField

import logging
import datetime
logger = logging.getLogger('django.request')


class SignDocument(IsDeletedMixin,
                   UserAuthMixin,
                   HelloSignOverridesMixin,
                   HelloSignModelMixin,
                   ModelContentTypeMixin,
                   models.Model):
    """
    An object to represent a url that allows multiple signers to view
    a document using a service like crocodoc
    """
    slug = UUIDField(auto=True, db_index=True)
    document = models.ForeignKey('attachment.Revision')
    requested_by = models.ForeignKey('auth.User', null=True, related_name='signatures_requested_by')
    signers = models.ManyToManyField('auth.User')
    is_complete = models.BooleanField(default=False)
    date_last_viewed = models.DateTimeField(blank=True, null=True)
    data = JSONField(default={})

    objects = SignDocumentManager()

    class Meta:
        # @BUSINESS RULE always return the newest to oldest
        ordering = ('-id',)

    @property
    def signer_has_viewed(self):
        return self.date_last_viewed is not None

    @signer_has_viewed.setter
    def signer_has_viewed(self, value):
        if value == True:
            self.date_last_viewed = datetime.datetime.utcnow()
        else:
            self.date_last_viewed = None
        self.save(update_fields=['date_last_viewed'])

    @property
    def is_current(self):
        """
        Test that this revision is still the latest revision
        if not then redirect elsewhere
        """
        return self.document.item.latest_revision == self.document

    @property
    def matter(self):
        return self.document.item.matter

    @property
    def participants(self):
        return set(self.signers.all() | self.matter.participants.all())

    @property
    def signing_request(self):
        return self.hellosign_requests().first()

    @property
    def signatures(self):
        return self.signing_request.data.get('signature_request', {}).get('signatures', []) if self.signing_request is not None else []

    def __unicode__(self):
        return u'%s' % str(self.slug)

    def get_absolute_url(self, signer):
        return ABSOLUTE_BASE_URL(reverse('sign:sign_document', kwargs={'slug': self.slug, 'username': signer.username}))

    def get_claim_url(self):
        return ABSOLUTE_BASE_URL(reverse('sign:claim_sign_document', kwargs={'slug': self.slug}))

    def get_signer_signing_url(self, signer):
        signature_id = None
        signatures = self.signatures
        signer_email = signer.email

        try:
            signature_id = [s for s in signatures if s.get('signer_email_address') == signer_email][0].get('signature_id', None)
        except IndexError:
            logger.error('Could not find signer: %s in %s' % (signer_email, signatures))
            
        if signature_id is not None:
            HS_CLIENT = HSClient(api_key=settings.HELLOSIGN_API_KEY)
            embedded_signing_object = HS_CLIENT.get_embedded_object(signature_id)

            return embedded_signing_object.sign_url
        return None

    def has_signed(self, signer):
        signer_email = signer.email
        return len([s for s in self.signatures if s.get('signer_email_address') == signer_email and s.get('signed_at') is not None]) == 1

    def signed_at(self, signer):
        signer_email = signer.email
        signed_at = None
        try:
            signed_at = [s for s in self.signatures if s.get('signer_email_address') == signer_email and s.get('signed_at') is not None][0].get('signed_at')
            signed_at = datetime.datetime.fromtimestamp(int(signed_at))
        except IndexError:
            pass
        return signed_at

    def percentage_complete(self):
        num_signatures = len(self.signatures)
        percentage_complete = None  # require None so that we can represent that there are no signatures

        if num_signatures > 0:
            percentage_complete = 0  # reset it here
            num_complete = len([signature for signature in self.signatures if signature.get('signed_at', None) is not None])

            if num_complete > 0:
                percentage_complete = float(num_complete) / float(num_signatures)
                percentage_complete = round(percentage_complete * 100, 0)

        return percentage_complete

    def complete(self, is_complete=True):
        self.is_complete = is_complete
        self.save(update_fields=['is_complete'])
    complete.alters_data = True

    def send_invite_email(self, from_user, users=[]):
        """
        @BUSINESSRULE requested users must be in the signers object
        """
        if type(users) not in [list]:
            raise Exception('users must be of type list: users=[<User>]')

        for u in self.signers.all():
            #
            # @BUSINESSRULE if no users passed in then send to all of the signers
            #
            if users == [] or u in users:
                #
                # send email
                #
                logger.info('Sending Sign Document invite email to: %s' % u)

                m = SignerReminderEmail(recipients=((u.get_full_name(), u.email,),))
                m.process(subject=m.subject,
                          item=self.document.item,
                          document=self.document,
                          from_name=from_user.get_full_name(),
                          action_url=ABSOLUTE_BASE_URL(path=self.get_absolute_url(user=u)))

    def can_read(self, user):
        return user in set(self.signers.all() | self.document.item.matter.participants.all())

    def can_edit(self, user):
        return user in self.document.item.matter.participants.all()

    def can_delete(self, user):
        return user in self.document.item.matter.participants.all()

rulez_registry.register("can_read", SignDocument)
rulez_registry.register("can_edit", SignDocument)
rulez_registry.register("can_delete", SignDocument)


from .signals import (ensure_matter_participants_are_in_signdocument_participants,
                      on_signer_add,
                      on_signer_remove,)