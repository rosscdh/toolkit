# -*- coding: UTF-8 -*-
from django.conf import settings
from django.contrib.auth.models import User
from django.http import Http404
from django.shortcuts import get_object_or_404

from rest_framework import mixins, status as http_status, viewsets
from rest_framework.response import Response
from rulez import registry as rulez_registry

from toolkit.api.serializers import (DiscussionCommentSerializer,
                                     DiscussionSerializer,
                                     LiteDiscussionSerializer,
                                     SimpleUserSerializer)

from toolkit.apps.discussion.models import DiscussionComment
from toolkit.apps.workspace.services import EnsureCustomerService

from .mixins import MatterMixin, ThreadMixin


class DiscussionEndpoint(MatterMixin, viewsets.ModelViewSet):
    lookup_field = 'slug'
    model = DiscussionComment

    def get_queryset(self):
        queryset = self.model.objects.for_model(self.matter).filter(parent=None)

        if self.action == 'list':
            # handle archived/unarchived
            is_archived = self.request.QUERY_PARAMS.get('archived', False)
            queryset = queryset.filter(is_archived=is_archived)

            # only show threads I'm a participant of
            queryset = queryset.filter(participants__in=[self.request.user])

        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return LiteDiscussionSerializer
        return DiscussionSerializer

    def check_object_permissions(self, request, obj):
        if request.user not in obj.participants.all():
            self.permission_denied(request)

        super(DiscussionEndpoint, self).check_object_permissions(request=request, obj=obj)

    def pre_save(self, obj):
        obj.matter = self.matter
        obj.parent = None
        obj.site_id = settings.SITE_ID
        obj.user = self.request.user

        return super(DiscussionEndpoint, self).pre_save(obj=obj)

    def post_save(self, obj, created=False):
        if created:
            obj.participants.add(self.request.user)

        return super(DiscussionEndpoint, self).post_save(obj=obj)

    def can_read(self, user):
        return user in self.matter.participants.all()

    def can_edit(self, user):
        return user in self.matter.participants.all()

    def can_delete(self, user):
        return user in self.matter.participants.all()

rulez_registry.register("can_read", DiscussionEndpoint)
rulez_registry.register("can_edit", DiscussionEndpoint)
rulez_registry.register("can_delete", DiscussionEndpoint)


class DiscussionCommentEndpoint(ThreadMixin, viewsets.ModelViewSet):
    lookup_field = 'slug'
    model = DiscussionComment
    serializer_class = DiscussionCommentSerializer

    def get_queryset(self):
        return self.model.objects.for_model(self.matter).filter(parent=self.thread.pk)

    def pre_save(self, obj):
        obj.matter = self.matter
        obj.parent = self.model.objects.get(pk=self.thread.pk)
        obj.site_id = settings.SITE_ID
        obj.user = self.request.user

        return super(DiscussionCommentEndpoint, self).pre_save(obj=obj)

    def can_read(self, user):
        return user in self.thread.participants.all()

    def can_edit(self, user):
        return user in self.thread.participants.all()

    def can_delete(self, user):
        return False
        # return user in self.thread.participants.all()

rulez_registry.register("can_read", DiscussionCommentEndpoint)
rulez_registry.register("can_edit", DiscussionCommentEndpoint)
rulez_registry.register("can_delete", DiscussionCommentEndpoint)


class DiscussionParticipantEndpoint(ThreadMixin, mixins.CreateModelMixin, viewsets.ReadOnlyModelViewSet):
    lookup_field = 'username'
    model = DiscussionComment.participants.through
    serializer_class = SimpleUserSerializer

    def create(self, request, *args, **kwargs):
        email = request.DATA.get('email')
        username = request.DATA.get('username')
        first_name = request.DATA.get('first_name')
        last_name = request.DATA.get('last_name')

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

        if user not in self.thread.participants.all():
            # add to the join if not there already
            self.thread.participants.add(user)

        # we have the user at this point
        serializer = self.get_serializer(user)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=http_status.HTTP_201_CREATED, headers=headers)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_through_object()
        self.pre_delete(obj)
        obj.delete()
        self.post_delete(obj)
        return Response(status=http_status.HTTP_204_NO_CONTENT)

    def get_through_object(self, queryset=None):
        if queryset is None:
            queryset = self.model.objects
        else:
            pass  # Deprecation warning

        username = self.kwargs.get('username')

        filter_kwargs = {
            'discussioncomment': self.thread.pk,
            'user__username': username
        }

        obj = get_object_or_404(queryset, **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj

    def get_queryset(self):
        return self.thread.participants.all()

    def can_read(self, user):
        return user in self.thread.participants.all()

    def can_edit(self, user):
        return user in self.thread.participants.all()

    def can_delete(self, user):
        return user in self.thread.participants.all()

rulez_registry.register("can_read", DiscussionParticipantEndpoint)
rulez_registry.register("can_edit", DiscussionParticipantEndpoint)
rulez_registry.register("can_delete", DiscussionParticipantEndpoint)
