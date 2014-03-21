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
                          generics.DestroyAPIView):
    """
    Endpoint to post new comments for item in matter
    """
    model = Action
    serializer_class = ItemActivitySerializer
    lookup_field = 'slug'
    lookup_url_kwarg = 'item_slug'

    permission_classes = (permissions.IsAuthenticated,)

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
            self.matter.actions.add_item_comment(user=request.user, item=self.item,
                                                                comment=comment)
            return Response(status=http_status.HTTP_201_CREATED)
        else:
            return Response(status=http_status.HTTP_400_BAD_REQUEST, data={'reason': 'You should send a comment.'})

    def get_object(self):
        return get_object_or_404(self.model, pk=self.kwargs.get('id'))

    def delete(self, request, *args, **kwargs):
        # lawyer can delete at any time
        # customer can ONLY delete if it is the newest comment

        self.object = self.get_object()
        try:
            newest_comment_by_user = Action.objects.get_queryset().filter(
                actor_content_type=ContentType.objects.get_for_model(request.user),
                actor_object_id=request.user.id,
                verb=u'commented',
                action_object_content_type=ContentType.objects.get_for_model(self.item),
                action_object_object_id=self.item.id,
                target_content_type=ContentType.objects.get_for_model(self.matter),
                target_object_id=self.matter.id)[0]
        except IndexError:
            newest_comment_by_user = None

        if self.object == newest_comment_by_user or request.user.profile.is_lawyer:
            # TODO: check if lawyer from different matter needs to be blocked
            self.object.delete()
            return Response(status=http_status.HTTP_204_NO_CONTENT)
        return Response(status=http_status.HTTP_403_FORBIDDEN)

    def can_edit(self, user):
        return user.profile.user_class in ['lawyer', 'customer']

rulez_registry.register("can_edit", ItemCommentEndpoint)
