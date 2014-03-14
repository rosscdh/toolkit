# -*- coding: utf-8 -*-
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
    def send_reminder_emails(self, from_user):
        #
        # @TODO filter by those reviewers that have not yet reviewed the doc
        #
        for u in self.latest_revision.reviewers.all():
            mailer = ReviewerReminderEmail(recipients=((u.get_full_name(), u.email,),))

            #
            # Get the review document for this user
            #
            review_document = self.latest_revision.reviewdocument_set.filter(reviewers__in=[u]).first()
            action_url = review_document.get_absolute_url(user=u)

            mailer.process(subject='[REMINDER] Please review this document',
                           item=self,
                           from_name=from_user.get_full_name(),
                           action_url=ABSOLUTE_BASE_URL(action_url))

            yield u