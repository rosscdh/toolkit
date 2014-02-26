# -*- coding: UTF-8 -*-
from django.http import Http404
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from rest_framework import viewsets
from rest_framework import generics
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework import status as http_status

from toolkit.apps.workspace.models import Workspace
from toolkit.core.item.models import Item
from toolkit.core.item.mailers import ReviewerReminderEmail, SignatoryReminderEmail

from ..serializers import MatterSerializer
from ..serializers.matter import LiteMatterSerializer
from ..serializers import ItemSerializer
from ..serializers import RevisionSerializer
from ..serializers import UserSerializer

import logging
logger = logging.getLogger('django.request')


class MatterEndpoint(viewsets.ModelViewSet):
    """
    Primary Matter ViewSet
    """
    model = Workspace
    serializer_class = MatterSerializer
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action == 'list':
            # @BUSINESSRULE show the light matter serializer
            # if we are looking at the list
            return LiteMatterSerializer
        return self.serializer_class

    def get_queryset(self):
        user = self.request.user
        return user.workspace_set.mine(user=user)


"""
Matter resolver Mixins
"""


class MatterMixin(generics.GenericAPIView):
    """
    Get the matter from the url slug :matter_slug
    """
    def initialize_request(self, request, *args, **kwargs):
        # provide the matter object
        self.matter = get_object_or_404(Workspace, slug=kwargs.get('matter_slug'))
        return super(MatterMixin, self).initialize_request(request, *args, **kwargs)


class MatterItemsQuerySetMixin(MatterMixin):
    """
    Mixin to filter the Items objects by their matter via the url :matter_slug
    """
    def get_queryset(self):
        return Item.objects.filter(matter=self.matter)


"""
Custom Api Endpoints
"""

class SpecificAttributeMixin(object):
    """
    mixin to allow use of specific attribute mixin
    """
    specific_attribute = None

    def __init__(self, *args, **kwargs):
        if self.specific_attribute is None:
            raise Exception('You must define a self.specific_attribute attrib that exists on the object')

        super(SpecificAttributeMixin, self).__init__(*args, **kwargs)

    def get_object(self):
        self.object = super(SpecificAttributeMixin, self).get_object()
        return getattr(self.object, self.specific_attribute, None)


"""
Matter item endpoints
"""

class MatterItemsView(MatterItemsQuerySetMixin,
                      generics.ListCreateAPIView):
    """
    /matters/:matter_slug/items/ (GET,POST)
        Allow the [lawyer,customer] user to list and create items in a matter
    """
    model = Item
    serializer_class = ItemSerializer

    def pre_save(self, obj):
        obj.matter = self.matter  # set in MatterItemsQuerySetMixin
        return super(MatterItemsView, self).pre_save(obj=obj)


class MatterItemView(generics.UpdateAPIView,
                     generics.DestroyAPIView,
                     generics.RetrieveAPIView,
                     MatterItemsQuerySetMixin):
    """
    /matters/:matter_slug/items/:item_slug/ (GET,PATCH,DELETE)
        Allow the [lawyer,customer] user to list, and update an existing item
        objects; that belong to them
    """
    model = Item
    serializer_class = ItemSerializer
    lookup_field = 'slug'
    lookup_url_kwarg = 'item_slug'


class ItemCurrentRevisionView(generics.CreateAPIView,
                              generics.UpdateAPIView,
                              generics.DestroyAPIView,
                              generics.RetrieveAPIView,
                              MatterItemsQuerySetMixin):
    """
    /matters/:matter_slug/items/:item_slug/revision (GET,POST,PATCH,DELETE)
        [lawyer,customer] to get,create,update,delete the latst revision
    Get the Item object and access its item.latest_revision to get access to
    the latest revision, but then return the serialized revision in the response
    """
    model = Item  # to allow us to use get_object generically
    serializer_class = RevisionSerializer  # as we are returning the revision and not the item
    lookup_field = 'slug'
    lookup_url_kwarg = 'item_slug'

    def get_revision(self):
        return self.item.latest_revision

    def get_object(self):
        """
        Ensure we get self.item
        but return the Revision object as self.object
        """
        self.item = super(ItemCurrentRevisionView, self).get_object()
        self.revision = self.get_revision()

        if self.revision is not None:
            return self.revision
        else:
            raise Http404


class ItemSpecificReversionView(ItemCurrentRevisionView):
    def get_revision(self):
        version = int(self.kwargs.get('version', 1))

        try:
            revision = [v for c, v in enumerate(self.item.revision_set.all()) if int(c + 1) == version][0]
        except:
            revision = None

        return revision



class BaseReviewerSignatoryMixin(ItemCurrentRevisionView):
    """
    Provides the object to access .signatories or .reviewers 
    and their required functionality
    """
    serializer_class = UserSerializer  # as we are returning the revision and not the item

    def get_revision_object_set_queryset(self):
        raise NotImplemented

    def get_object(self):
        username = self.kwargs.get('username')
        self.revision = super(BaseReviewerSignatoryMixin, self).get_object()
        #
        # Return the User object contained in the signatory/reviewer join table
        #
        return get_object_or_404(self.get_revision_object_set_queryset(), username=username)

    def update(self, request, **kwargs):
        raise exceptions.MethodNotAllowed(method=self.request.method)

    def create(self, request, **kwargs):
        """
        as we are dealign with a set here we can actually create the object,
        we are trying to create just the join
        """
        try:
            user = self.get_object()
            status = http_status.HTTP_304_NOT_MODIFIED
        except:
            #
            # Only create the join if it doesnt already exist
            #
            username = self.kwargs.get('username')
            user = get_object_or_404(User, username=username)
            # add to the join
            self.get_revision_object_set_queryset().add(user)

            status = http_status.HTTP_201_CREATED

        # we have the user at this point
        serializer = self.get_serializer(user)
        headers = self.get_success_headers(serializer.data)

        return Response(serializer.data, status=status, headers=headers)

    def delete(self, request, **kwargs):
        """
        as we are dealign with a set here we can actually delete the object,
        we are trying to delete just the join
        """
        user = self.get_object()
        # we have the user at this point
        serializer = self.get_serializer(user)
        headers = None

        try:
            #
            # Only delete the join if it exists
            #
            self.get_revision_object_set_queryset().remove(user)

            status = http_status.HTTP_204_NO_CONTENT
            headers = self.get_success_headers(serializer.data)
        except Exception as e:
            logger.critical('delete failed: %s' % e)
            status = http_status.HTTP_400_BAD_REQUEST

        return Response(serializer.data, status=status, headers=headers)


class ItemRevisionReviewerView(BaseReviewerSignatoryMixin):
    """
    /matters/:matter_slug/items/:item_slug/revision/reviewer/:username (GET,POST,DELETE)
        [lawyer,customer] to view, create and delete reviewers
    Get the specified reviewer for info purposes
    """

    def get_revision_object_set_queryset(self):
        return self.revision.reviewers


class ItemRevisionSignatoryView(BaseReviewerSignatoryMixin):
    """
    /matters/:matter_slug/items/:item_slug/revision/signatory/:username (DELETE)
        [lawyer,customer] to delete signatories
    Get the specified signatory for info purposes
    Is the same functionality as the ItemRevisionReviewerView
    """
    def get_revision_object_set_queryset(self):
        return self.revision.signatories


"""
Reminder emails
"""

class BaseReminderMixin(ItemCurrentRevisionView):
    """
    Mixin to ensure that inherited mthods are not implemented at this level
    necessary as we require the ItemCurrentRevisionView.get_object to provide us
    with the matter object
    """
    serializer_class = UserSerializer  # return a set of users that were reminded
    mailer = None

    def post(self, request, **kwargs):
        self.get_object()

        sent_to = {
            'detail': 'Sent %s to these users' % self.mailer.name,
            'results': []
        }

        for u in self.get_revision_object_set_queryset().all():
            try:
                m = self.mailer(recipients=((u.get_full_name(), u.email,)))
                m.process(subject=self.subject,
                          item=self.item,
                          from_name=self.request.user.get_full_name(),
                          action_url='http://lawpal.com/etc/')

                sent_to['results'].append(UserSerializer(u).data)

            except Exception as e:
                logger.critical('Could not send "%s" reminder email: %s' % (self.mailer, e))
        return Response(sent_to, status=http_status.HTTP_202_ACCEPTED)

    def update(self, **kwargs): raise exceptions.MethodNotAllowed(method=self.request.method)
    def delete(self, **kwargs): raise exceptions.MethodNotAllowed(method=self.request.method)
    def retrieve(self, **kwargs): raise exceptions.MethodNotAllowed(method=self.request.method)


class RemindReviewers(BaseReminderMixin):
    """
    Send reminder emails to reviewers
    """
    mailer = ReviewerReminderEmail
    subject = '[ACTION REQUIRED] Reminder to review'

    def get_revision_object_set_queryset(self):
        return self.revision.reviewers


class RemindSignatories(BaseReminderMixin):
    """
    Send reminder emails to signatories
    """
    mailer = SignatoryReminderEmail
    subject = '[ACTION REQUIRED] Reminder to sign'

    def get_revision_object_set_queryset(self):
        return self.revision.signatories



"""
Category and Closing Groups
"""

class CategoryView(SpecificAttributeMixin,
                   generics.DestroyAPIView,
                   generics.CreateAPIView,
                   generics.RetrieveAPIView,
                   MatterMixin,):
    """
    /matters/:matter_slug/category/:category (GET,POST,DELETE)
        [lawyer] can assign an item to a category
    
    view/create/delete a specific closing_group
    """
    model = Workspace
    serializer_class = MatterSerializer
    lookup_field = 'slug'
    lookup_url_kwarg = 'matter_slug'

    specific_attribute = 'categories'

    def retrieve(self, request, **kwargs):
        obj = self.get_object()
        return Response(obj)

    def create(self, request, **kwargs):
        self.get_object()

        cats = self.object.add_category(self.kwargs.get('category'))
        self.object.save(update_fields=['data'])

        return Response(cats)

    def delete(self, request, **kwargs):
        cats = self.get_object()
        category = self.kwargs.get('category')

        try:
            cats = self.object.remove_category(category, instance=self.object)
            self.object.save(update_fields=['data'])
        except Exception as e:
            logger.info('Could not delete category: %s due to: %s' % (category, e,))

        return Response(cats)


class ClosingGroupView(SpecificAttributeMixin,
                       generics.DestroyAPIView,
                       generics.CreateAPIView,
                       generics.RetrieveAPIView,
                       MatterMixin,):
    """
    /matters/:matter_slug/closing_group/:group (GET,POST,DELETE)
        [lawyer] can assign an item to a closing group

    view/create/delete a specific closing_group
    """
    model = Workspace
    serializer_class = MatterSerializer
    lookup_field = 'slug'
    lookup_url_kwarg = 'matter_slug'

    specific_attribute = 'closing_groups'

    def retrieve(self, request, **kwargs):
        obj = self.get_object()
        return Response(obj)

    def create(self, request, **kwargs):
        self.get_object()
        closing_group = self.kwargs.get('closing_group')

        closing_groups = self.object.add_closing_group(closing_group)
        self.object.save(update_fields=['data'])

        return Response(closing_groups)

    def delete(self, request, **kwargs):
        closing_groups = self.get_object()
        closing_group = self.kwargs.get('closing_group')

        try:
            closing_groups = self.object.remove_closing_group(closing_group, instance=self.object)
            self.object.save(update_fields=['data'])
        except Exception as e:
            logger.info('Could not delete closing_group: %s due to: %s' % (closing_group, e,))

        return Response(closing_groups)