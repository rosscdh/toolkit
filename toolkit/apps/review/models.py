# -*- coding: utf-8 -*-
from django.db import models
from django.core.urlresolvers import reverse
from django.core.files.storage import default_storage
from django.contrib.contenttypes.models import ContentType

from toolkit.apps.default.templatetags.toolkit_tags import ABSOLUTE_BASE_URL

from .mixins import UserAuthMixin
from .mailers import ReviewerReminderEmail

from dj_crocodoc.models import CrocodocDocument
from storages.backends.s3boto import S3BotoStorage

from uuidfield import UUIDField
from jsonfield import JSONField

import logging
logger = logging.getLogger('django.request')


class ReviewDocument(UserAuthMixin, models.Model):
    """
    An object to represent a url that allows multiple reviewers to view
    a document using a service like crocodoc
    """
    slug = UUIDField(auto=True, db_index=True)
    document = models.ForeignKey('attachment.Revision')
    participants = models.ManyToManyField('auth.User', related_name='review_owners')
    reviewers = models.ManyToManyField('auth.User')
    data = JSONField(default={})

    class Meta:
        # @BUSINESS RULE always return the oldest to newest
        ordering = ('id',)

    def get_absolute_url(self, user):
        auth_key = self.get_user_auth(user=user)
        if auth_key is not None:
            return reverse('review:review_document', kwargs={'slug': self.slug, 'auth_slug': self.get_user_auth(user=user)})
        return None

    @property
    def crocodoc(self):

        if self.file_exists_locally is False:
            self.download_if_not_exists()

        crocodoc, is_new = CrocodocDocument.objects.get_or_create(object_id=self.document.pk,
                                                                  content_object_type=ContentType.objects.get_for_model(self.document),
                                                                  object_attachment_fieldname='executed_file')
        return crocodoc

    @property
    def file_exists_locally(self):
        """
        Used to determin if we should download the file locally
        """
        try:
            return default_storage.exists(self.document.executed_file)
        except Exception as e:
            logger.critical('Crocodoc file does not exist locally: %s raised exception %s' % (self.document.executed_file, e))
        return False

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
        @BUSINESSRULE requested users must be in the reviewers object
        """
        if type(users) not in [list]:
            raise Exception('users must be of type list: users=[<User>]')

        for u in self.reviewers.all():
            #
            # @BUSINESSRULE if no users passed in then send to all of the reviewers
            #
            if users == [] or u in users:
                #
                # send email
                #
                logger.info('Sending ReviewDocument invite email to: %s' % u)

                m = ReviewerReminderEmail(recipients=((u.get_full_name(), u.email,),))
                m.process(subject=m.subject,
                          item=self.document.item,
                          document=self.document,
                          from_name=from_user.get_full_name(),
                          action_url=ABSOLUTE_BASE_URL(path=self.get_absolute_url(user=u)))


from .signals import (on_participant_add,
                      on_participant_add,
                      on_reviewer_add,
                      on_reviewer_remove,)