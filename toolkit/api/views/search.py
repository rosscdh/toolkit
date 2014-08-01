# -*- coding: utf-8 -*-
from django.shortcuts import get_object_or_404

from rest_framework import generics
from rest_framework.response import Response

from rulez import registry as rulez_registry

from toolkit.api.serializers import SimpleMatterSerializer, MatterSearchSerializer
from toolkit.apps.workspace.models import Workspace

from itertools import chain


class MatterSearchEndpoint(generics.ListAPIView):
    """
    Endpoint for getting a list of activity-stream-actions for matter
    """
    model = Workspace
    serializer_class = SimpleMatterSerializer
    lookup_url_kwarg = 'matter_slug'
    lookup_field = 'slug'

    def initialize_request(self, request, *args, **kwargs):
        # provide the matter object
        self.matter = get_object_or_404(Workspace, slug=kwargs.get('matter_slug'))
        return super(MatterSearchEndpoint, self).initialize_request(request, *args, **kwargs)

    def get_object(self, **kwargs):
        return self.matter

    def get_queryset(self):
        # return  list(self.matter.item_set.all()) + [i.revision_set.all() for i in self.matter.item_set.all()] + [i.task_set.all() for i in self.matter.item_set.all()] + [i.attachments.all() for i in self.matter.item_set.all()]
        # combined_querysets = [[i] for i in self.matter.item_set.all()]  \
        #                      + [i.revision_set.all() for i in self.matter.item_set.all()]  \
        #                      + [i.task_set.all() for i in self.matter.item_set.all()]  \
        #                      + [i.attachments.all() for i in self.matter.item_set.all()]
        combined_querysets = [[i] for i in self.matter.item_set.all()]  \
                                     + [i.task_set.all() for i in self.matter.item_set.all()]  \
                                     + [i.attachments.all() for i in self.matter.item_set.all()]

        #return list(chain(*combined_querysets))
        return [i for i in list(chain(*combined_querysets)) if i.can_read(user=self.request.user)]

    def get_serializer(self, query_set, **kwargs):
        context = self.get_serializer_context()
        return MatterSearchSerializer(query_set, many=kwargs.get('many', True), context=context)

    def list(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        serializer = self.get_serializer(self.object_list, many=True)

        return Response(serializer.data)

    def can_read(self, user):
        return user in self.get_object().participants.all()


rulez_registry.register("can_read", MatterSearchEndpoint)
