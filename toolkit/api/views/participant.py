# -*- coding: UTF-8 -*-
"""
Matter Participant endpoint
"""
from django.forms import EmailField
from django.contrib.auth.models import User

from rulez import registry as rulez_registry

from rest_framework import generics
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework import status as http_status

from toolkit.apps.matter.signals import MATTER_ADD_PARTICIPANT
from toolkit.apps.workspace.models import Workspace
from toolkit.apps.workspace.services import EnsureCustomerService

from ..serializers import MatterSerializer
from .mixins import (MatterMixin,)


class MatterParticipant(generics.CreateAPIView,
                        generics.DestroyAPIView,
                        MatterMixin):
    """
    Endpoint for adding and removing matter level participants
    these participants have the same level permission as the lawyer
    unless they are user.profile.is_customer == True

    POST,DELETE /matters/:matter_slug/participant
    {
        "email": "username@example.com"
    }

    @TODO @QUESTION security hazard a lawyer can add another lawyer, but can that new
    lawyer add other lawyers?
    """
    model = Workspace
    serializer_class = MatterSerializer
    lookup_field = 'slug'
    lookup_url_kwarg = 'matter_slug'

    def validate_data(self, data):
        if all(k in data.keys() for k in ["email"]) is False:
            raise exceptions.ParseError('request.DATA must be: {"email": "username@example.com"}')

        email_validator = EmailField()
        # will raise error if incorrect
        email_validator.clean(data.get('email'))

    def create(self, request, **kwargs):
        data = request.DATA.copy()
        self.validate_data(data=data)
        email = data.get('email')

        try:
            new_participant = User.objects.get(email=email)
        except User.DoesNotExist:
            #
            # @BUSINESSRULE if an email does not exist then create them as
            # customer
            #
            service = EnsureCustomerService(email=email, full_name=None)
            is_new, new_participant, profile = service.process()

        if new_participant not in self.matter.participants.all():
            self.matter.participants.add(new_participant)
            MATTER_ADD_PARTICIPANT.send(sender=self, matter=self.matter, user=new_participant)

        return Response(status=http_status.HTTP_202_ACCEPTED)

    def delete(self, request, **kwargs):
        # extract from url arg
        data = {"email": self.kwargs.get('email')}
        self.validate_data(data=data)
        email = data.get('email')

        # will raise Does not exist if not found
        participant_to_remove = User.objects.get(email=email)

        #
        # @BUSINESSRULE you cannot delete the primary lawyer
        #
        if participant_to_remove == self.matter.lawyer:
            raise exceptions.PermissionDenied('You are not able to remove the primary lawyer')

        if participant_to_remove in self.matter.participants.all():
            self.matter.participants.remove(participant_to_remove)

        return Response(status=http_status.HTTP_202_ACCEPTED)

    def can_read(self, user):
        return user.profile.user_class in ['lawyer', 'customer']

    def can_edit(self, user):
        return user.profile.is_lawyer

    def can_delete(self, user):
        return user.profile.is_lawyer


rulez_registry.register("can_read", MatterParticipant)
rulez_registry.register("can_edit", MatterParticipant)
rulez_registry.register("can_delete", MatterParticipant)
