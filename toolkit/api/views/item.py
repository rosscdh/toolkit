# -*- coding: UTF-8 -*-
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied

from toolkit.core.item.models import Item
from ..serializers import ItemSerializer


class ItemEndpoint(viewsets.ModelViewSet):
    """
    """
    model = Item
    lookup_field = 'slug'
    serializer_class = ItemSerializer

    # def list(self, request, **kwargs):
    #     """
    #     @TODO limit by user client
    #     """
    #     import pdb;pdb.set_trace()
    #     return super(ClientEndpoint, self).list(request=request, **kwargs)