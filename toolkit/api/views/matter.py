# -*- coding: UTF-8 -*-
from django.shortcuts import get_object_or_404

from rulez import registry as rulez_registry

from rest_framework import viewsets
from rest_framework import generics
from rest_framework import exceptions

from rest_framework.response import Response
from rest_framework import status as http_status

from toolkit.core.item.models import Item

from toolkit.core.attachment.models import Revision

from toolkit.apps.workspace.models import Workspace
from toolkit.apps.review.models import ReviewDocument
from toolkit.apps.workspace.services import EnsureCustomerService

from .mixins import (MatterMixin,
                     _MetaJSONRendererMixin,
                     SpecificAttributeMixin,
                     _CreateActionMixin)

from .revision import ItemCurrentRevisionView

from ..serializers import MatterSerializer
from ..serializers.matter import LiteMatterSerializer
from ..serializers import UserSerializer

import logging
logger = logging.getLogger('django.request')


class MatterEndpoint(viewsets.ModelViewSet):
    """
    Primary Matter ViewSet
    """
    model = Workspace
    serializer_class = MatterSerializer
    lookup_field = 'slug'
    renderer_classes = (_CreateActionMixin, _MetaJSONRendererMixin)  # this ONLY calls the first JSONRenderer. Need to combine them.

    def get_meta(self):
        return {
            'matter': {'status': None},
            'item': {'status': Item.ITEM_STATUS.get_choices_dict()},
            'revision': {'status': Revision.REVISION_STATUS.get_choices_dict()},
        }

    def get_serializer_class(self):
        if self.action == 'list':
            # @BUSINESSRULE show the light matter serializer
            # if we are looking at the list
            return LiteMatterSerializer
        return self.serializer_class

    def get_queryset(self):
        user = self.request.user
        return user.workspace_set.mine(user=user)

    def pre_save(self, obj):
        """
        @BUSINESSRULE Enforce the lawyer being set as the current user
        """
        if obj.lawyer in [None, '']:
            if self.request.user.profile.is_lawyer:
                obj.lawyer = self.request.user

        return super(MatterEndpoint, self).pre_save(obj=obj)

    def can_read(self, user):
        return user.profile.user_class in ['lawyer', 'customer']

    def can_edit(self, user):
        return user.profile.is_lawyer

    def can_delete(self, user):
        return user.profile.is_lawyer


rulez_registry.register("can_read", MatterEndpoint)
rulez_registry.register("can_edit", MatterEndpoint)
rulez_registry.register("can_delete", MatterEndpoint)


"""
Custom Api Endpoints
"""


class BaseReviewerSignatoryMixin(ItemCurrentRevisionView):
    """
    Provides the object to access .signatories or .reviewers
    and their required functionality
    """
    serializer_class = UserSerializer  # as we are returning the revision and not the item

    def get_revision_object_set_queryset(self):
        raise NotImplementedError

    def process_event_purpose_object(self, user):
        """
        is this a review or a signature?
        """
        raise NotImplementedError

    def get_object(self):
        username = self.kwargs.get('username')
        self.revision = super(BaseReviewerSignatoryMixin, self).get_object()
        #
        # Return the User object contained in the signatory/reviewer join table
        #
        return get_object_or_404(self.get_revision_object_set_queryset(), username=username)

    def update(self, request, **kwargs):
        raise exceptions.MethodNotAllowed(method=self.request.method)

    def create(self, request, **kwargs):
        """
        as we are dealign with a set here we can actually create the object,
        we are trying to create just the join
        """
        try:
            user = self.get_object()
            status = http_status.HTTP_304_NOT_MODIFIED
        except:
            #
            # Only create the join if it doesnt already exist
            #
            username = self.kwargs.get('username')

            service = EnsureCustomerService(username=username, full_name=None)
            is_new, user, profile = service.process()

            # add to the join if not there already
            self.get_revision_object_set_queryset().add(user) if user not in self.get_revision_object_set_queryset().all() else None

            status = http_status.HTTP_201_CREATED

        # add the user to the purpose of this endpoint object review||signature
        self.process_event_purpose_object(user=user)

        # we have the user at this point
        serializer = self.get_serializer(user)
        headers = self.get_success_headers(serializer.data)

        return Response(serializer.data, status=status, headers=headers)

    def delete(self, request, **kwargs):
        """
        as we are dealign with a set here we can actually delete the object,
        we are trying to delete just the join
        """
        user = self.get_object()
        # we have the user at this point
        serializer = self.get_serializer(user)
        headers = None

        try:
            #
            # Only delete the join if it exists
            #
            self.get_revision_object_set_queryset().remove(user)

            status = http_status.HTTP_204_NO_CONTENT
            headers = self.get_success_headers(serializer.data)
        except Exception as e:
            logger.critical('delete failed: %s' % e)
            status = http_status.HTTP_400_BAD_REQUEST

        return Response(serializer.data, status=status, headers=headers)


class ItemRevisionReviewerView(BaseReviewerSignatoryMixin):
    """
    /matters/:matter_slug/items/:item_slug/revision/reviewer/:username (GET,POST,DELETE)
        [lawyer,customer] to view, create and delete reviewers
    Get the specified reviewer for info purposes
    """

    def get_revision_object_set_queryset(self):
        return self.revision.reviewers

    def process_event_purpose_object(self, user):
        # perform ReviewDocument get or create
        review_doc, is_new = ReviewDocument.objects.get_or_create(document=self.revision)
        # add the user to the reviewers if not there alreadt
        review_doc.reviewers.add(user) if user not in review_doc.reviewers.all() else None

        logger.info("Added %s to the ReviewDocument %s is_new: %s for revision: %s" % (user, review_doc, is_new, self.revision))


class ItemRevisionSignatoryView(BaseReviewerSignatoryMixin):
    """
    /matters/:matter_slug/items/:item_slug/revision/signatory/:username (DELETE)
        [lawyer,customer] to delete signatories
    Get the specified signatory for info purposes
    Is the same functionality as the ItemRevisionReviewerView
    """
    def get_revision_object_set_queryset(self):
        return self.revision.signatories


class ClosingGroupView(SpecificAttributeMixin,
                       generics.DestroyAPIView,
                       generics.CreateAPIView,
                       generics.RetrieveAPIView,
                       MatterMixin,):
    """
    /matters/:matter_slug/closing_group/:group (GET,POST,DELETE)
        [lawyer] can assign an item to a closing group

    view/create/delete a specific closing_group
    """
    model = Workspace
    serializer_class = MatterSerializer
    lookup_field = 'slug'
    lookup_url_kwarg = 'matter_slug'

    specific_attribute = 'closing_groups'

    def retrieve(self, request, **kwargs):
        obj = self.get_object()
        return Response(obj)

    def create(self, request, **kwargs):
        self.get_object()
        closing_group = self.kwargs.get('closing_group')

        closing_groups = self.object.add_closing_group(closing_group)
        self.object.save(update_fields=['data'])

        return Response(closing_groups)

    def delete(self, request, **kwargs):
        closing_groups = self.get_object()
        closing_group = self.kwargs.get('closing_group')

        try:
            closing_groups = self.object.remove_closing_group(closing_group, instance=self.object)
            self.object.save(update_fields=['data'])
        except Exception as e:
            logger.info('Could not delete closing_group: %s due to: %s' % (closing_group, e,))

        return Response(closing_groups)
