# -*- coding: utf-8 -*-
from django.db import models
from django.core.urlresolvers import reverse
from django.core.files.storage import default_storage

from rulez import registry as rulez_registry


# django wrapper hello_sign imports
from hello_sign.mixins import ModelContentTypeMixin, HelloSignModelMixin

from toolkit.core.mixins import IsDeletedMixin

from toolkit.apps.default.templatetags.toolkit_tags import ABSOLUTE_BASE_URL
from toolkit.apps.review.mixins import UserAuthMixin

from .managers import SignDocumentManager
from .mailers import SignerReminderEmail
from .mixins import HelloSignOverridesMixin

from storages.backends.s3boto import S3BotoStorage

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

    # @property
    # def signer(self):
    #     """
    #     return the reviewer: the person in self.signers that is not in self.participants
    #     """
    #     try:
    #         # combine signers and participants
    #         # this is necessary as a participant may be a reviewer by request
    #         signers = set(self.signers.all())
    #         participants = set(self.matter.participants.all())
    #         combined = signers.union(participants)
    #         # get the common reviewer
    #         return signers.intersection(combined).pop()
    #     except:
    #         logger.error('no reviewer found for ReviewDocument: %s' % self)
    #         return None

    @property
    def signing_request(self):
        return self.hellosign_requests().first()

    def __unicode__(self):
        return u'%s' % str(self.slug)

    def get_absolute_url(self, user):
        # auth_key = self.get_user_auth(user=user)
        # if auth_key is not None:
        #     return reverse('sign:sign_document', kwargs={'slug': self.slug, 'auth_slug': auth_key})
        # return None
        return ABSOLUTE_BASE_URL(reverse('sign:sign_document', kwargs={'slug': self.slug}))

    def complete(self, is_complete=True):
        self.is_complete = is_complete
        self.save(update_fields=['is_complete'])
    complete.alters_data = True

    def send_for_signing(self, **kwargs):
        kwargs.update({
            'requester_email_address': kwargs.get('requester_email_address', self.matter.lawyer.email),  # required for this type
        })

        return super(SignDocument, self).send_for_signing(**kwargs)

    # def download_if_not_exists(self):
    #     """
    #     Its necessary to download the file from s3 locally as we have restrictive s3
    #     permissions (adds time but necessary for security)
    #     """
    #     file_name = self.document.executed_file.name

    #     b = S3BotoStorage()

    #     if b.exists(file_name) is False:
    #         raise Exception('File does not exist on s3: %s' % file_name)

    #     else:
    #         #
    #         # download from s3 and save the file locally
    #         #
    #         file_object = b._open(file_name)
    #         return default_storage.save(file_name, file_object)

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