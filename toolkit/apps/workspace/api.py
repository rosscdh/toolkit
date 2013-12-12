# -*- coding: UTF-8 -*-
from rest_framework.viewsets import ModelViewSet

from toolkit.apps.eightythreeb.signals import lawyer_invite_customer

from .models import InviteKey
from .serializers import InviteKeySerializer


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
