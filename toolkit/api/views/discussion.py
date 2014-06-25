# -*- coding: UTF-8 -*-
from django.conf import settings
from django.contrib.auth.models import User
from django.http import Http404
from django.shortcuts import get_object_or_404

from rest_framework import generics, status as http_status, viewsets
from rest_framework.response import Response
from rulez import registry as rulez_registry

from toolkit.api.serializers import (DiscussionCommentSerializer,
                                     DiscussionSerializer,
                                     LiteDiscussionSerializer,
                                     SimpleUserSerializer)
from toolkit.apps.discussion.models import DiscussionComment
from toolkit.apps.workspace.services import EnsureCustomerService

from .mixins import MatterMixin


class DiscussionEndpoint(MatterMixin, viewsets.ModelViewSet):
    model = DiscussionComment

    def get_queryset(self):
        queryset = self.model.objects.for_model(self.matter).filter(parent=None)

        if self.action == 'list':
            is_archived = self.request.QUERY_PARAMS.get('archived', False)
            queryset = queryset.filter(is_archived=is_archived)

        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return LiteDiscussionSerializer
        return DiscussionSerializer

    def pre_save(self, obj):
        obj.matter = self.matter
        obj.parent = None
        obj.site_id = settings.SITE_ID
        obj.user = self.request.user

        return super(DiscussionEndpoint, self).pre_save(obj=obj)

    def can_read(self, user):
        return user.profile.user_class in ['lawyer', 'customer'] and user in self.matter.participants.all()

    def can_edit(self, user):
        return user.profile.user_class in ['lawyer', 'customer'] and user in self.matter.participants.all()

    def can_delete(self, user):
        return user.profile.user_class in ['lawyer', 'customer'] and user in self.matter.participants.all()

rulez_registry.register("can_read", DiscussionEndpoint)
rulez_registry.register("can_edit", DiscussionEndpoint)
rulez_registry.register("can_delete", DiscussionEndpoint)


class DiscussionCommentEndpoint(MatterMixin, viewsets.ModelViewSet):
    model = DiscussionComment
    serializer_class = DiscussionCommentSerializer

    def get_queryset(self):
        return self.model.objects.for_model(self.matter).filter(parent=self.kwargs.get('thread_id'))

    def pre_save(self, obj):
        obj.matter = self.matter
        obj.parent = self.model.objects.get(pk=self.kwargs.get('thread_id'))
        obj.site_id = settings.SITE_ID
        obj.user = self.request.user

        return super(DiscussionCommentEndpoint, self).pre_save(obj=obj)

    def can_read(self, user):
        return user in self.matter.participants.all()

    def can_edit(self, user):
        return user in self.matter.participants.all()

    def can_delete(self, user):
        return user in self.matter.participants.all()

rulez_registry.register("can_read", DiscussionCommentEndpoint)
rulez_registry.register("can_edit", DiscussionCommentEndpoint)
rulez_registry.register("can_delete", DiscussionCommentEndpoint)


class DiscussionParticipantEndpoint(MatterMixin,
                                    generics.CreateAPIView,
                                    generics.RetrieveDestroyAPIView,
                                    viewsets.GenericViewSet
                                    ):
    """
    Override a lot of the default views, as not all the participants are stored
    in the through table.
    """
    lookup_field = 'user__username'
    model = DiscussionComment.subscribers.through
    serializer_class = SimpleUserSerializer

    def create(self, request, *args, **kwargs):
        """
        We already have the discussion thread, we just need to:

        1. ensure the user exists; create if not
        2. subscribe them to the thread; if not already
        """
        username = request.DATA.get('username')
        first_name = request.DATA.get('first_name')
        last_name = request.DATA.get('last_name')
        email = request.DATA.get('email')

        if username is None and email is None:
            raise exceptions.APIException('You must provide a username or email')

        try:
            if username is not None:
                user = User.objects.get(username=username)
            elif email is not None:
                user = User.objects.get(email=email)
        except User.DoesNotExist:
            if email is None:
                raise Http404
            else:
                # we have a new user here
                user_service = EnsureCustomerService(email=email, full_name='%s %s' % (first_name, last_name))
                is_new, user, profile = user_service.process()

        if user not in self.thread.participants:
            # add to the join if not there already
            self.thread.subscribers.add(user)

        # we have the user at this point
        serializer = self.get_serializer(user)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=http_status.HTTP_201_CREATED, headers=headers)

    def list(self, request, **kwargs):
        serializer = self.get_serializer(self.thread.participants, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        try:
            self.object = self.get_object().user
        except Http404, e:
            try:
                self.object = User.objects.get(username=self.kwargs.get(self.lookup_field, None))
            except User.DoesNotExist:
                raise e

            if self.object not in self.thread.matter.participants.all():
                raise e

        serializer = self.get_serializer(self.object)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        try:
            obj = self.get_object()
        except Http404, e:
            """Can't delete matter participants"""
            try:
                obj = User.objects.get(username=self.kwargs.get(self.lookup_field, None))
            except User.DoesNotExist:
                raise e

            if obj not in self.thread.matter.participants.all():
                raise e

            return Response(status=http_status.HTTP_400_BAD_REQUEST, data={'reason': 'You can not unsubscribe a matter participant.'})

        self.pre_delete(obj)
        obj.delete()
        self.post_delete(obj)
        return Response(status=http_status.HTTP_204_NO_CONTENT)

    def get_queryset(self):
        return self.model.objects.filter(discussioncomment=self.thread)

    def initialize_request(self, request, *args, **kwargs):
        request = super(DiscussionParticipantEndpoint, self).initialize_request(request, *args, **kwargs)

        queryset = DiscussionComment.objects.for_model(self.matter)
        self.thread = get_object_or_404(queryset, pk=kwargs.get('thread_id'))
        return request

    def can_read(self, user):
        return user in self.matter.participants.all()

    def can_edit(self, user):
        return user in self.matter.participants.all()

    def can_delete(self, user):
        return user in self.matter.participants.all()

rulez_registry.register("can_read", DiscussionParticipantEndpoint)
rulez_registry.register("can_edit", DiscussionParticipantEndpoint)
rulez_registry.register("can_delete", DiscussionParticipantEndpoint)
