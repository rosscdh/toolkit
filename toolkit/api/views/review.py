# -*- coding: UTF-8 -*-
"""
Item review a revision endpoint
"""
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from rulez import registry as rulez_registry

from rest_framework import generics
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework import status as http_status

from toolkit.core.attachment.models import Revision
from ..serializers import RevisionSerializer

from toolkit.apps.review.models import ReviewDocument

from toolkit.apps.workspace.models import Workspace
from toolkit.apps.workspace.services import EnsureCustomerService

from ..serializers import SimpleUserSerializer

import logging
logger = logging.getLogger('django.request')


class BaseReviewerSignatoryMixin(generics.ListAPIView,
                                 generics.CreateAPIView):
    """
    Provides the object to access .signatories or .reviewers
    and their required functionality
    """
    model = Revision  # to allow us to use get_object generically
    serializer_class = SimpleUserSerializer  # as we are returning the revision and not the item
    lookup_field = 'slug'
    lookup_url_kwarg = 'item_slug'

    def initial(self, request, *args, **kwargs):
        self.matter = get_object_or_404(Workspace, slug=kwargs.get('matter_slug'))
        self.item = get_object_or_404(self.matter.item_set.all(), slug=kwargs.get('item_slug'))
        self.revision = self.item.latest_revision
        super(BaseReviewerSignatoryMixin, self).initial(request, *args, **kwargs)

    def process_event_purpose_object(self, user):
        """
        is this a review or a signature?
        """
        raise NotImplementedError

    def update(self, request, **kwargs):
        raise exceptions.MethodNotAllowed(method=self.request.method)


class ItemRevisionReviewersView(BaseReviewerSignatoryMixin):
    """
    /matters/:matter_slug/items/:item_slug/revision/reviewers/ (GET,POST)
        [lawyer,customer] to list, create reviewers
    """
    def get_queryset_provider(self):
        return self.revision.reviewers

    def get_queryset(self):
        return self.get_queryset_provider().all()

    def process_event_purpose_object(self, user):
        # perform ReviewDocument get or create
        review_doc, is_new = ReviewDocument.objects.get_or_create(document=self.revision)
        # add the user to the reviewers if not there alreadt
        review_doc.reviewers.add(user) if user not in review_doc.reviewers.all() else None

        logger.info("Added %s to the ReviewDocument %s is_new: %s for revision: %s" % (user, review_doc, is_new, self.revision))

    def create(self, request, **kwargs):
        """
        we already have the matter item and revision we just need to
        1. ensure the user exists
        2. is the user already a reviewer for this revision
        3. if not make them one
        """
        user = get_object_or_404(User, username=request.DATA.get('username'))
        note = request.DATA.get('note')

        # add to the join if not there already
        self.get_queryset_provider().add(user) if user not in self.get_queryset() else None

        # add the user to the purpose of this endpoint object review||signature
        self.process_event_purpose_object(user=user)

        # we have the user at this point
        serializer = self.get_serializer(user)
        headers = self.get_success_headers(serializer.data)

        return Response(serializer.data, status=http_status.HTTP_201_CREATED, headers=headers)

    def can_read(self, user):
        return user.profile.user_class in ['lawyer', 'customer']

    def can_edit(self, user):
        return user.profile.is_lawyer

    def can_delete(self, user):
        return user.profile.is_lawyer


rulez_registry.register("can_read", ItemRevisionReviewersView)
rulez_registry.register("can_edit", ItemRevisionReviewersView)
rulez_registry.register("can_delete", ItemRevisionReviewersView)


# singular looking at a specific
class ItemRevisionReviewerView(BaseReviewerSignatoryMixin):
    """
    Singular
    /matters/:matter_slug/items/:item_slug/revision/reviewer/:username (GET,DELETE)
        [lawyer,customer] to view, delete reviewers
    """
    # def delete(self, request, **kwargs):
    #     """
    #     as we are dealign with a set here we can actually delete the object,
    #     we are trying to delete just the join
    #     """
    #     user = self.get_object()
    #     # we have the user at this point
    #     serializer = self.get_serializer(user)
    #     headers = None

    #     try:

    #         #
    #         # Only delete the join if it exists
    #         #
    #         self.get_revision_object_set_queryset().remove(user)

    #         status = http_status.HTTP_204_NO_CONTENT
    #         headers = self.get_success_headers(serializer.data)

    #     except Exception as e:
    #         logger.critical('delete failed: %s' % e)
    #         status = http_status.HTTP_400_BAD_REQUEST

    #     return Response(serializer.data, status=status, headers=headers)

    def can_read(self, user):
        return user.profile.user_class in ['lawyer', 'customer']

    def can_edit(self, user):
        return user.profile.is_lawyer

    def can_delete(self, user):
        return user.profile.is_lawyer


rulez_registry.register("can_read", ItemRevisionReviewerView)
rulez_registry.register("can_edit", ItemRevisionReviewerView)
rulez_registry.register("can_delete", ItemRevisionReviewerView)