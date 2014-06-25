# -*- coding: UTF-8 -*-
"""
Reminder emails
"""
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework import status as http_status

from rulez import registry as rulez_registry

from ..serializers import SimpleUserSerializer
from .mixins import SpecificAttributeMixin
from .revision import ItemCurrentRevisionView

import logging
logger = logging.getLogger('django.request')


class BaseReminderMixin(SpecificAttributeMixin, ItemCurrentRevisionView):
    """
    Mixin to ensure that inherited mthods are not implemented at this level
    necessary as we require the ItemCurrentRevisionView.get_object to provide us
    with the matter object
    """
    serializer_class = SimpleUserSerializer  # return a set of users that were reminded
    specific_attribute = 'reviewers.all()'
    allowed_methods = ('create',)

    def create(self, request, **kwargs):

        sent_to = {
            'detail': 'Sent reminder email to the following users',
            'results': []
        }

        serializer = self.get_serializer_class()

        for user in self.send_reminders():
            #
            # We expect a set of User objects here
            #
            sent_to['results'].append(serializer(user, context={'request': self.request}).data)

        return Response(sent_to, status=http_status.HTTP_202_ACCEPTED)

    def send_reminders(self):
        raise NotImplementedError

    def update(self, request, **kwargs):
        raise exceptions.MethodNotAllowed(method=self.request.method)

    def delete(self, request, **kwargs):
        raise exceptions.MethodNotAllowed(method=self.request.method)

    def retrieve(self, request, **kwargs):
        raise exceptions.MethodNotAllowed(method=self.request.method)


class RemindReviewers(BaseReminderMixin):
    """
    Send reminder emails to reviewers
    """

    def send_reminders(self):
        return self.item.send_review_reminder_emails(from_user=self.request.user)

    def can_read(self, user):
        return user.profile.user_class in ['lawyer']

    def can_edit(self, user):
        return user.profile.is_lawyer

    def can_delete(self, user):
        return user.profile.is_lawyer


rulez_registry.register("can_read", RemindReviewers)
rulez_registry.register("can_edit", RemindReviewers)
rulez_registry.register("can_delete", RemindReviewers)


class RemindSignatories(BaseReminderMixin):
    """
    Send reminder emails to signers
    """
    specific_attribute = 'signers.all()'

    def send_reminders(self):
        return self.item.send_sign_reminder_emails(from_user=self.request.user)

    def can_read(self, user):
        return user.profile.user_class in ['lawyer']

    def can_edit(self, user):
        return user.profile.is_lawyer

    def can_delete(self, user):
        return user.profile.is_lawyer


rulez_registry.register("can_read", RemindSignatories)
rulez_registry.register("can_edit", RemindSignatories)
rulez_registry.register("can_delete", RemindSignatories)


class RemindRequestedRevisionInvitee(BaseReminderMixin):
    """
    Reminders for requested document invitees
    """
    specific_attribute = 'responsible_party'

    def send_reminders(self):
        return [self.item.send_document_requested_emails(from_user=self.request.user, subject='[REMINDER] Please provide a document')]

    def get_object(self):
        return self.item

    def can_read(self, user):
        return user in self.matter.participants.all()

    def can_edit(self, user):
        return user.matter_permissions(matter=self.matter).has_permission(manage_document_reviews=True) is True

    def can_delete(self, user):
        return user.matter_permissions(matter=self.matter).has_permission(manage_document_reviews=True) is True


rulez_registry.register("can_read", RemindRequestedRevisionInvitee)
rulez_registry.register("can_edit", RemindRequestedRevisionInvitee)
rulez_registry.register("can_delete", RemindRequestedRevisionInvitee)
