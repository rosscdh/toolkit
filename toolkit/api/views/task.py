# -*- coding: UTF-8 -*-
from django.shortcuts import get_object_or_404

from rest_framework import generics
from rest_framework import viewsets

from rulez import registry as rulez_registry

from toolkit.apps.task.models import Task

from .mixins import MatterItemsQuerySetMixin
from ..serializers import (ItemSerializer,
                           TaskSerializer,
                           CreateTaskSerializer,
                           SimpleUserSerializer)

class TaskEndpoint(viewsets.ModelViewSet):
    """
    """
    model = Task
    lookup_field = 'slug'
    serializer_class = TaskSerializer

    def can_read(self, user):
        return True

    def can_edit(self, user):
        return True

    def can_delete(self, user):
        return True


rulez_registry.register("can_read", TaskEndpoint)
rulez_registry.register("can_edit", TaskEndpoint)
rulez_registry.register("can_delete", TaskEndpoint)


class GetTaskMixin(MatterItemsQuerySetMixin):
    def get_item(self):
        """
        get the item based on the MatterItemsQuerySetMixin selector which looks for matter items
        """
        return get_object_or_404(super(GetTaskMixin, self).get_queryset(), slug=self.kwargs.get('item_slug'))

    def get_queryset(self):
        self.item = self.get_item()
        return self.model.objects.for_item_by_user(item=self.item,
                                                   user=self.request.user)


class ItemTasksView(GetTaskMixin,
                    generics.ListCreateAPIView):
    """
    /matters/:matter_slug/items/:item_slug/tasks (GET,POST)
        Allow the [lawyer,customer] user to list and create item tasks in a matter
    """
    model = Task

    def get_serializer_class(self, **kwargs):
        if self.request.method in ['POST', 'PATCH']:
            return CreateTaskSerializer
        else:
            return TaskSerializer

    def get_serializer_context(self):
        return {'request': self.request}

    def create(self, request, **kwargs):
        request.DATA.update({
            'item': ItemSerializer(self.get_item()).data.get('url'),
            'created_by': request.user.username,
        })
        return super(ItemTasksView, self).create(request=request, **kwargs)

    def can_read(self, user):
        return user in self.matter.participants.all()

    def can_edit(self, user):
        return user in self.matter.participants.all()  \
               or user.matter_permissions(matter=self.item.matter).has_permission(manage_items=True)

    def can_delete(self, user):
        return False  # do not support delete


rulez_registry.register("can_read", ItemTasksView)
rulez_registry.register("can_edit", ItemTasksView)
rulez_registry.register("can_delete", ItemTasksView)


class ItemTaskView(GetTaskMixin,
                   generics.RetrieveUpdateAPIView,
                   generics.DestroyAPIView):
    """
    /matters/:matter_slug/items/:item_slug/tasks/:slug (GET,DELETE)
        Allow the [lawyer,customer] user to list and create item tasks in a matter
    """
    model = Task
    lookup_field = 'slug'
    serializer_class = TaskSerializer

    def get_serializer_context(self):
        return {'request': self.request}

    def can_read(self, user):
        return user in self.matter.participants.all()

    def can_edit(self, user):
        self.task = self.get_object()
        return hasattr(self, 'item') is False  \
               or user == self.task.created_by  \
               or user.matter_permissions(matter=self.item.matter).has_permission(manage_items=True) is True

    def can_delete(self, user):
        self.task = self.get_object()
        return user == self.task.created_by  \
               or user.matter_permissions(matter=self.item.matter).has_permission(manage_items=True) is True


rulez_registry.register("can_read", ItemTaskView)
rulez_registry.register("can_edit", ItemTaskView)
rulez_registry.register("can_delete", ItemTaskView)
