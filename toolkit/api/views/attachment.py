# -*- coding: UTF-8 -*-
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied

from toolkit.core.attachment.models import Revision
from toolkit.core.item.models import Item
from ..serializers import AttachmentSerializer


class AttachmentEndpoint(viewsets.ModelViewSet):
    """
    """
    model = Revision
    serializer_class = AttachmentSerializer

    def get_queryset(self):
        items = Item.objects.filter(participants=self.request.user)
        return Revision.objects.filter(item__in=items)