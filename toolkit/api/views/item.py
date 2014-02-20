# -*- coding: UTF-8 -*-
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied

from toolkit.core.item.models import Item
from ..serializers import ItemSerializer


class ItemEndpoint(viewsets.ModelViewSet):
    """
    """
    model = Item
    serializer_class = ItemSerializer