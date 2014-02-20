# -*- coding: UTF-8 -*-
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied

from toolkit.core.client.models import Client
from ..serializers import ClientSerializer


class ClientEndpoint(viewsets.ModelViewSet):
    """
    """
    model = Client
    serializer_class = ClientSerializer

    def list(self, request, **kwargs):
        """
        @TODO limit by user client
        """
        return super(ClientEndpoint, self).list(request=request, **kwargs)
        