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
    def invited_document_reviews(self):
        """
        exclude the primary reviewdocument which is only for matter.participants
        """
        if self.latest_revision:
            return self.latest_revision.reviewdocument_set.exclude(reviewers=None)
        else:
            return []

    @property
    def participants_review_document(self):
        """
        Get the main review_document used by the matter.participants
        """
        return self.latest_revision.reviewdocument_set.filter(reviewers=None).last()

    def percent_formatted(self, value):
        """
        Get the main review_document used by the matter.participants as a str(%)
        """
        return "{0:.0f}%".format(value) if value is not None else None

    @property
    def review_percentage_complete(self):
        return self.data.get('review_percentage_complete', None)

    @review_percentage_complete.setter
    def review_percentage_complete(self, value):
        if type(value) not in [type(None), int, float]:
            raise Exception('review_percentage_complete must be None or a float was passed a: %s' % type(value))

        logger.info('Item %s review_percentage_complete set to %s' % (self, value))
        self.data['review_percentage_complete'] = value

    def recalculate_review_percentage_complete(self):
        """
        Sets the review_percentage_complete status to False
        called when
        1. a new revision document is uploaded
        2. all reviews are complete (approved)
        3. all reviews are deleted
        """
        num_reviewdocuments = None # this is necessary to ensure that we can present None when there are no reviews active
        num_reviewdocuments_complete = 0
        review_percentage_complete = None

        queryset = self.invited_document_reviews()
        if queryset:
            # we have a queryset

            for rd in queryset.values('is_complete'):
                # this is necessary to ensure that we can present None when there are no reviews active
                num_reviewdocuments = 0 if num_reviewdocuments is None else num_reviewdocuments
                num_reviewdocuments += 1
                num_reviewdocuments_complete += 1 if rd.get('is_complete') is True else 0

            if num_reviewdocuments > 0:
                review_percentage_complete = float(num_reviewdocuments_complete) / float(num_reviewdocuments)
                review_percentage_complete = round(review_percentage_complete * 100, 0)

        if review_percentage_complete != self.review_percentage_complete: # only if its different (save the db update event)

            # Has changed AND is 100.00
            if review_percentage_complete == 100.0:
                # send matter.action signal
                self.matter.actions.all_revision_reviews_complete(item=self, revision=self.latest_revision)

            self.review_percentage_complete = review_percentage_complete
            logger.info('Item %s review_percentage_complete set to %s' % (self, review_percentage_complete))
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
        # otherwise send to the reviewers who have not complted the review
        recipients_set = recipients if recipients else self.invited_document_reviews().filter(is_complete=False)

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
