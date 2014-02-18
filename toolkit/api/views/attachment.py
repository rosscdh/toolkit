# -*- coding: UTF-8 -*-
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied

from toolkit.core.attachment.models import Attachment
from toolkit.core.item.models import Item
from ..serializers import AttachmentSerializer


class AttachmentEndpoint(viewsets.ModelViewSet):
    """
    """
    model = Attachment
    serializer_class = AttachmentSerializer

    def get_queryset(self):
        items = Item.objects.filter(participants=self.request.user)
        return Attachment.objects.filter(item__in=items)