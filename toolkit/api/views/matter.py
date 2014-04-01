# -*- coding: UTF-8 -*-

from rulez import registry as rulez_registry

from rest_framework import viewsets
from rest_framework import generics

from rest_framework.response import Response

from toolkit.core.item.models import Item

from toolkit.core.attachment.models import Revision

from toolkit.apps.workspace.models import Workspace

from .mixins import (MatterMixin,
                     _MetaJSONRendererMixin,
                     SpecificAttributeMixin,)

from ..serializers import MatterSerializer
from ..serializers.matter import LiteMatterSerializer

import logging
logger = logging.getLogger('django.request')


class MatterEndpoint(viewsets.ModelViewSet):
    """
    Primary Matter ViewSet
    """
    model = Workspace
    serializer_class = MatterSerializer
    lookup_field = 'slug'
    renderer_classes = (_MetaJSONRendererMixin,)

    def get_meta(self):
        return {
            'matter': {
                'status': None,
            },
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
