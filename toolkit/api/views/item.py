# -*- coding: UTF-8 -*-
from actstream.models import Action
from rest_framework import viewsets

from rulez import registry as rulez_registry

from rest_framework import generics

from toolkit.core.item.models import Item

from .mixins import (MatterItemsQuerySetMixin,)

from ..serializers import ItemSerializer


class ItemEndpoint(viewsets.ModelViewSet):
    """
    This endpoint is not actually "used". item objects are accessed via
    the api/v1/matters/:matter_slug/items/:item_slug endpoint
    this class is only present to provide rest_framework with the machinary it
    requires to generate hypermedia urls (in this case they are not used)
    """
    model = Item
    lookup_field = 'slug'
    serializer_class = ItemSerializer

    def get_serializer_context(self):
        return {'request': self.request}

    def can_read(self, user):
        self.object = self.get_object_or_none()
        if self.object is not None:
            return user.profile.user_class in ['lawyer', 'customer'] and user in self.object.participants()
        return False

    def can_edit(self, user):
        self.object = self.get_object_or_none()
        if self.object is not None:
            return user.profile.is_lawyer and user in self.object.matter.participants.all()  # allow any lawyer who is a participant
        return False

    def can_delete(self, user):
        self.object = self.get_object_or_none()
        if self.object is not None:
            return user.profile.is_lawyer and user in self.object.matter.participants.all()  # allow any lawyer who is a participant
        return False

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
        if created is True:
            # issue the created item signal
            self.matter.actions.item_created(user=self.request.user, item=obj)

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

    def update(self, request, *args, **kwargs):
        old_object = self.get_object()
        response = super(MatterItemView, self).update(request, *args, **kwargs)
        new_object = self.get_object()

        if old_object is not None:
            if old_object.name != new_object.name:
                self.matter.actions.item_rename(user=self.request.user, item=new_object, previous_name=old_object.name)

            if old_object.status != new_object.status:
                self.matter.actions.item_changed_status(user=self.request.user,
                                                        item=new_object,
                                                        previous_status=old_object.get_status_display())

            if old_object.responsible_party != new_object.responsible_party and new_object.responsible_party is None:
            #sign-app merge# if previous_instance.is_requested != instance.is_requested and instance.is_requested is False:
                self.matter.actions.cancel_user_upload_revision_request(item=new_object,
                                                                        removing_user=self.request.user,
                                                                        removed_user=old_object.responsible_party)

            if old_object.is_complete != new_object.is_complete:
                if new_object.is_complete is True:
                    self.matter.actions.item_closed(user=self.request.user, item=new_object)
                else:
                    self.matter.actions.item_reopened(user=self.request.user, item=new_object)

            if not old_object.is_deleted and new_object.is_deleted:
                self.matter.actions.item_deleted(user=self.request.user, item=new_object)

        return response

    def can_read(self, user):
        return user.profile.user_class in ['lawyer', 'customer'] and user in self.matter.participants.all()

    def can_edit(self, user):
        return user.profile.is_lawyer and user in self.matter.participants.all()  # allow any lawyer who is a participant

    def can_delete(self, user):
        return user.profile.is_lawyer and user in self.matter.participants.all()  # allow any lawyer who is a participant


rulez_registry.register("can_read", MatterItemView)
rulez_registry.register("can_edit", MatterItemView)
rulez_registry.register("can_delete", MatterItemView)
