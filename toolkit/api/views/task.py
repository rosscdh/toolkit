# -*- coding: UTF-8 -*-
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from rest_framework import generics
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status as http_status

from rulez import registry as rulez_registry

from toolkit.decorators import mutable_request
from toolkit.apps.task.models import Task

from .mixins import MatterItemsQuerySetMixin
from ..serializers import (ItemSerializer,
                           TaskSerializer,
                           CreateTaskSerializer,)


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

    def update_assigned_to(self, task, assigned_to_usernames):
        # is not completed and we have assigned_to usernames
        if assigned_to_usernames is not None:
            current_assigned_to_usernames = [u.username for u in task.assigned_to.all()]
            #
            # should we also only send email to new assigned_to? and skip those that are already asigneees
            # as they will have recieved the original message? (ie. avoid resending emails and being annoying)
            #
            if assigned_to_usernames is not current_assigned_to_usernames:
                # Clear the set of current assigned_to users
                task.assigned_to.clear()
                # add the current state of users
                for username in assigned_to_usernames:
                    username = username.get('username') if type(username) in [dict] else username
                    task.assigned_to.add(User.objects.get(username=username))
                #
                # Send the email only if not completed
                #
                if task.is_complete is False:
                    task.send_assigned_to_email(from_user=self.request.user)


class ItemTasksView(GetTaskMixin,
                    generics.ListCreateAPIView,):
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
        context = super(ItemTasksView, self).get_serializer_context()
        context.update({'request': self.request})
        return context

    @mutable_request
    def create(self, request, **kwargs):
        self.item = self.get_item()

        # remove the assigned to from teh data set as we handle it manually
        assigned_to = request.DATA.pop('assigned_to', None)  # remove the assigned_to
        request.DATA.update({
            'item': ItemSerializer(self.item).data.get('url'),
            'created_by': request.user.username,
        })

        resp = super(ItemTasksView, self).create(request=request, **kwargs)

        # if the resp is OK then
        if resp.status_code in [201, 200]:
            # reset and update the assigned_to option
            self.update_assigned_to(task=self.object,
                                    assigned_to_usernames=assigned_to)

        return Response(self.get_serializer(self.object).data, status=http_status.HTTP_201_CREATED)

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

    @mutable_request
    def update(self, request, **kwargs):
        # remove the assigned to from teh data set as we handle it manually
        assigned_to = request.DATA.pop('assigned_to', None)  # remove the assigned_to

        # what is the value of is complete before this update takes place
        self.task = self.get_object()
        current_task_is_complete = self.task.is_complete

        # process normally
        resp = super(ItemTaskView, self).update(request=request, **kwargs)

        # refresh object
        self.task = self.task.__class__.objects.get(pk=self.task.pk)

        #
        # Handle status change events
        #
        if current_task_is_complete is False and self.task.is_complete is True:
            # was completed
            self.item.matter.actions.task_completed(user=request.user, item=self.item, task=self.task)

        if current_task_is_complete is True and self.task.is_complete is False:
            # was reopened
            self.item.matter.actions.task_reopened(user=request.user, item=self.item, task=self.task)

        # if the resp is OK then
        if resp.status_code in [200]:
            # reset and update the assigned_to option
            self.update_assigned_to(task=self.object, assigned_to_usernames=assigned_to)

        return resp

    def delete(self, request, **kwargs):
        self.task = self.get_object()

        resp = super(ItemTaskView, self).delete(request=request, **kwargs)

        # event
        self.item.matter.actions.deleted_task(user=request.user, item=self.item, task=self.task)

        return resp

    def can_read(self, user):
        return user in self.matter.participants.all()

    def can_edit(self, user):
        self.task = self.get_object()
        return hasattr(self, 'item') is False  \
               or user == self.task.created_by  \
               or user.matter_permissions(matter=self.item.matter).has_permission(manage_items=True) is True

    def can_delete(self, user):
        self.task = self.get_object()
        perms = user.matter_permissions(matter=self.item.matter)
        return user == self.task.created_by  \
               or perms.role is perms.ROLES.colleague \
               or perms.has_permission(manage_items=True) is True


rulez_registry.register("can_read", ItemTaskView)
rulez_registry.register("can_edit", ItemTaskView)
rulez_registry.register("can_delete", ItemTaskView)
