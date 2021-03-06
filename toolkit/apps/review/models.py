# -*- coding: utf-8 -*-
from django.db import models
from django.core.urlresolvers import reverse

from rulez import registry as rulez_registry

from toolkit.apps.default.templatetags.toolkit_tags import ABSOLUTE_BASE_URL

from toolkit.core.mixins import IsDeletedMixin
from toolkit.core.mixins import ApiSerializerMixin
from toolkit.core.mixins import FileExistsLocallyMixin

from .mixins import UserAuthMixin
from .managers import ReviewDocumentManager
from .mailers import ReviewerReminderEmail

from uuidfield import UUIDField
from jsonfield import JSONField

import datetime

import logging
logger = logging.getLogger('django.request')


class ReviewDocument(IsDeletedMixin,
                     FileExistsLocallyMixin,
                     UserAuthMixin,
                     ApiSerializerMixin,
                     models.Model):
    """
    An object to represent a url that allows multiple reviewers to view
    a document using a service like crocodoc
    """
    slug = UUIDField(auto=True, db_index=True)

    crocodoc_uuid = UUIDField(hyphenate=True, null=True, blank=True)

    document = models.ForeignKey('attachment.Revision')
    reviewers = models.ManyToManyField('auth.User')

    is_complete = models.BooleanField(default=False)
    date_last_viewed = models.DateTimeField(blank=True, null=True)

    data = JSONField(default={})

    objects = ReviewDocumentManager()

    _serializer = 'toolkit.api.serializers.ReviewSerializer'

    class Meta:
        # @BUSINESS RULE always return the newest to oldest
        ordering = ('-id',)

    # override for FileExistsLocallyMixin:
    def get_document(self):
        return self.document.executed_file

    def reviewing_user_is_participant_review_url(self, user):
        """
        if a mater.participant is invited to review a document
        they should be directed to comment on the primary document and not
        the sandboxed copy document. This method returns the prmary document
        url if the user is a matter.participant
        """
        # is the invited reviewer and is a participant
        if user == self.reviewer and user in self.matter.participants.all():
            primary_review_document = self.document.item.primary_participant_review_document()
            return ABSOLUTE_BASE_URL(reverse('review:review_document', kwargs={'slug': primary_review_document.slug, 'auth_slug': primary_review_document.get_user_auth(user=user)}))
        return None

    def get_absolute_url(self, user):
        """
        should change depending on who is looking at it.
        in order to make matter.participants all reivew and comment on the same document
        we have to check if they are matter.participant
        """
        auth_key = self.get_user_auth(user=user)
        if auth_key is not None:
            # see if the user is a participant and review their primary review_documnet
            primary_document_review_url = self.reviewing_user_is_participant_review_url(user=user)
            if primary_document_review_url is not None:
                return primary_document_review_url
            else:
                # is a normal 3rd party invited user
                return ABSOLUTE_BASE_URL(reverse('review:review_document', kwargs={'slug': self.slug, 'auth_slug': self.get_user_auth(user=user)}))
        return None

    def get_download_url(self, user):
        """
        The download url must stay not be changed even if the user is a matter.participant
        as its used to see if their review of the document is done
        and since the documents are simply copies of the primary this is safe
        """
        return ABSOLUTE_BASE_URL(reverse('review:download_document', kwargs={'slug': self.slug, 'auth_slug': self.get_user_auth(user=user)}))

    def get_approval_url(self, user):
        """
        The approval url must stay not be changed even if the user is a matter.participant
        as its used to see if their review of the document is done
        and since the documents are simply copies of the primary this is safe
        """
        auth_key = self.get_user_auth(user=user)
        if auth_key is not None:
            return ABSOLUTE_BASE_URL(reverse('review:approve_document',
                                             kwargs={'slug': self.slug, 'auth_slug': self.get_user_auth(user=user)}))
        return None

    def get_regular_url(self):
        """
        Used in notficiations & activity
        """
        return '{url}/review/{slug}'.format(url=self.document.get_absolute_url(), slug=self.slug)

    def complete(self, is_complete=True):
        self.is_complete = is_complete
        self.save(update_fields=['is_complete'])

    complete.alters_data = True

    @property
    def reviewer_has_viewed(self):
        return self.date_last_viewed is not None

    @reviewer_has_viewed.setter
    def reviewer_has_viewed(self, value):
        if value == True:
            self.date_last_viewed = datetime.datetime.utcnow()
            # user has viewed -> 10
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
        return set(self.reviewers.all() | self.matter.participants.all())

    @property
    def reviewer(self):
        """
        return the reviewer: the person in self.reviewers that is not in self.participants
        """
        try:
            # combine reviewers and participants
            # this is necessary as a participant may be a reviewer by request
            reviewers = set(self.reviewers.all())
            participants = set(self.matter.participants.all())
            combined = reviewers.union(participants)
            # get the common reviewer
            return reviewers.intersection(combined).pop()
        except Exception as e:
            return None

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

                m = ReviewerReminderEmail(recipients=((u.get_full_name(), u.email,),), from_tuple=(from_user.get_full_name(), from_user.email,))
                m.process(subject=m.subject,
                          item=self.document.item,
                          document=self.document,
                          from_name=from_user.get_full_name(),
                          action_url=ABSOLUTE_BASE_URL(path=self.get_absolute_url(user=u)))

    def can_read(self, user):
        return user in self.participants

    def can_edit(self, user):
        return user in self.participants

    def can_delete(self, user):
        return user in self.participants

rulez_registry.register("can_read", ReviewDocument)
rulez_registry.register("can_edit", ReviewDocument)
rulez_registry.register("can_delete", ReviewDocument)

from .signals import (#set_item_review_percentage_complete,
                      #reset_item_review_percentage_complete_on_complete,
                      #reset_item_review_percentage_complete_on_delete,
                      ensure_matter_participants_are_in_reviewdocument_participants,
                      on_reviewer_add,
                      on_reviewer_remove,)
