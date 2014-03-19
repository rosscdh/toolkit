# -*- coding: UTF-8 -*-
from actstream.models import Action
from rest_framework import generics
from rest_framework import status as http_status
from rest_framework.response import Response
from toolkit.api.serializers import ItemActivitySerializer
from toolkit.api.views.mixins import MatterItemsQuerySetMixin
from rulez import registry as rulez_registry
from toolkit.core.services.matter_activity import MatterActivityEventService


class ItemCommentEndpoint(MatterItemsQuerySetMixin, generics.CreateAPIView):
    """
    Endpoint to post new comments for item in matter
    """
    model = Action
    serializer_class = ItemActivitySerializer
    lookup_field = 'slug'
    lookup_url_kwarg = 'item_slug'

    def create(self, request, **kwargs):
        comment = request.DATA.get('comment', '')
        if comment.strip() not in [None, '']:
            MatterActivityEventService(self.matter).add_comment(user=request.user, item=self.get_object(),
                                                                comment=comment)
            return Response(status=http_status.HTTP_201_CREATED)
        else:
            return Response(status=http_status.HTTP_400_BAD_REQUEST, data={'reason': 'You should send a comment.'})

    def can_edit(self, user):
        return user.profile.user_class in ['lawyer', 'customer']


rulez_registry.register("can_edit", ItemCommentEndpoint)