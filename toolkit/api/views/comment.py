# -*- coding: UTF-8 -*-
import datetime
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rulez import registry as rulez_registry

from actstream.models import Action

from rest_framework import generics
from rest_framework import status as http_status
from rest_framework.response import Response
from rest_framework import permissions

from toolkit.api.serializers import ItemActivitySerializer
from toolkit.api.views.mixins import MatterItemsQuerySetMixin


class ItemCommentEndpoint(MatterItemsQuerySetMixin,
                          generics.CreateAPIView,
                          generics.UpdateAPIView,
                          generics.DestroyAPIView):
    """
    Endpoint to post new comments for item in matter
    """
    model = Action
    serializer_class = ItemActivitySerializer
    lookup_field = 'slug'
    lookup_url_kwarg = 'item_slug'

    permission_classes = (permissions.IsAuthenticated, )

    def initialize_request(self, request, *args, **kwargs):
        """
        when creating a new comment we need self.item
        but when deleting a comment, get_object needs to return the REAL object and not the overriden
            get_object from MatterItemsQuerySetMixin
        deletion does NOT use rulez because it tries to use the overriden get_object instead of the one we want to use
        """
        result = super(ItemCommentEndpoint, self).initialize_request(request, *args, **kwargs)
        self.item = super(ItemCommentEndpoint, self).get_object()
        return result

    def create(self, request, **kwargs):
        comment = request.DATA.get('comment', '')
        if comment.strip() not in [None, '']:
            self.matter.actions.add_item_comment(user=request.user,
                                                 item=self.item,
                                                 comment=comment)
            # the comment is created via a signal, so we do NOT have the comment-object with its id directly.
            return Response(status=http_status.HTTP_201_CREATED)
        else:
            return Response(status=http_status.HTTP_400_BAD_REQUEST, data={'reason': 'You should send a comment.'})

    def update(self, request, *args, **kwargs):
        comment = request.DATA.get('comment', '')
        if comment.strip() not in [None, '']:
            comment_object = self.get_object()
            # I am only allowed to update a comment if it is mine and it is not older than EDIT_COMMENTS_DURATION
            if comment_object.actor == request.user and comment_object.timestamp > \
                            timezone.now() - datetime.timedelta(minutes=settings.EDIT_COMMENTS_DURATION):
                comment_object.data['comment'] = comment
                comment_object.save(update_fields=['data'])
                return Response(status=http_status.HTTP_200_OK)
            return Response(status=http_status.HTTP_403_FORBIDDEN,
                            data={'reason': u'Your comment is too old to be edited.'})
        else:
            return Response(status=http_status.HTTP_400_BAD_REQUEST, data={'reason': 'You should send a comment.'})

    def get_object(self):
        return get_object_or_404(self.model, pk=self.kwargs.get('id'))

    def delete(self, request, *args, **kwargs):
        # lawyer can delete at any time
        # customer can ONLY delete if it not older than DELETE_COMMENTS_DURATION

        self.object = self.get_object()

        if request.user.profile.is_lawyer or self.object.timestamp > \
                        timezone.now() - datetime.timedelta(minutes=settings.DELETE_COMMENTS_DURATION):
            # TODO: check if lawyer from different matter needs to be blocked
            self.object.delete()
            return Response(status=http_status.HTTP_204_NO_CONTENT)
        return Response(status=http_status.HTTP_403_FORBIDDEN)

    def can_edit(self, user):
        return user.profile.user_class in ['lawyer', 'customer']

rulez_registry.register("can_edit", ItemCommentEndpoint)
