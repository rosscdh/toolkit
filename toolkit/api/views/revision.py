# -*- coding: UTF-8 -*-
from django.http import Http404
from django.shortcuts import get_object_or_404

from rulez import registry as rulez_registry

from rest_framework import viewsets
from rest_framework import generics
from toolkit.core.services import MatterActivityEventService

from toolkit.core.attachment.models import Revision

from .mixins import (MatterItemsQuerySetMixin,)

from ..serializers import RevisionSerializer
from ..serializers import ItemSerializer
from ..serializers import UserSerializer


class RevisionEndpoint(viewsets.ModelViewSet):
    """
    """
    model = Revision
    serializer_class = RevisionSerializer

    def get_queryset(self):
        """
        @TODO limit to current users items
        # items = Item.objects.filter(participants=self.request.user)
        # return Revision.objects.filter(item__in=items)
        """
        return super(RevisionEndpoint, self).get_queryset()


class ItemCurrentRevisionView(generics.CreateAPIView,
                              generics.UpdateAPIView,
                              generics.DestroyAPIView,
                              generics.RetrieveAPIView,
                              MatterItemsQuerySetMixin):
    """
    /matters/:matter_slug/items/:item_slug/revision (GET,POST,PATCH,DELETE)
        [lawyer,customer] to get,create,update,delete the latest revision
    Get the Item object and access its item.latest_revision to get access to
    the latest revision, but then return the serialized revision in the response
    """
    #parser_classes = (parsers.FileUploadParser,) # his will obly be necessary if we stop using filepicker.io which passes us a url

    model = Revision  # to allow us to use get_object generically
    serializer_class = RevisionSerializer  # as we are returning the revision and not the item
    lookup_field = 'slug'
    lookup_url_kwarg = 'item_slug'

    def initial(self, request, *args, **kwargs):
        self.item = get_object_or_404(self.matter.item_set.all(), slug=kwargs.get('item_slug'))
        self.revision = self.get_object()
        super(ItemCurrentRevisionView, self).initial(request, *args, **kwargs)

    def get_object(self):
        """
        Ensure we get self.item
        but return the Revision object as self.object
        """
        if self.request.method in ['POST']:

            self.revision = Revision(uploaded_by=self.request.user, item=self.item) if self.request.user.is_authenticated() else None

        else:

            # get,patch
            self.revision = self.get_latest_revision()

            if self.request.method in ['GET'] and self.revision is None:
                raise Http404

        return self.revision

    def get_latest_revision(self):
        return self.item.latest_revision

    def get_serializer_context(self):
        return {'request': self.request}

    def get_serializer(self, instance=None, data=None,
                       files=None, many=False, partial=False):
        # pop it
        if data is not None:
            item_serializer_data = ItemSerializer(self.item, context={'request': self.request}).data
            user_serializer_data = UserSerializer(self.request.user, context={'request': self.request}).data

            data.update({
                'item': item_serializer_data.get('url'),
                'uploaded_by': user_serializer_data.get('url'),
            })

        return super(ItemCurrentRevisionView, self).get_serializer(instance=instance,
                                                                   data=data,
                                                                   files=files,
                                                                   many=many,
                                                                   partial=partial)

    def create(self, request, **kwargs):
        resp = super(ItemCurrentRevisionView, self).create(request=request, **kwargs)
        MatterActivityEventService(self.matter).created_revision(user=self.request.user,
                                                                 item=self.item,
                                                                 revision=self.revision)
        return resp

    def destroy(self, request, **kwargs):
        resp = super(ItemCurrentRevisionView, self).destroy(request=request, **kwargs)
        MatterActivityEventService(self.matter).deleted_revision(user=self.request.user,
                                                                 item=self.item,
                                                                 revision=self.revision)
        return resp

    def pre_save(self, obj):
        """
        @BUSINESSRULE Enforce the revision.uploaded_by and revision.item
        """
        obj.item = self.item
        obj.uploaded_by = self.request.user

        if obj.name is None:
            executed_file = self.request.FILES.get('executed_file')
            if executed_file is not None:
                #
                # Set the object name to the filename if no obj.name exists
                #
                obj.name = executed_file.name

        super(ItemCurrentRevisionView, self).pre_save(obj=obj)

    def can_read(self, user):
        return user.profile.user_class in ['lawyer', 'customer'] and user in self.matter.participants.all()

    def can_edit(self, user):
        return user.profile.is_lawyer and user in self.matter.participants.all()  # allow any lawyer who is a participant

    def can_delete(self, user):
        return user.profile.is_lawyer and user in self.matter.participants.all()  # allow any lawyer who is a participant


rulez_registry.register("can_read", ItemCurrentRevisionView)
rulez_registry.register("can_edit", ItemCurrentRevisionView)
rulez_registry.register("can_delete", ItemCurrentRevisionView)


class ItemSpecificReversionView(ItemCurrentRevisionView):
    def get_latest_revision(self):
        version = int(self.kwargs.get('version', 1))

        try:
            revision = [v for c, v in enumerate(self.item.revision_set.all()) if int(c + 1) == version][0]
        except:
            revision = None

        return revision
