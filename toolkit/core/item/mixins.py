# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse

from toolkit.apps.workspace.models import InviteKey
from toolkit.apps.review.mailers import ReviewerReminderEmail
from toolkit.apps.default.templatetags.toolkit_tags import ABSOLUTE_BASE_URL

from .mailers import RequestedDocumentReminderEmail
from toolkit.apps.sign.mailers import SignerReminderEmail

import logging
logger = logging.getLogger('django.request')


class RequestDocumentUploadMixin(object):
    """
    Mixin to allow Item to act in requesting an upload from a user
    """
    @property
    def request_document_message(self):
        return self.data.get('request_document', {}).get('message', None)

    @request_document_message.setter
    def request_document_message(self, value):
        request_document = self.data.get('request_document', {})
        request_document.update({'message': value})
        self.data['request_document'] = request_document

    @property
    def requested_by(self):
        return self.data.get('request_document', {}).get('requested_by', None)

    @requested_by.setter
    def requested_by(self, value):
        request_document = self.data.get('request_document', {})
        request_document.update({'requested_by': value})

        self.data['request_document'] = request_document


class ReviewInProgressMixin(object):
    """
    """
    @property
    def review_in_progress(self):
        return self.data.get('review_in_progress', False)

    @review_in_progress.setter
    def review_in_progress(self, value):
        value = True if value in [True, 't', 1, '1', 'true'] else False
        logger.info('Item %s review_in_progress set to %s' % (self, value))

        self.data['review_in_progress'] = value

    def set_review_is_in_progress(self):
        """
        Sets the review_in_progress status to True
        called when
        1. a new review is created
        """
        if self.review_in_progress is False:  # only if its not already True
            self.review_in_progress = True
            logger.info('Item %s review_in_progress is True' % self)
            self.save(update_fields=['data'])

    def reset_review_in_progress(self):
        """
        Sets the review_in_progress status to False
        called when
        1. a new revision document is uploaded
        2. all reviews are complete (approved)
        3. all reviews are deleted
        """
        if self.review_in_progress is True: # only if its not already False
            self.review_in_progress = False
            logger.info('Item %s review_in_progress reset (set to False)' % self)
            self.save(update_fields=['data'])


class RequestedDocumentReminderEmailsMixin(object):
    def send_document_requested_emails(self, from_user, subject=None, **kwargs):
        #
        # @BUSINESSRULE this email only gets sent when is_requested is True
        #
        if self.is_requested is True:
            #
            # the responsible_party is the one to upload the document
            #
            user = self.responsible_party

            if user:

                #
                # if we have one
                # @BUSINESSRULE ALWAYS redirect the invitee to the requests page
                # and not the specific object
                #
                next_url = reverse('request:list')

                #
                # Create the invite key (it may already exist)
                #
                invite, is_new = InviteKey.objects.get_or_create(matter=self.matter,
                                                                 invited_user=user,
                                                                 next=next_url)
                invite.inviting_user = from_user
                invite.save(update_fields=['inviting_user'])

                # send the invite url
                action_url = ABSOLUTE_BASE_URL(invite.get_absolute_url())

                if subject is not None:
                    #
                    # Add the subject if its provided
                    #
                    kwargs.update({'subject': subject})

                mailer = RequestedDocumentReminderEmail(recipients=((user.get_full_name(), user.email,),), from_tuple=(from_user.get_full_name(), from_user.email,))
                mailer.process(item=self,
                               from_name=from_user.get_full_name(),
                               action_url=action_url,  # please understsand the diff between action_url and next_url
                               **kwargs)


class RevisionReviewReminderEmailsMixin(object):
    def send_invite_to_review_emails(self, from_user, to, **kwargs):
        """
        Send the initial email to invite
        but use the standard subject; which is an [ACTION REQUIRED]
        """
        assert type(to) is list, 'to must be a list [User]'
        #
        # Becase we are yield users need to call next on this to make it action
        #
        return [email for email in self.send_review_emails(from_user=from_user, subject=ReviewerReminderEmail.subject, recipients=to, **kwargs)]

    def send_review_reminder_emails(self, from_user, **kwargs):
        """
        Send the initial email to invite
        but use the standard subject; which is a [REMINDER]
        """
        #
        # Becase we are yield users need to call next on this to make it action
        #
        return [email for email in self.send_review_emails(from_user=from_user, subject='[REMINDER] Please review this document', **kwargs)]

    def send_review_emails(self, from_user, subject, recipients=[], **kwargs):
        #
        # @TODO filter by those reviewers that have not yet reviewed the doc
        #

        # send to the provided recipients if there are any
        # otherwise send to the reviewers
        recipients_set = recipients if recipients else self.latest_revision.reviewers.all()

        for u in recipients_set:

            mailer = ReviewerReminderEmail(recipients=((u.get_full_name(), u.email,),), from_tuple=(from_user.get_full_name(), from_user.email,))

            #
            # Get the review document for this user
            #
            review_document = self.latest_revision.reviewdocument_set.filter(reviewers__in=[u]).first()

            if review_document:
                #
                # if we have one
                # @BUSINESSRULE ALWAYS redirect the invitee to the requests page
                # and not the specific object
                #
                next_url = reverse('request:list')
                #
                # Create the invite key (it may already exist)
                #
                invite, is_new = InviteKey.objects.get_or_create(matter=self.matter,
                                                                 invited_user=u,
                                                                 next=next_url)
                invite.inviting_user = from_user
                invite.save(update_fields=['inviting_user'])

                # send the invite url
                action_url = ABSOLUTE_BASE_URL(invite.get_absolute_url())

                mailer.process(subject=subject,
                               item=self,
                               from_name=from_user.get_full_name(),
                               action_url=action_url, # please understsand the diff between action_url and next_url
                               **kwargs)

                yield u

            else:

                yield None


class RevisionSignReminderEmailsMixin(object):
    def send_invite_to_sign_emails(self, from_user, to, **kwargs):
        """
        Send the initial email to invite
        but use the standard subject; which is an [ACTION REQUIRED]
        """
        assert type(to) is list, 'to must be a list [User]'
        #
        # Becase we are yield users need to call next on this to make it action
        #
        return [email for email in self.send_sign_emails(from_user=from_user, subject=SignerReminderEmail.subject, recipients=to, **kwargs)]

    def send_sign_reminder_emails(self, from_user, **kwargs):
        """
        Send the initial email to invite
        but use the standard subject; which is a [REMINDER]
        """
        #
        # Becase we are yield users need to call next on this to make it action
        #
        return [email for email in self.send_sign_emails(from_user=from_user, subject='[REMINDER] Please sign this document', **kwargs)]

    def send_sign_emails(self, from_user, subject, recipients=[], **kwargs):
        #
        # @TODO filter by those reviewers that have not yet reviewed the doc
        #

        # send to the provided recipients if there are any
        # otherwise send to the reviewers
        recipients_set = recipients if recipients else self.latest_revision.signers.all()

        for u in recipients_set:

            mailer = SignerReminderEmail(recipients=((u.get_full_name(), u.email,),), from_tuple=(from_user.get_full_name(), from_user.email,))

            #
            # Get the review document for this user
            #
            sign_document = self.latest_revision.signdocument_set.filter(signers__in=[u]).first()

            if sign_document:
                #
                # if we have one
                # @BUSINESSRULE ALWAYS redirect the invitee to the requests page
                # and not the specific object
                #
                next_url = reverse('request:list')
                #
                # Create the invite key (it may already exist)
                #
                invite, is_new = InviteKey.objects.get_or_create(matter=self.matter,
                                                                 invited_user=u,
                                                                 next=next_url)
                invite.inviting_user = from_user
                invite.save(update_fields=['inviting_user'])

                # send the invite url
                action_url = ABSOLUTE_BASE_URL(invite.get_absolute_url())

                mailer.process(subject=subject,
                               item=self,
                               from_name=from_user.get_full_name(),
                               action_url=action_url, # please understsand the diff between action_url and next_url
                               **kwargs)

                yield u

            else:

                yield None
