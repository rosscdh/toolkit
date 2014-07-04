# -*- coding: UTF-8 -*-
from rest_framework import generics
from rest_framework import viewsets

from rulez import registry as rulez_registry

from toolkit.apps.task.models import Task

from .mixins import MatterItemsQuerySetMixin
from ..serializers import TaskSerializer


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
    def get_queryset(self):
        item = super(GetTaskMixin, self).get_queryset().first()
        return self.model.objects.filter(item=item)


class ItemTasksView(GetTaskMixin,
                    generics.ListCreateAPIView):
    """
    /matters/:matter_slug/items/:item_slug/tasks (GET,POST)
        Allow the [lawyer,customer] user to list and create item tasks in a matter
    """
    model = Task
    serializer_class = TaskSerializer

    def get_serializer_context(self):
        return {'request': self.request}

    def can_read(self, user):
        return True

    def can_edit(self, user):
        return True

    def can_delete(self, user):
        return True


rulez_registry.register("can_read", ItemTasksView)
rulez_registry.register("can_edit", ItemTasksView)
rulez_registry.register("can_delete", ItemTasksView)


class ItemTaskView(GetTaskMixin,
                   generics.ListCreateAPIView,
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
        return user.matter_permissions(matter=self.matter).has_permission(manage_items=True) is True

    def can_delete(self, user):
        return user.matter_permissions(matter=self.matter).has_permission(manage_items=True) is True


rulez_registry.register("can_read", ItemTaskView)
rulez_registry.register("can_edit", ItemTaskView)
rulez_registry.register("can_delete", ItemTaskView)
