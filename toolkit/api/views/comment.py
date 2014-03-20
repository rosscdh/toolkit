# -*- coding: UTF-8 -*-
from actstream.models import Action, model_stream
from rest_framework import generics
from rest_framework import status as http_status
from rest_framework.response import Response
from toolkit.api.serializers import ItemActivitySerializer
from toolkit.api.views.mixins import MatterItemsQuerySetMixin
from rulez import registry as rulez_registry
from toolkit.core.item.models import Item
from toolkit.core.services.matter_activity import MatterActivityEventService


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

    def can_delete(self, user):
        bla = model_stream(Item)[:1][0].actor == user or user.profile.is_lawyer
        import pdb
        pdb.set_trace()
        return bla

rulez_registry.register("can_edit", ItemCommentEndpoint)
rulez_registry.register("can_delete", ItemCommentEndpoint)
