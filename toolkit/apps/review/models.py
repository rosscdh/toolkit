# -*- coding: utf-8 -*-
from django.db import models
from django.core.urlresolvers import reverse
from django.core.files.storage import default_storage

from rulez import registry as rulez_registry

from toolkit.apps.default.templatetags.toolkit_tags import ABSOLUTE_BASE_URL

from toolkit.core.mixins import IsDeletedMixin

from .mixins import UserAuthMixin
from .managers import ReviewDocumentManager
from .mailers import ReviewerReminderEmail

from storages.backends.s3boto import S3BotoStorage

from uuidfield import UUIDField
from jsonfield import JSONField

import logging
logger = logging.getLogger('django.request')


class ReviewDocument(IsDeletedMixin, UserAuthMixin, models.Model):
    """
    An object to represent a url that allows multiple reviewers to view
    a document using a service like crocodoc
    """
    slug = UUIDField(auto=True, db_index=True)
    document = models.ForeignKey('attachment.Revision')
    reviewers = models.ManyToManyField('auth.User')
    is_complete = models.BooleanField(default=False)
    date_last_viewed = models.DateTimeField(blank=True, null=True)
    data = JSONField(default={})

    objects = ReviewDocumentManager()

    class Meta:
        # @BUSINESS RULE always return the newest to oldest
        ordering = ('-id',)

    def get_absolute_url(self, user):
        auth_key = self.get_user_auth(user=user)
        if auth_key is not None:
            return reverse('review:review_document', kwargs={'slug': self.slug, 'auth_slug': self.get_user_auth(user=user)})
        return None

    def get_approval_url(self, user):
        auth_key = self.get_user_auth(user=user)
        if auth_key is not None:
            return reverse('review:approve_document', kwargs={'slug': self.slug, 'auth_slug': self.get_user_auth(user=user)})
        return None

    def complete(self):
        self.is_complete = True
        self.save(update_fields=['is_complete'])
    complete.alters_data = True

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
        return set(self.reviewers.all() | self.matter.participants.all())

    @property
    def reviewer(self):
        """
        return the reviewer: the person in self.reviewers that is not in self.participants
        """
        try:
            return set(self.reviewers.all()).difference(self.matter.participants.all()).pop()
        except:
            logger.error('no reviewer found for ReviewDocument: %s' % self)
            return None

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

    def can_read(self, user):
        return user in self.reviewers.all()

    def can_edit(self, user):
        return user in self.reviewers.all()

    def can_delete(self, user):
        return user in self.participants.all()

rulez_registry.register("can_read", ReviewDocument)
rulez_registry.register("can_edit", ReviewDocument)
rulez_registry.register("can_delete", ReviewDocument)

from .signals import (ensure_matter_participants_are_in_reviewdocument_participants,
                      on_reviewer_add,
                      on_reviewer_remove,)
