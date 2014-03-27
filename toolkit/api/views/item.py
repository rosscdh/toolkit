# -*- coding: UTF-8 -*-
from actstream.models import Action
from rest_framework import viewsets

from django.conf import settings

from rulez import registry as rulez_registry

from mixpanel import Mixpanel
from rest_framework import generics

from toolkit.core.item.models import Item

from .mixins import (MatterItemsQuerySetMixin,)

from ..serializers import ItemSerializer


MIXPANEL_API_TOKEN = getattr(settings, 'MIXPANEL_API_TOKEN', None)


class ItemEndpoint(viewsets.ModelViewSet):
    """
    """
    model = Item
    lookup_field = 'slug'
    serializer_class = ItemSerializer

    def get_serializer_context(self):
        return {'request': self.request}

    def can_read(self, user):
        return user.profile.user_class in ['lawyer', 'customer'] and user in self.object.participants.all()

    def can_edit(self, user):
        return user.profile.is_lawyer and user in self.object.matter.participants.all()  # allow any lawyer who is a participant

    def can_delete(self, user):
        return user.profile.is_lawyer and user in self.object.matter.participants.all()  # allow any lawyer who is a participant


rulez_registry.register("can_read", ItemEndpoint)
rulez_registry.register("can_edit", ItemEndpoint)
rulez_registry.register("can_delete", ItemEndpoint)


"""
Matter item endpoints
"""

class MatterItemsView(MatterItemsQuerySetMixin,
                      generics.ListCreateAPIView):
    """
    /matters/:matter_slug/items/ (GET,POST)
        Allow the [lawyer,customer] user to list and create items in a matter
    """
    model = Item
    serializer_class = ItemSerializer

    def get_serializer_context(self):
        return {'request': self.request}

    def pre_save(self, obj):
        obj.matter = self.matter  # set in MatterItemsQuerySetMixin
        return super(MatterItemsView, self).pre_save(obj=obj)

    def post_save(self, obj, created=False):
        if created:
            # send event off to Mixpanel
            if MIXPANEL_API_TOKEN:
                mp = Mixpanel(MIXPANEL_API_TOKEN)

                mp.track(self.request.user.email, 'Item Created', {
                    'Account Type': self.request.user.profile.account_type,
                    'Client': obj.matter.client.name,
                    'Firm': self.request.user.profile.firm_name,
                    'User Type': self.request.user.profile.type,
                    'Via': 'web',
                })

                mp.people_increment(self.request.user.email, {'Items Created': 1})

    def can_read(self, user):
        return user.profile.user_class in ['lawyer', 'customer'] and user in self.matter.participants.all()

    def can_edit(self, user):
        return user.profile.is_lawyer and user in self.matter.participants.all()  # allow any lawyer who is a participant

    def can_delete(self, user):
        return user.profile.is_lawyer and user in self.matter.participants.all()  # allow any lawyer who is a participant


rulez_registry.register("can_read", MatterItemsView)
rulez_registry.register("can_edit", MatterItemsView)
rulez_registry.register("can_delete", MatterItemsView)


class MatterItemView(generics.UpdateAPIView,
                     generics.DestroyAPIView,
                     generics.RetrieveAPIView,
                     MatterItemsQuerySetMixin):
    """
    /matters/:matter_slug/items/:item_slug/ (GET,PATCH,DELETE)
        Allow the [lawyer,customer] user to list, and update an existing item
        objects; that belong to them
    """
    model = Item
    serializer_class = ItemSerializer
    lookup_field = 'slug'
    lookup_url_kwarg = 'item_slug'

    def get_serializer_context(self):
        return {'request': self.request}

    def can_read(self, user):
        return user.profile.user_class in ['lawyer', 'customer'] and user in self.matter.participants.all()

    def can_edit(self, user):
        return user.profile.is_lawyer and user in self.matter.participants.all()  # allow any lawyer who is a participant

    def can_delete(self, user):
        return user.profile.is_lawyer and user in self.matter.participants.all()  # allow any lawyer who is a participant


rulez_registry.register("can_read", MatterItemView)
rulez_registry.register("can_edit", MatterItemView)
rulez_registry.register("can_delete", MatterItemView)
