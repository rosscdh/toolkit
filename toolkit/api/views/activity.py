# -*- coding: utf-8 -*-
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType

from rest_framework import viewsets
from rest_framework import generics

from actstream.models import Action, model_stream
from rulez import registry as rulez_registry

from toolkit.api.serializers.activity import (MatterActivitySerializer,
                                              ItemActivitySerializer,)
from toolkit.apps.workspace.models import Workspace
from toolkit.core.item.models import Item
from toolkit.core.attachment.models import Revision


class ActivityEndpoint(viewsets.ModelViewSet):
    """
    Endpoint for Actions from activity-stream
    """
    model = Action
    lookup_field = 'id'
    serializer_class = MatterActivitySerializer

    def can_read(self, user):
        return True


rulez_registry.register("can_read", ActivityEndpoint)

#
# Matter endpoint
#


class MatterActivityEndpoint(generics.ListAPIView):
    """
    Endpoint for getting a list of activity-stream-actions for matter
    """
    model = Workspace
    serializer_class = MatterActivitySerializer
    lookup_field = 'matter_slug'

    def initialize_request(self, request, *args, **kwargs):
        # provide the matter object
        self.matter = get_object_or_404(Workspace, slug=kwargs.get('matter_slug'))
        return super(MatterActivityEndpoint, self).initialize_request(request, *args, **kwargs)

    def get_queryset(self):
        return model_stream(self.model).filter(target_object_id=self.matter.pk)

    def can_read(self, user):
        return user.profile.user_class in ['lawyer', 'customer']


rulez_registry.register("can_read", MatterActivityEndpoint)

#
# Item endpoint
#


class ItemActivityEndpoint(MatterActivityEndpoint):
    """
    Endpoint for getting a list of activity-stream-actions for matter items
    """
    serializer_class = ItemActivitySerializer

    def __init__(self, *args, **kwargs):
        super(ItemActivityEndpoint, self).__init__(*args, **kwargs)
        self.ITEM_CONTENT_TYPE = ContentType.objects.get_for_model(Item)
        self.REVISION_CONTENT_TYPE = ContentType.objects.get_for_model(Revision)

    def initialize_request(self, request, *args, **kwargs):
        # provide the matter object
        self.item = get_object_or_404(Item, slug=kwargs.get('item_slug'))
        return super(ItemActivityEndpoint, self).initialize_request(request, *args, **kwargs)

    def get_queryset(self):
        qs = super(ItemActivityEndpoint, self).get_queryset()
        revision_ids = [i.get('pk') for i in self.item.revision_set.all().values('pk')]
        return qs.filter(action_object_content_type=self.ITEM_CONTENT_TYPE, action_object_object_id=self.item.pk) | qs.filter(action_object_content_type=self.REVISION_CONTENT_TYPE, action_object_object_id__in=revision_ids)

    def can_read(self, user):
        return user.profile.user_class in ['lawyer', 'customer']


rulez_registry.register("can_read", ItemActivityEndpoint)
