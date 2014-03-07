# -*- coding: UTF-8 -*-
"""
Reminder emails
"""
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework import status as http_status

from toolkit.core.item.mailers import SignatoryReminderEmail
from toolkit.apps.review.mailers import ReviewerReminderEmail

from ..serializers import UserSerializer

from .revision import ItemCurrentRevisionView

import logging
logger = logging.getLogger('django.request')


class BaseReminderMixin(ItemCurrentRevisionView):
    """
    Mixin to ensure that inherited mthods are not implemented at this level
    necessary as we require the ItemCurrentRevisionView.get_object to provide us
    with the matter object
    """
    serializer_class = UserSerializer  # return a set of users that were reminded
    mailer = None

    def post(self, request, **kwargs):
        self.get_object()

        sent_to = {
            'detail': 'Sent %s to these users' % self.mailer.name,
            'results': []
        }

        for u in self.get_revision_object_set_queryset().all():
            try:
                m = self.mailer(recipients=((u.get_full_name(), u.email,)))
                m.process(subject=self.subject,
                          item=self.item,
                          from_name=self.request.user.get_full_name(),
                          action_url='http://lawpal.com/etc/')

                sent_to['results'].append(UserSerializer(u).data)

            except Exception as e:
                logger.critical('Could not send "%s" reminder email: %s' % (self.mailer, e))
        return Response(sent_to, status=http_status.HTTP_202_ACCEPTED)

    def update(self, **kwargs):
        raise exceptions.MethodNotAllowed(method=self.request.method)

    def delete(self, **kwargs):
        raise exceptions.MethodNotAllowed(method=self.request.method)

    def retrieve(self, **kwargs):
        raise exceptions.MethodNotAllowed(method=self.request.method)


class RemindReviewers(BaseReminderMixin):
    """
    Send reminder emails to reviewers
    """
    mailer = ReviewerReminderEmail
    subject = '[ACTION REQUIRED] Reminder to review'

    def get_revision_object_set_queryset(self):
        return self.revision.reviewers


class RemindSignatories(BaseReminderMixin):
    """
    Send reminder emails to signatories
    """
    mailer = SignatoryReminderEmail
    subject = '[ACTION REQUIRED] Reminder to sign'

    def get_revision_object_set_queryset(self):
        return self.revision.signatories
