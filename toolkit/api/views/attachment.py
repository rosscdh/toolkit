# -*- coding: UTF-8 -*-
from django.http import Http404
from django.core.cache import cache
from django.utils.timezone import utc
from django.shortcuts import get_object_or_404

from rulez import registry as rulez_registry

from rest_framework import viewsets
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response

from toolkit.core.attachment.models import Attachment

from .mixins import (MatterItemsQuerySetMixin,)

from ..serializers import AttachmentSerializer
from ..serializers import ItemSerializer
from ..serializers import UserSerializer


import logging
import datetime

logger = logging.getLogger('django.request')


class AttachmentEndpoint(viewsets.ModelViewSet):
    model = Attachment
    serializer_class = AttachmentSerializer


class AttachmentView(MatterItemsQuerySetMixin,
                     generics.CreateAPIView,
                     generics.RetrieveAPIView,
                     generics.DestroyAPIView):
    """
    /matters/:matter_slug/items/:item_slug/attachment (GET,POST,DELETE)
    """
    model = Attachment
    serializer_class = AttachmentSerializer
    lookup_field = 'slug'
    lookup_url_kwarg = 'item_slug'

    def initial(self, request, *args, **kwargs):
        self.item = get_object_or_404(self.matter.item_set.all(), slug=kwargs.get('item_slug'))
        self.attachment = self.get_object()
        super(AttachmentView, self).initial(request, *args, **kwargs)

    def get_object(self):
        """
        Ensure we get self.item
        but return the Attachment object as self.object
        """
        if self.request.method in ['POST']:
            self.attachment = Attachment(uploaded_by=self.request.user, item=self.item) if self.request.user.is_authenticated() else None

        else:
            # get,patch
            self.attachment = self.item.attachments.all().last()

            if self.request.method in ['GET'] and self.attachment is None:
                raise Http404

        return self.attachment

    def get_serializer_context(self):
        return {'request': self.request}

    def get_serializer(self, instance=None, data=None, files=None, many=False, partial=False):
        # pop it
        if data is not None:
            item_serializer_data = ItemSerializer(self.item, context={'request': self.request}).data
            user_serializer_data = UserSerializer(self.request.user, context={'request': self.request}).data

            data.update({
                'item': item_serializer_data.get('url'),
                'uploaded_by': user_serializer_data.get('url'),
            })

        return super(AttachmentView, self).get_serializer(instance=instance,
                                                          data=data,
                                                          files=files,
                                                          many=many,
                                                          partial=partial)

    # def handle_revision_status(self, status=None):
    #     #
    #     # Status change
    #     #
    #     if status is not None:
    #         #
    #         # if we have a current revision then test to see if the status is
    #         # being changes from its previous revision
    #         # TODO move into model?
    #         #
    #         if self.revision and int(status) != self.revision.status:
    #             previous_instance = self.revision.previous()
    #             if previous_instance is not None:
    #                 self.matter.actions.revision_changed_status(user=self.request.user,
    #                                                             revision=self.revision,
    #                                                             previous_status=previous_instance.status)

    # def update(self, request, *args, **kwargs):
    #     #
    #     # Status change
    #     #
    #     self.handle_revision_status(status=request.DATA.get('status', None))
    #     # #
    #     # # sign_in_progress events
    #     # # @NOTE that we POP the sign_in_progress value as its not a valid field
    #     # #
    #     # self.handle_sign_in_progress(sign_in_progress=request.DATA.pop('sign_in_progress', None))
    #
    #     return super(ItemCurrentRevisionView, self).update(request=request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """
        Have had to copy directly the method from the base class
        because of the need to modify the data
        """
        request_data = request.DATA.copy()

        serializer = self.get_serializer(self.attachment, data=request_data, files=request.FILES)

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
                                                   attachment=self.attachment)
            return Response(serializer.data, status=status.HTTP_201_CREATED,
                            headers=headers)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, **kwargs):
        resp = super(AttachmentView, self).destroy(request=request, **kwargs)
        self.matter.actions.deleted_attachment(user=self.request.user,
                                               item=self.item,
                                               attachment=self.attachment)
        return resp

    def pre_save(self, obj):
        """
        @BUSINESSRULE Enforce the revision.uploaded_by and revision.item
        """
        obj.item = self.item
        obj.uploaded_by = self.request.user

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
        # TODO: check if we want to change names from API:
        # Then we need to differentiate between:
        # - anyone who may create new attachments
        # - not anyone who may change the name/description/whatever
        return user in self.matter.participants.all()

    def can_delete(self, user):
        return user == self.get_object().uploaded_by \
               or user.matter_permissions(self.matter).has_permission(manage_attachments=True)


rulez_registry.register("can_read", AttachmentView)
rulez_registry.register("can_edit", AttachmentView)
rulez_registry.register("can_delete", AttachmentView)
