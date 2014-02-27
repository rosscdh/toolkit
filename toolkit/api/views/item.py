# -*- coding: UTF-8 -*-
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied

from rulez import registry as rulez_registry

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
    #     return super(ItemEndpoint, self).list(request=request, **kwargs)

    def can_read(self, user):
        return user.profile.user_class in ['lawyer', 'customer'] and user in item.matter.participants.all()

    def can_edit(self, user):
        return user.profile.is_lawyer and user in item.matter.participants.all()  # allow any lawyer who is a participant

    def can_delete(self, user):
        return user.profile.is_lawyer and user in item.matter.participants.all()  # allow any lawyer who is a participant


rulez_registry.register("can_read", ItemEndpoint)
rulez_registry.register("can_edit", ItemEndpoint)
rulez_registry.register("can_delete", ItemEndpoint)