# -*- coding: UTF-8 -*-
from django.http import Http404
from django.shortcuts import get_object_or_404

from rulez import registry as rulez_registry

from rest_framework import viewsets
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response

from toolkit.core.attachment.models import Revision

from .mixins import (MatterItemsQuerySetMixin,)

from ..serializers import RevisionSerializer
from ..serializers import ItemSerializer
from ..serializers import UserSerializer

from toolkit.apps.workspace.models import ROLES

import logging
logger = logging.getLogger('django.request')


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

    def update(self, request, *args, **kwargs):
        #
        # Status change
        #
        new_status = request.DATA.get('status', None)
        if new_status is not None:
            #
            # if we have a current revision then test to see if the status is
            # being changes from its previous revision
            # TODO move into model?
            #
            if self.revision and int(new_status) != self.revision.status:
                previous_instance = self.revision.previous()
                if previous_instance is not None:
                    self.matter.actions.revision_changed_status(user=self.request.user,
                                                                revision=self.revision,
                                                                previous_status=previous_instance.status)

        return super(ItemCurrentRevisionView, self).update(request=request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """
        Have had to copy directly the method from the base class
        because of the need to modify the data
        """
        #
        # NB! this is the important line
        # we always have a revision object! normally you dont you just pass in data and files
        # but this is a specialized case where we also always have a self.revision
        # so we have to clone the base class method except for the following lines
        #
        self.revision.pk = None  # ensure that we are CREATING a new one based on the existing one
        self.revision.is_current = True

        request_data = request.DATA.copy()

        request_data.update({
            # get default if none present
            'status': request_data.get('status', self.matter.default_status_index),  # get the default status if its not presetn
        })

        serializer = self.get_serializer(self.revision, data=request_data, files=request.FILES)

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
            self.matter.actions.created_revision(user=self.request.user,
                                                 item=self.item,
                                                 revision=self.revision)

            # see if there is a previous request for this revision
            # TODO: check if this works! absolutely not sure!
            if self.item.requested_by is not None:
                self.matter.actions.user_uploaded_revision(user=self.request.user,
                                                           item=self.item,
                                                           revision=self.revision)

            return Response(serializer.data, status=status.HTTP_201_CREATED,
                            headers=headers)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, **kwargs):
        resp = super(ItemCurrentRevisionView, self).destroy(request=request, **kwargs)
        self.matter.actions.deleted_revision(user=self.request.user,
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
                # Set the object name to the filename
                #
                obj.name = executed_file.name

        super(ItemCurrentRevisionView, self).pre_save(obj=obj)

    def can_read(self, user):
        """
        the participants, the latest_revision reviewers and the users which were activated can read
        """
        if user.matter_permissions(matter=self.matter).role == ROLES.client:
            return user in self.get_object().shared_with.all()
        return user in self.matter.participants.all() or user in self.item.latest_revision.reviewers.all()
        # return (user.profile.user_class in ['lawyer', 'customer'] and user in self.matter.participants.all() \
        #     or user in self.item.latest_revision.reviewers.all())

    def can_edit(self, user):
        return (user in self.matter.participants.all() \
               or (self.item.latest_revision is not None and user in self.item.latest_revision.reviewers.all())
               or user == self.item.responsible_party)
        # return (user.profile.user_class in ['lawyer', 'customer'] and user in self.matter.participants.all() \
        #     or (self.item.latest_revision is not None and user in self.item.latest_revision.reviewers.all())
        #     or user == self.item.responsible_party)

    def can_delete(self, user):
        return user in self.matter.participants.all() and \
               user.matter_permissions(matter=self.matter).has_permission(manage_items=True) is True
        # return user.profile.is_lawyer and user in self.matter.participants.all()  # allow any lawyer who is a participant


rulez_registry.register("can_read", ItemCurrentRevisionView)
rulez_registry.register("can_edit", ItemCurrentRevisionView)
rulez_registry.register("can_delete", ItemCurrentRevisionView)


class ItemSpecificReversionView(ItemCurrentRevisionView):
    def get_latest_revision(self):
        version = int(self.kwargs.get('version', 1))
        revision = None

        try:
            revision = self.item.revision_set.filter(slug='v%d'%version).first()
        except:
            logger.info('Could not find attachment.Revision v%d for matter: %s' % (version, self.matter))

        return revision
