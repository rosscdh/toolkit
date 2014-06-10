# -*- coding: UTF-8 -*-
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404

from rest_framework import generics, viewsets
from rulez import registry as rulez_registry
from threadedcomments.models import ThreadedComment

from toolkit.api.serializers import DiscussionCommentSerializer, DiscussionSerializer, LiteDiscussionSerializer

from .mixins import MatterMixin


class DiscussionEndpoint(MatterMixin, viewsets.ModelViewSet):
    model = ThreadedComment

    def get_queryset(self):
        return self.model.objects.for_model(self.matter).filter(parent=None)

    def get_serializer_class(self):
        if self.action == 'list':
            return LiteDiscussionSerializer
        return DiscussionSerializer

    def can_read(self, user):
        return user.profile.user_class in ['lawyer', 'customer'] and user in self.matter.participants.all()

rulez_registry.register("can_read", DiscussionEndpoint)


class DiscussionCommentEndpoint(MatterMixin,
                                viewsets.ModelViewSet):
    model = ThreadedComment
    serializer_class = DiscussionCommentSerializer

    def get_queryset(self):
        return self.model.objects.for_model(self.matter).filter(parent=self.kwargs.get('thread_id'))

    def pre_save(self, obj):
        obj.content_type_id = ContentType.objects.get_for_model(self.matter).pk
        obj.object_pk = self.matter.pk
        obj.parent = self.model.objects.get(pk=self.kwargs.get('thread_id'))
        obj.site_id = settings.SITE_ID
        obj.user = self.request.user

        return super(DiscussionCommentEndpoint, self).pre_save(obj=obj)

    def can_read(self, user):
        return user.profile.user_class in ['lawyer', 'customer'] and user in self.matter.participants.all()

rulez_registry.register("can_read", DiscussionCommentEndpoint)
