# -*- coding: UTF-8 -*-
from django.conf import settings
from django.shortcuts import get_object_or_404

from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rulez import registry as rulez_registry

from toolkit.api.serializers import (DiscussionCommentSerializer,
                                     DiscussionSerializer,
                                     LiteDiscussionSerializer,
                                     SimpleUserSerializer)
from toolkit.apps.discussion.models import DiscussionComment

from .mixins import MatterMixin


class DiscussionEndpoint(MatterMixin, viewsets.ModelViewSet):
    model = DiscussionComment

    def get_queryset(self):
        return self.model.objects.for_model(self.matter).filter(parent=None)

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
