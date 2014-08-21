# -*- coding: UTF-8 -*-
from django.shortcuts import get_object_or_404

from rulez import registry as rulez_registry

from rest_framework import status
from rest_framework import viewsets
from rest_framework import generics
from rest_framework.response import Response

from toolkit.decorators import mutable_request, valid_request_filesize
from toolkit.core.attachment.models import Attachment

from .mixins import (MatterItemsQuerySetMixin,)

from ..serializers import (AttachmentSerializer,
                           ItemSerializer,)


import os
import logging
logger = logging.getLogger('django.request')


class AttachmentEndpoint(viewsets.ModelViewSet):
    model = Attachment
    lookup_field = 'slug'
    serializer_class = AttachmentSerializer

    def can_read(self, user):
        self.object = self.get_object()
        return user in self.object.item.matter.participants.all()

    def can_edit(self, user):
        self.object = self.get_object()
        if self.request.method == 'POST':
            # any participant may create new attachments
            return user in self.object.item.matter.participants.all()
        else:
            # must be PATCH to change the name/description/...
            return user == self.object.uploaded_by \
                   or user.matter_permissions(self.object.item.matter).has_permission(manage_attachments=True)

    def can_delete(self, user):
        self.object = self.get_object()
        return user == self.get_object().uploaded_by \
               or user.matter_permissions(self.object.item.matter).has_permission(manage_attachments=True)


rulez_registry.register("can_read", AttachmentEndpoint)
rulez_registry.register("can_edit", AttachmentEndpoint)
rulez_registry.register("can_delete", AttachmentEndpoint)


class AttachmentView(MatterItemsQuerySetMixin,
                     generics.ListCreateAPIView):
    """
    /matters/:matter_slug/items/:item_slug/attachment (GET,POST,DELETE)
    """
    model = Attachment
    serializer_class = AttachmentSerializer
    lookup_field = 'slug'
    lookup_url_kwarg = 'item_slug'

    def initial(self, request, *args, **kwargs):
        self.item = get_object_or_404(self.matter.item_set.all(), slug=kwargs.get('item_slug'))
        self.attachment = None
        super(AttachmentView, self).initial(request, *args, **kwargs)

    def get_queryset(self, **kwargs):
        return self.model.objects.filter(item=self.item)

    def get_serializer_context(self):
        return {'request': self.request}

    @mutable_request
    @valid_request_filesize
    def create(self, request, *args, **kwargs):
        """
        Have had to copy directly the method from the base class
        because of the need to modify the data
        """
        executed_file_from_filepicker = request.DATA.pop('executed_file', None)
        if executed_file_from_filepicker is not None:
            request.DATA.update({
                'attachment': executed_file_from_filepicker,  # rename from executed_file to attachment for serializer
                'name': request.DATA.pop('name', None),
            })
        else:
            # normal POST and the FILES object is present
            request.DATA.update({
                'name': request.FILES.get('attachment').name if request.FILES.get('attachment', None) is not None else None,
            })

        # set the defaults
        request.DATA.update({
            'item': ItemSerializer(self.item).data.get('url'),
            'uploaded_by': request.user.username,
        })

        serializer = self.get_serializer(data=request.DATA, files=request.FILES)

        if serializer.is_valid():
            self.pre_save(serializer.object)
            self.object = serializer.save(force_insert=True)
            self.post_save(self.object, created=True)

            headers = self.get_success_headers(serializer.data)

            #
            # Custom signal event
            #
            self.matter.actions.created_attachment(user=self.request.user,
                                                   item=self.item,
                                                   attachment=self.object)
            return Response(serializer.data, status=status.HTTP_201_CREATED,
                            headers=headers)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def can_read(self, user):
        return user in self.matter.participants.all()

    def can_edit(self, user):
        if self.request.method == 'POST':
            # anyone may create new attachments
            return user in self.matter.participants.all()
        else:
            # must be PATCH to change the name/description/...
            return user == self.get_object().uploaded_by \
                   or user.matter_permissions(self.matter).has_permission(manage_attachments=True)

    def can_delete(self, user):
        return user == self.get_object().uploaded_by \
               or user.matter_permissions(self.matter).has_permission(manage_attachments=True)


rulez_registry.register("can_read", AttachmentView)
rulez_registry.register("can_edit", AttachmentView)
rulez_registry.register("can_delete", AttachmentView)
