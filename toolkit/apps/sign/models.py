# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.files.storage import default_storage

from rulez import registry as rulez_registry

# NB! hellosign is not the same lib as hello_sign
from hellosign import HelloSignUnclaimedDraftDocumentSignature
# django wrapper hello_sign imports
from hello_sign.models import HelloSignRequest
from hello_sign.mixins import ModelContentTypeMixin, HelloSignModelMixin
from hello_sign.services import HelloSignService

from toolkit.core.mixins import IsDeletedMixin

from toolkit.apps.default.templatetags.toolkit_tags import ABSOLUTE_BASE_URL
from toolkit.apps.review.mixins import UserAuthMixin

from .managers import SignDocumentManager
from .mailers import SignerReminderEmail

from storages.backends.s3boto import S3BotoStorage

from uuidfield import UUIDField
from jsonfield import JSONField

import urlparse
import logging
import datetime
logger = logging.getLogger('django.request')


class SignDocument(IsDeletedMixin,
                   UserAuthMixin,
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

    def __unicode__(self):
        return u'%s' % str(self.slug)

    def get_absolute_url(self, user):
        auth_key = self.get_user_auth(user=user)
        if auth_key is not None:
            return reverse('sign:sign_document', kwargs={'slug': self.slug, 'auth_slug': auth_key})
        return None

    def complete(self, is_complete=True):
        self.is_complete = is_complete
        self.save(update_fields=['is_complete'])
    complete.alters_data = True

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
    def file_exists_locally(self):
        """
        Used to determine if we should download the file locally
        """
        try:
            return default_storage.exists(self.document.executed_file)
        except Exception as e:
            logger.critical('Crocodoc file does not exist locally: %s raised exception %s' % (self.document.executed_file, e))
        return False

    @property
    def matter(self):
        return self.document.item.matter

    @property
    def participants(self):
        return set(self.signers.all() | self.matter.participants.all())

    @property
    def signer(self):
        """
        return the reviewer: the person in self.signers that is not in self.participants
        """
        try:
            # combine signers and participants
            # this is necessary as a participant may be a reviewer by request
            signers = set(self.signers.all())
            participants = set(self.matter.participants.all())
            combined = signers.union(participants)
            # get the common reviewer
            return signers.intersection(combined).pop()
        except:
            logger.error('no reviewer found for ReviewDocument: %s' % self)
            return None

    def get_hs_service(self):
        """
        OVERRIDDEN to return the HelloSignUnclaimedDraftDocumentSignature as default
        """
        return HelloSignService(HelloSignSignatureClass=HelloSignUnclaimedDraftDocumentSignature,  # Passed in to override the default
                                document=self.hs_document(),
                                title=self.hs_document_title(),
                                invitees=self.hs_signers(),
                                subject=self.hs_subject(),
                                message=self.hs_message())

    def send_for_signing(self, **kwargs):
        kwargs.update({
            'requester_email_address': kwargs.get('requester_email_address', self.matter.lawyer.email),  # required for this type
        })

        return super(SignDocument, self).send_for_signing(**kwargs)

    def hs_post_process_result(self, resp):
        result = resp.json()
        #
        # Clean ugly HS namespace
        #
        result = result.get('unclaimed_draft', result)

        if 'claim_url' in result:
            # append client_id to the claim_url attrib
            result['claim_url_with_client_id'] = '%s&client_id=%s' % (result['claim_url'], settings.HELLOSIGN_CLIENT_ID)

        return result

    def hs_record_result(self, result):
        """
        Because HS's api is so crap they dont give us an identifying GUID as part
        of the standard json, instead we have to manually parse the gui out of their crappy
        claim_url response, wasting precious cycles
        """
        claim_url = result.get('claim_url') # get claim url so we can **manually** (wtf hellosign) extract the gui
        parsed_url = urlparse.urlparse(claim_url)
        parsed_url_query = urlparse.parse_qs(parsed_url.query)
        unclaimed_draft_guid = parsed_url_query.get('guid')

        if unclaimed_draft_guid:
            if type(unclaimed_draft_guid) in [list]:
                unclaimed_draft_guid = unclaimed_draft_guid[0]  # its a list so get the first one as the guid

            hs_request_object, is_new = HelloSignRequest.objects.get_or_create(unclaimed_draft_guid=unclaimed_draft_guid,
                                                                               content_object_type=self.get_content_type_object(),
                                                                               object_id=self.pk)
            # save the result
            hs_request_object.data = result
            # save the field
            hs_request_object.save(update_fields=['data'])

            return hs_request_object
        return None


    def hs_subject(self):
        return 'Signature Request for: %s' % self.document.name

    def hs_document_title(self):
        """
        Method to set the document title, displayed in the HelloSign Interface
        """
        return self.document.name

    def hs_document(self):
        """
        Return the document to be sent for signing
        Ties in with HelloSignModelMixin method
        """
        return default_storage.open(self.document.executed_file)

    def hs_signers(self):
        """
        Return a list of invitees to sign
        """
        return [{'name': u.get_full_name(), 'email': u.email} for u in self.signers.all()]

    def download_if_not_exists(self):
        """
        Its necessary to download the file from s3 locally as we have restrictive s3
        permissions (adds time but necessary for security)
        """
        file_name = self.document.executed_file.name

        b = S3BotoStorage()

        if b.exists(file_name) is False:
            raise Exception('File does not exist on s3: %s' % file_name)

        else:
            #
            # download from s3 and save the file locally
            #
            file_object = b._open(file_name)
            return default_storage.save(file_name, file_object)

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