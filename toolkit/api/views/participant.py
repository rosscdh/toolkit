# -*- coding: UTF-8 -*-
"""
Matter Participant endpoint
"""
from django.http import Http404
from django.forms import EmailField
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import UnsupportedMediaType

from rulez import registry as rulez_registry

from rest_framework import generics
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework import status as http_status

from toolkit.apps.matter.signals import PARTICIPANT_ADDED
from toolkit.apps.workspace.models import Workspace, ROLES, WorkspaceParticipants
from toolkit.apps.workspace.services import EnsureCustomerService
from toolkit.apps.matter.services import MatterParticipantRemovalService

from ..serializers import MatterSerializer, SimpleUserSerializer
from .mixins import (MatterMixin,)


class MatterParticipant(generics.CreateAPIView,
                        generics.UpdateAPIView,
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

    @staticmethod
    def validate_data(data, expected_keys=[]):
        if all(k in data.keys() for k in expected_keys) is False:
            raise exceptions.ParseError('request.DATA must have the following keys: %s' % ', '.join(expected_keys))

        email_validator = EmailField()
        # will raise error if incorrect
        email_validator.clean(data.get('email'))

    def create(self, request, **kwargs):
        data = request.DATA.copy()

        self.validate_data(data=data, expected_keys=['email', 'first_name', 'last_name', 'message', 'role'])

        email = data.get('email')
        role = data.get('role', 'client')  # @TODO need to review
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        message = data.get('message')
        permissions = data.get('permissions', {})

        try:
            new_participant = User.objects.get(email=email)

        except User.DoesNotExist:
            #
            # @BUSINESSRULE if an email does not exist then create them as
            # customer
            #
            # @TODO handle the lawyer userclass
            service = EnsureCustomerService(email=email, full_name='%s %s' % (first_name, last_name))
            is_new, new_participant, profile = service.process()

        if new_participant in self.matter.participants.all():
            # if they are already a participant they must update not create
            status = http_status.HTTP_304_NOT_MODIFIED

        else:
            status = http_status.HTTP_202_ACCEPTED
            self.matter.add_participant(user=new_participant, role=ROLES.get_value_by_name(role), **permissions)

            PARTICIPANT_ADDED.send(sender=self,
                                   matter=self.matter,
                                   participant=new_participant,
                                   user=request.user,
                                   note=message)

        return Response(SimpleUserSerializer(new_participant, context={'request': self.request}).data,
                        status=status)

    def update(self, request, *args, **kwargs):
        """
        used for updating permissions/role of user in matter
        """
        data = request.DATA.copy()

        email = data.get('email')
        role = data.get('role', None)
        permissions = data.get('permissions')

        try:
            participant = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'details': 'User does not exist (email=%s)' % email})

        perms = participant.matter_permissions(matter=self.matter)
        if perms.pk is None:
            # user is not a participant of this matter yet
            raise Http404

        if role is not None:
            perms.role = ROLES.get_value_by_name(role)

        perms.update_permissions(**permissions)
        perms.save()

        return Response(SimpleUserSerializer(participant, context={'request': self.request}).data,
                        status=http_status.HTTP_202_ACCEPTED)

    def delete(self, request, **kwargs):
        status = http_status.HTTP_202_ACCEPTED
        
        # extract from url arg
        data = {"email": self.kwargs.get('email')}

        self.validate_data(data=data, expected_keys=['email'])
        email = data.get('email')

        # will raise Does not exist if not found
        participant_to_remove = User.objects.get(email=email)

        try:
            service = MatterParticipantRemovalService(matter=self.matter, removing_user=request.user)
            service.process(participant_to_remove)

        except PermissionDenied, e:
            status = http_status.HTTP_403_FORBIDDEN

        return Response(status=status)

    def can_read(self, user):
        return user in self.get_object().participants.all() or user == self.get_object().lawyer

    def can_edit(self, user):
        role = self.request.DATA.get('role')
        if not role:
            return False

        # manage_participants overrides manage_clients
        if user.matter_permissions(matter=self.matter).has_permission(manage_participants=True) is True:
            return True
        elif ROLES.get_value_by_name(role.lower()) == ROLES.client:
            return user.matter_permissions(matter=self.matter).has_permission(manage_clients=True) is True

    def can_delete(self, user):
        user_to_work_on = User.objects.get(email=self.kwargs.get('email'))

        # manage_participants overrides manage_clients
        if user.matter_permissions(matter=self.matter).has_permission(manage_participants=True) is True \
                or user_to_work_on == self.request.user:
            return True
        elif user_to_work_on.matter_permissions(matter=self.matter).role == ROLES.client:
            return user.matter_permissions(matter=self.matter).has_permission(manage_clients=True) is True


rulez_registry.register("can_read", MatterParticipant)
rulez_registry.register("can_edit", MatterParticipant)
rulez_registry.register("can_delete", MatterParticipant)
