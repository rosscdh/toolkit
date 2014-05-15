# -*- coding: UTF-8 -*-
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404

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

    def _get_newest_comment_by_user(self, user):
        try:
            return Action.objects.get_queryset().filter(
                actor_content_type=ContentType.objects.get_for_model(user),
                actor_object_id=user.id,
                verb=u'commented',
                action_object_content_type=ContentType.objects.get_for_model(self.item),
                action_object_object_id=self.item.id,
                target_content_type=ContentType.objects.get_for_model(self.matter),
                target_object_id=self.matter.id)[0]
        except IndexError:
            return None

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
            # I am only allowed to update a comment if it is my latest one
            if comment_object.actor == request.user and \
                            comment_object == self._get_newest_comment_by_user(request.user):
                comment_object.data['comment'] = comment
                comment_object.save(update_fields=['data'])
                return Response(status=http_status.HTTP_200_OK)
            return Response(status=http_status.HTTP_403_FORBIDDEN,
                            data={'reason': u'You are not the creator of the comment you want to edit or it is not your newest comment.'})
        else:
            return Response(status=http_status.HTTP_400_BAD_REQUEST, data={'reason': 'You should send a comment.'})

    def get_object(self):
        return get_object_or_404(self.model, pk=self.kwargs.get('id'))

    def delete(self, request, *args, **kwargs):
        # lawyer can delete at any time
        # customer can ONLY delete if it is the newest comment

        # possibly change to time limit instead of this last-comment-rule for customers

        self.object = self.get_object()
        newest_comment_by_user = self._get_newest_comment_by_user(request.user)

        if self.object == newest_comment_by_user or request.user.profile.is_lawyer:
            # TODO: check if lawyer from different matter needs to be blocked
            self.object.delete()
            return Response(status=http_status.HTTP_204_NO_CONTENT)
        return Response(status=http_status.HTTP_403_FORBIDDEN)

    def can_edit(self, user):
        return user.profile.user_class in ['lawyer', 'customer']

rulez_registry.register("can_edit", ItemCommentEndpoint)
