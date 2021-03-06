# -*- coding: UTF-8 -*-
from django.http import Http404
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from rulez import registry as rulez_registry

from rest_framework import viewsets
from rest_framework import generics
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework import status as http_status

from toolkit.apps.sign.models import SignDocument

from toolkit.apps.workspace.services import EnsureCustomerService

from ..serializers import SimpleUserWithSignUrlSerializer
from ..serializers import SignatureSerializer

from .review import BaseReviewerOrSignerMixin

import logging
logger = logging.getLogger('django.request')


class SignatureEndpoint(viewsets.ModelViewSet):
    """
    Primary Matter ViewSet
    """
    model = SignDocument
    serializer_class = SignatureSerializer
    lookup_field = 'slug'

    def pre_delete(self, obj, **kwargs):
        obj.signers.clear()
        obj.document.signers.clear()

        return super(SignatureEndpoint, self).pre_delete(obj=obj, **kwargs)

    def can_read(self, user):
        return user.profile.user_class in ['lawyer', 'customer']

    def can_edit(self, user):
        obj = self.get_object()
        return user.matter_permissions(matter=obj.matter).has_permission(manage_signature_requests=True) is True

    def can_delete(self, user):
        obj = self.get_object()
        return user.matter_permissions(matter=obj.matter).has_permission(manage_signature_requests=True) is True


rulez_registry.register("can_read", SignatureEndpoint)
rulez_registry.register("can_edit", SignatureEndpoint)
rulez_registry.register("can_delete", SignatureEndpoint)


class ItemRevisionSignersView(generics.ListAPIView,
                              generics.CreateAPIView,
                              BaseReviewerOrSignerMixin):
    """
    /matters/:matter_slug/items/:item_slug/revision/signers/ (GET,POST)
        [lawyer,customer] to list, create signers
    """
    serializer_class = SignatureSerializer  # as we are returning the revision and not the item

    def get_queryset_provider(self):
        return self.revision.signers

    def list(self, request, *args, **kwargs):
        sign_document = self.revision.primary_signdocument
        serializer = self.get_serializer(sign_document)
        return Response(serializer.data)

    def create(self, request, **kwargs):
        """
        we already have the matter item and revision we just need to
        1. ensure the user exists
        2. is the user already a signer for this revision
        3. if not make them one
        """
        status = http_status.HTTP_400_BAD_REQUEST
        headers = None
        message = request.DATA.get('message')
        signers = request.DATA.get('signers')

        if not signers:
            data = {'detail': 'You need to provide at least 1 signer: You provided: %s' % signers}

        else:

            self.revision.signers.clear() # remove existing signers

            for signer in signers:

                first_name = signer.get('first_name')
                last_name = signer.get('last_name')
                email = signer.get('email')

                if email is None:
                    raise exceptions.APIException('You must provide a list of signers and they must have an email attribute {"signers": [{"email": "me@example.com"},]}')

                try:
                    user = User.objects.get(email=email)

                except User.DoesNotExist:

                    # we have a new user here
                    user_service = EnsureCustomerService(email=email, full_name='%s %s' % (first_name, last_name))
                    is_new, user, profile = user_service.process()

                if user not in self.get_queryset():
                    # add to the join if not there already
                    # add the user to the purpose of this endpoint object review||signature
                    self.revision.signers.add(user)

                    #
                    # Send invite to review Email
                    #
                    # self.item.send_invite_to_sign_emails(from_user=request.user, to=[user], message=message)
                    # @NB Dont invite them to sign yet, as we ahve to setup the document for signing first

                    #
                    # add activity
                    #
                    self.matter.actions.invite_user_as_signer(item=self.item,
                                                              inviting_user=request.user,
                                                              invited_user=user)

            sign_document = self.revision.primary_signdocument
            sign_document.requested_by = request.user
            sign_document.save(update_fields=['requested_by'])
            sign_document.signers.clear() # remove existing signers from sign object
            sign_document.signers = self.revision.signers.all()

            if not sign_document:
                raise Exception('Could not get Revision.primary_signdocument')

            #
            # @TODO make this async with run_task
            #
            sign_document.create_unclaimed_draft(requester_email_address=request.user.email)

            # we have the user at this point
            serializer = self.get_serializer(sign_document)

            headers = self.get_success_headers(serializer.data)
            status = http_status.HTTP_201_CREATED
            data = serializer.data

        return Response(data, status=status, headers=headers)

    def can_read(self, user):
        return user.profile.user_class in ['lawyer', 'customer']

    def can_edit(self, user):
        return user.matter_permissions(matter=self.matter).has_permission(manage_signature_requests=True) is True

    def can_delete(self, user):
        return user.matter_permissions(matter=self.matter).has_permission(manage_signature_requests=True) is True


rulez_registry.register("can_read", ItemRevisionSignersView)
rulez_registry.register("can_edit", ItemRevisionSignersView)
rulez_registry.register("can_delete", ItemRevisionSignersView)


# singular looking at a specific
class ItemRevisionSignerView(generics.RetrieveAPIView,
                             generics.DestroyAPIView,
                             BaseReviewerOrSignerMixin):
    """
    Singular
    /matters/:matter_slug/items/:item_slug/revision/signer/:username (GET,DELETE)
        [lawyer,customer] to view, delete signers
    """
    model = User  # to allow us to use get_object generically
    serializer_class = SimpleUserWithSignUrlSerializer  # as we are returning the revision and not the item
    lookup_field = 'username'
    lookup_url_kwarg = 'username'

    def get_queryset_provider(self):
        return self.revision.signing_request.signers

    def get_object(self):
        return get_object_or_404(User, username=self.kwargs.get('username'))

    def retrieve(self, request, **kwargs):
        status = http_status.HTTP_200_OK

        user = self.get_object()
        serializer = self.get_serializer(user)
        data = serializer.data

        #
        # Find ReviewDocumets where this user is the signer
        # Should only ever be one per user
        #
        user_signdocument_set = self.revision.signdocument_set.filter(signers__in=[user])

        if len(user_signdocument_set) == 0:
            #
            # must not be 0 as we have the users username thus they should be
            # part of the signers at this stage
            #
            logger.critical('A revision %s for a user %s has more than 0 signdocument they should have 1 per revision' % (self.revision, user))
            raise Http404

        if len(user_signdocument_set) > 1:
            #
            # Should never have more than 1
            #
            status = http_status.HTTP_406_NOT_ACCEPTABLE
            logger.critical('A revision %s for a user %s has more than 1 signdocument they should only have 1 per revision' % (self.revision, user))        

        # TODO: check if this was the last user to review the document.
        # if so: user_revision_review_complete()
        status = http_status.HTTP_200_OK

        return Response(data, status=status)

    def delete(self, request, **kwargs):
        status = http_status.HTTP_200_OK

        user = self.get_object()
        serializer = self.get_serializer(user)
        data = serializer.data

        if user in self.revision.signers.all():
            #
            # the user is in the signers set
            # remove them. This will (via the signals) remove them from the
            # signdocument object too
            #
            self.revision.signers.remove(user)

            self.matter.actions.cancel_user_upload_revision_request(item=self.item,
                                                                    removing_user=request.user,
                                                                    removed_user=user)
        else:
            status = http_status.HTTP_404_NOT_FOUND

        return Response(data, status=status)

    def can_read(self, user):
        return user.profile.user_class in ['lawyer', 'customer']

    def can_edit(self, user):
        return user.matter_permissions(matter=self.matter).has_permission(manage_signature_requests=True) is True

    def can_delete(self, user):
        return user.matter_permissions(matter=self.matter).has_permission(manage_signature_requests=True) is True


rulez_registry.register("can_read", ItemRevisionSignerView)
rulez_registry.register("can_edit", ItemRevisionSignerView)
rulez_registry.register("can_delete", ItemRevisionSignerView)
