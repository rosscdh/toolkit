# -*- coding: UTF-8 -*-
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import CreateAPIView
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin

from toolkit.apps.eightythreeb.signals import lawyer_invite_customer

from .models import InviteKey
from .models import Workspace, Tool
from .serializers import InviteKeySerializer, WorkspaceToolSerializer


class InviteKeyViewSet(ModelViewSet):
    """
    """
    queryset = InviteKey.objects.all()
    serializer_class = InviteKeySerializer

    def create(self, request, *args, **kwargs):
        resp = super(InviteKeyViewSet, self).create(request, *args, **kwargs)

        if resp.status_code == 201:
            # created
            instance = self.object.tool.model.objects.get(pk=self.object.tool_object_id)
            lawyer_invite_customer.send(sender=request.user,
                                        instance=instance,
                                        actor_name=request.user.email)
        return resp


class WorkspaceToolsView(CreateAPIView):
    """
    Api Endpoint to provide access to associated workspace tools
    """
    queryset = Workspace.objects.all()
    serializer_class = WorkspaceToolSerializer
    lookup_field = 'slug'
    lookup_url_kwarg = 'slug'

    def create(self, request, *args, **kwargs):
        self.workspace = self.get_object()
        self.tool = get_object_or_404(Tool, slug=request.DATA.get('tool'))  # tool slug

        self.object = self.tool #switcheroo for teh serializer
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)

        if self.tool not in self.workspace.tools.all():
            self.workspace.tools.add(self.tool)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED,
                            headers=headers)

        return Response(serializer.data, status=status.HTTP_200_OK)