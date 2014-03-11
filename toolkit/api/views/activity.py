# -*- coding: utf-8 -*-
from actstream.models import Action, model_stream
from django.shortcuts import get_object_or_404
from rest_framework import generics
from toolkit.api.serializers.activity import ActivitySerializer
from toolkit.apps.workspace.models import Workspace
from rulez import registry as rulez_registry


__author__ = 'Marius Burfey <marius.burfey@ambient-innovation.com> - 11.03.14'


class MatterActivityView(generics.ListAPIView):
    """
    Endpoint for getting (and creating?) activity-stream-actions for matter
    """
    model = Workspace
    serializer_class = ActivitySerializer
    lookup_field = 'target_object_id'
    lookup_url_kwarg = 'matter_slug'

    def initialize_request(self, request, *args, **kwargs):
        # provide the matter object
        self.matter = get_object_or_404(Workspace, slug=kwargs.get('matter_slug'))
        return super(MatterActivityView, self).initialize_request(request, *args, **kwargs)

    def get_queryset(self):
        # import pdb;pdb.set_trace()
        return model_stream(self.model).filter(target_object_id=self.matter.pk)

    def can_read(self, user):
        return user.profile.user_class in ['lawyer', 'customer']


rulez_registry.register("can_read", MatterActivityView)