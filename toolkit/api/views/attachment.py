# -*- coding: UTF-8 -*-
from django.shortcuts import get_object_or_404

from rulez import registry as rulez_registry

from rest_framework import viewsets
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response

from toolkit.core.attachment.models import Attachment

from .mixins import (MatterItemsQuerySetMixin,)

from ..serializers import (AttachmentSerializer,
                           ItemSerializer,
                           SimpleUserSerializer)


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
            return user == self.get_object().uploaded_by \
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

    # def get_serializer(self, instance=None, data=None, files=None, many=False, partial=False):
    #     # pop it
    #     if data is not None:
    #         item_serializer_data = ItemSerializer(self.item, context={'request': self.request}).data
    #         user_serializer_data = SimpleUserSerializer(self.request.user, context={'request': self.request}).data

    #         data.update({
    #             'item': item_serializer_data.get('url'),
    #             'uploaded_by': user_serializer_data.get('url'),
    #         })

    #     return super(AttachmentView, self).get_serializer(instance=instance,
    #                                                       data=data,
    #                                                       files=files,
    #                                                       many=many,
    #                                                       partial=partial)

    def create(self, request, *args, **kwargs):
        """
        Have had to copy directly the method from the base class
        because of the need to modify the data
        """
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
            # Asynchronous celery task to upload the file
            #
            # @TODO add this back when the bug with viewing a matter signal is fixed
            # run_task(crocodoc_upload_task,
            #          user=self.request.user, revision=self.object)

            #
            # Custom signal event
            #
            self.matter.actions.created_attachment(user=self.request.user,
                                                   item=self.item,
                                                   attachment=self.object)
            return Response(serializer.data, status=status.HTTP_201_CREATED,
                            headers=headers)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def destroy(self, request, **kwargs):
    #     resp = super(AttachmentView, self).destroy(request=request, **kwargs)
    #     self.matter.actions.deleted_attachment(user=self.request.user,
    #                                            item=self.item,
    #                                            attachment=self.attachment)
    #     return resp

    def pre_save(self, obj):
        """
        @BUSINESSRULE Enforce the revision.uploaded_by and revision.item
        """
        if obj.name is None:
            file = self.request.FILES.get('file')

            if file is not None:
                #
                # Set the object name to the filename
                #
                obj.name = file.name

        super(AttachmentView, self).pre_save(obj=obj)

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
