# -*- coding: UTF-8 -*-
from django.shortcuts import get_object_or_404

from rest_framework import viewsets
from rest_framework import generics

from toolkit.apps.workspace.models import Workspace
from toolkit.core.item.models import Item

from ..serializers import MatterSerializer
from ..serializers import ItemSerializer


class MatterEndpoint(viewsets.ModelViewSet):
    """
    Primary Matter ViewSet
    """
    model = Workspace
    serializer_class = MatterSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        user = self.request.user
        return user.workspace_set.mine(user=user)

"""
Matter resolver Mixins
"""

class MatterMixin(object):
    """
    Get the matter from the url slug :matter_slug
    """
    def dispatch(self, request, *args, **kwargs):
        # provide the matter object
        self.matter = get_object_or_404(Workspace, slug=kwargs.get('matter_slug'))
        super(MatterMixin, self).dispatch(request=request, *args, **kwargs)


class MatterItemsQuerySetMixin(MatterMixin):
    """
    Mixin to filter the Items objects by their matter via the url :matter_slug
    """
    def get_queryset(self):
        return Item.objects.filter(matter=self.matter)


"""
Custom Api Endpoints
"""


class MatterItemsView(generics.ListAPIView, MatterMixin):
    """
    /matters/:matter_slug/items/ (GET)
        Allow the [lawyer,customer] user to list items that belong to them
    """
    model = Item
    serializer_class = ItemSerializer


class MatterItemView(generics.UpdateAPIView, generics.DestroyAPIView, generics.RetrieveAPIView, MatterItemsQuerySetMixin):
    """
    /matters/:matter_slug/items/:item_slug/ (GET,PATCH,DELETE)
        Allow the [lawyer,customer] user to list, and update an existing item
        objects; that belong to them
    """
    model = Item
    serializer_class = ItemSerializer
    lookup_field = 'slug'
    lookup_url_kwarg = 'item_slug'

