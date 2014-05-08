# -*- coding: utf-8 -*-
from django.db import models
from django.core.urlresolvers import reverse

from rulez import registry as rulez_registry


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

    def __unicode__(self):
        return u'%s' % str(self.slug)

    def get_absolute_url(self):
        return ABSOLUTE_BASE_URL(reverse('sign:sign_document', kwargs={'slug': self.slug}))

    def get_claim_url(self):
        return ABSOLUTE_BASE_URL(reverse('sign:claim_sign_document', kwargs={'slug': self.slug}))

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