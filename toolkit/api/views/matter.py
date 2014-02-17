# -*- coding: UTF-8 -*-
from rest_framework import viewsets
from rest_framework.response import Response

from toolkit.apps.workspace.models import Workspace
from ..serializers import MatterSerializer


class MatterEndpoint(viewsets.ModelViewSet):
    """
    """
    model = Workspace
    serializer_class = MatterSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        user = self.request.user
        return user.workspace_set.mine(user=user)