# -*- coding: utf-8 -*-
from django.views.generic import ListView

from rest_framework import generics
from rest_framework.response import Response
from rest_framework import permissions

from stored_messages.models import (Inbox, MessageArchive,)
from stored_messages.serializers import InboxSerializer


class InboxNotificationsView(ListView):
    model = Inbox
    template_name = 'notification/notification_list.html'

    def get_queryset(self):
        if self.request.user.is_authenticated():
            return self.model.objects.prefetch_related().filter(user=self.request.user)

        return self.model.objects.none()


class ReadNotificationsView(ListView):
    model = MessageArchive
    template_name = 'notification/notification_list.html'

    def get_queryset(self):
        if self.request.user.is_authenticated():
            return self.model.objects.prefetch_related().filter(user=self.request.user)

        return self.model.objects.none()


class InboxViewSet(generics.DestroyAPIView):
    """
    Provides `list` and `detail` actions, plus a `read` POST endpoint for
    marking inbox messages as read.
    """
    model = Inbox
    serializer_class = InboxSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        if self.request.user.is_authenticated():
            return Inbox.objects.filter(user=self.request.user)
        return Inbox.objects.none()

    def destroy(self, request, pk=None):
        """
        Mark the message as read (i.e. delete from inbox)
        """
        inbox_m = self.get_object()
        inbox_m.delete()

        return Response({'status': 'message marked as read'})


class MarkAllAsReadEndpoint(generics.DestroyAPIView):
    model = Inbox
    serializer_class = InboxSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def destroy(self, request, pk=None):
        """
        Mark the message as read (i.e. delete from inbox)
        """
        Inbox.objects.filter(user=request.user).delete()
        return Response({'status': 'message marked as read'})
