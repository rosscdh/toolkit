# -*- coding: utf-8 -*-
from django.shortcuts import get_object_or_404

from rest_framework import viewsets
from rest_framework import generics

from actstream.models import Action, model_stream
from rulez import registry as rulez_registry

from toolkit.api.serializers.activity import ActivitySerializer
from toolkit.apps.workspace.models import Workspace


class ActivityEndpoint(viewsets.ModelViewSet):
    """
    Endpoint for Actions from activity-stream
    """
    model = Action
    lookup_field = 'id'
    serializer_class = ActivitySerializer

    def can_read(self, user):
        return True

rulez_registry.register("can_read", ActivityEndpoint)


class MatterActivityEndpoint(generics.ListAPIView):
    """
    Endpoint for getting a list of activity-stream-actions for matter
    """
    model = Workspace
    serializer_class = ActivitySerializer
    lookup_field = 'matter_slug'
    lookup_url_kwarg = 'matter_slug'

    def initialize_request(self, request, *args, **kwargs):
        # provide the matter object
        self.matter = get_object_or_404(Workspace, slug=kwargs.get('matter_slug'))
        return super(MatterActivityEndpoint, self).initialize_request(request, *args, **kwargs)

    def get_queryset(self):
        return model_stream(self.model).filter(target_object_id=self.matter.pk)

    def can_read(self, user):
        return user.profile.user_class in ['lawyer', 'customer']


rulez_registry.register("can_read", MatterActivityEndpoint)