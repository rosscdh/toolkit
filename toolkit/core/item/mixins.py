# -*- coding: utf-8 -*-
from toolkit.apps.workspace.models import InviteKey
from toolkit.apps.review.mailers import ReviewerReminderEmail
from toolkit.apps.default.templatetags.toolkit_tags import ABSOLUTE_BASE_URL


class RequestDocumentUploadMixin(object):
    """
    Mixin to allow Item to act in requesting an upload from a user
    """
    @property
    def note(self):
        return self.data.get('request_document', {}).get('note', None)

    @note.setter
    def note(self, value):
        request_document = self.data.get('request_document', {})
        request_document.update({'note': value})

        self.data['request_document'] = request_document

    @property
    def requested_by(self):
        return self.data.get('request_document', {}).get('requested_by', None)

    @requested_by.setter
    def requested_by(self, value):
        request_document = self.data.get('request_document', {})
        request_document.update({'requested_by': value})

        self.data['request_document'] = request_document


class LatestRevisionReminderEmailsMixin(object):
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

    def send_reminder_emails(self, from_user, **kwargs):
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

            mailer = ReviewerReminderEmail(recipients=((u.get_full_name(), u.email,),))

            #
            # Get the review document for this user
            #
            review_document = self.latest_revision.reviewdocument_set.filter(reviewers__in=[u]).first()

            if review_document:
                #
                # if we have one
                #
                next_url = review_document.get_absolute_url(user=u)
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
