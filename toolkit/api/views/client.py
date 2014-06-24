# -*- coding: UTF-8 -*-
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied

from rulez import registry as rulez_registry

from toolkit.core.client.models import Client
from ..serializers import ClientSerializer


class ClientEndpoint(viewsets.ModelViewSet):
    """
    no GUI-interface available.
    so no permission-check for workspace.manage_clients added yet.
    """
    model = Client
    lookup_field = 'slug'
    serializer_class = ClientSerializer

    def list(self, request, **kwargs):
        """
        @TODO limit by user client
        """
        return super(ClientEndpoint, self).list(request=request, **kwargs)

    def can_read(self, user):
        return user.profile.is_lawyer

    def can_edit(self, user):
        return user.profile.is_lawyer

    def can_delete(self, user):
        return user.profile.is_lawyer


rulez_registry.register("can_read", ClientEndpoint)
rulez_registry.register("can_edit", ClientEndpoint)
rulez_registry.register("can_delete", ClientEndpoint)