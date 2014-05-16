# -*- coding: UTF-8 -*-
"""
Item review a revision endpoint
"""
from django.http import Http404
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from rulez import registry as rulez_registry

from rest_framework import viewsets
from rest_framework import generics
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework import status as http_status

from toolkit.core.attachment.models import Revision

from toolkit.apps.review.models import ReviewDocument

from toolkit.apps.workspace.models import Workspace
from toolkit.apps.workspace.services import EnsureCustomerService

from ..serializers import SimpleUserWithReviewUrlSerializer
from ..serializers import ReviewSerializer

import logging
logger = logging.getLogger('django.request')


class ReviewEndpoint(viewsets.ModelViewSet):
    """
    Primary Matter ViewSet
    """
    model = ReviewDocument
    serializer_class = ReviewSerializer
    lookup_field = 'pk'

    def can_read(self, user):
        return user.profile.user_class in ['lawyer', ]

    def can_edit(self, user):
        return user.profile.is_lawyer

    def can_delete(self, user):
        return user.profile.is_lawyer


rulez_registry.register("can_read", ReviewEndpoint)
rulez_registry.register("can_edit", ReviewEndpoint)
rulez_registry.register("can_delete", ReviewEndpoint)


class BaseReviewerSignatoryMixin(generics.GenericAPIView):
    """
    Provides the object to access .signers or .reviewers
    and their required functionality
    """
    model = Revision  # to allow us to use get_object generically
    serializer_class = ReviewSerializer  # as we are returning the revision and not the item
    lookup_field = 'slug'
    lookup_url_kwarg = 'item_slug'

    def get_objects(self, **kwargs):
        self.matter = get_object_or_404(Workspace, slug=kwargs.get('matter_slug'))
        self.item = get_object_or_404(self.matter.item_set.all(), slug=kwargs.get('item_slug'))
        self.revision = self.item.latest_revision

    def initial(self, request, *args, **kwargs):
        self.get_objects(**kwargs)
        super(BaseReviewerSignatoryMixin, self).initial(request, *args, **kwargs)

    def get_queryset_provider(self):
        raise NotImplementedError

    def get_queryset(self):
        return self.get_queryset_provider().all()

    def process_event_purpose_object(self, user):
        """
        is this a review or a signature?
        """
        raise NotImplementedError

    def update(self, request, **kwargs):
        raise exceptions.MethodNotAllowed(method=self.request.method)


class ItemRevisionReviewersView(generics.ListAPIView,
                                generics.CreateAPIView,
                                BaseReviewerSignatoryMixin):
    """
    /matters/:matter_slug/items/:item_slug/revision/reviewers/ (GET,POST)
        [lawyer,customer] to list, create reviewers
    """
    def get_queryset_provider(self):
        return self.revision.reviewdocument_set

    def create(self, request, **kwargs):
        """
        we already have the matter item and revision we just need to
        1. ensure the user exists
        2. is the user already a reviewer for this revision
        3. if not make them one
        """
        username = request.DATA.get('username')
        first_name = request.DATA.get('first_name')
        last_name = request.DATA.get('last_name')
        email = request.DATA.get('email')
        note = request.DATA.get('note')

        if username is None and email is None:
            raise exceptions.APIException('You must provide a username or email')

        try:
            if username is not None:
                user = User.objects.get(username=username)

            elif email is not None:
                user = User.objects.get(email=email)

        except User.DoesNotExist:

            if email is None:
                raise Http404

            else:
                # we have a new user here
                user_service = EnsureCustomerService(email=email, full_name='%s %s' % (first_name, last_name))
                is_new, user, profile = user_service.process()

        if user not in self.get_queryset():
            # add to the join if not there already
            # add the user to the purpose of this endpoint object review||signature
            self.revision.reviewers.add(user)

            #
            # Send invite to review Email
            #
            self.item.send_invite_to_review_emails(from_user=request.user, to=[user], note=note)

            #
            # add activity
            #
            self.matter.actions.invite_user_as_reviewer(item=self.item,
                                                        inviting_user=request.user,
                                                        invited_user=user)

        review_document = self.revision.reviewdocument_set.filter(reviewers__in=[user]).first()

        # we have the user at this point
        serializer = self.get_serializer(review_document)

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
class ItemRevisionReviewerView(generics.RetrieveAPIView,
                               generics.DestroyAPIView,
                               BaseReviewerSignatoryMixin):
    """
    Singular
    /matters/:matter_slug/items/:item_slug/revision/reviewer/:username (GET,DELETE)
        [lawyer,customer] to view, delete reviewers
    """
    model = User  # to allow us to use get_object generically
    serializer_class = SimpleUserWithReviewUrlSerializer  # as we are returning the revision and not the item
    lookup_field = 'username'
    lookup_url_kwarg = 'username'

    def get_queryset_provider(self):
        return self.revision.reviewers

    def get_object(self):
        return get_object_or_404(User, username=self.kwargs.get('username'))

    def retrieve(self, request, **kwargs):
        status = http_status.HTTP_200_OK

        user = self.get_object()
        serializer = self.get_serializer(user)
        data = serializer.data

        #
        # Find ReviewDocumets where this user is the reviewer
        # Should only ever be one per user
        #
        user_reviewdocument_set = self.revision.reviewdocument_set.filter(reviewers__in=[user])

        if len(user_reviewdocument_set) == 0:
            #
            # must not be 0 as we have the users username thus they should be
            # part of the reviewers at this stage
            #
            logger.critical('A revision %s for a user %s has more than 0 reviewdocument they should have 1 per revision' % (self.revision, user))
            raise Http404

        if len(user_reviewdocument_set) > 1:
            #
            # Should never have more than 1
            #
            status = http_status.HTTP_406_NOT_ACCEPTABLE
            logger.critical('A revision %s for a user %s has more than 1 reviewdocument they should only have 1 per revision' % (self.revision, user))

        # create event
        #
        # @TODO discuss with @alex do we need to know when a lawyer/participant views the revision?
        #
        # self.revision.item.matter.actions.user_viewed_revision(item=self.revision.item,
        #                                                        user=user,
        #                                                        revision=self.revision)
        

        # TODO: check if this was the last user to review the document.
        # if so: user_revision_review_complete()
        status = http_status.HTTP_200_OK

        return Response(data, status=status)

    def delete(self, request, **kwargs):
        status = http_status.HTTP_200_OK

        user = self.get_object()
        serializer = self.get_serializer(user)
        data = serializer.data

        if user in self.revision.reviewers.all():
            #
            # the user is in the reviewers set
            # remove them. This will (via the signals) remove them from the
            # reviewdocument object too
            #
            self.revision.reviewers.remove(user)

            self.matter.actions.cancel_user_upload_revision_request(item=self.item,
                                                                    removing_user=request.user,
                                                                    removed_user=user)
        else:
            status = http_status.HTTP_404_NOT_FOUND

        return Response(data, status=status)

    def can_read(self, user):
        return user.profile.user_class in ['lawyer', 'customer']

    def can_edit(self, user):
        return user.profile.is_lawyer

    def can_delete(self, user):
        return user.profile.is_lawyer


rulez_registry.register("can_read", ItemRevisionReviewerView)
rulez_registry.register("can_edit", ItemRevisionReviewerView)
rulez_registry.register("can_delete", ItemRevisionReviewerView)


class ReviewerHasViewedRevision(generics.UpdateAPIView,
                                BaseReviewerSignatoryMixin):
    """
    Called when the invited user views the revision
    via ajax event of closing the crocodoc modal window
    """
    http_method_names = ('patch',)

    model = ReviewDocument
    serializer_class = ReviewSerializer
    lookup_url_kwarg = 'reviewdocument_slug'
    lookup_field = 'slug'

    def get_objects(self, **kwargs):
        super(ReviewerHasViewedRevision, self).get_objects(**kwargs)
        self.reviewdocument = get_object_or_404(self.model, slug=kwargs.get('reviewdocument_slug'))

    def update(self, request, **kwargs):
        # 
        # Just issue the user viewed the object
        #
        self.reviewdocument.reviewer_has_viewed = True

        self.matter.actions.user_viewed_revision(item=self.item,
                                                 user=self.request.user,
                                                 revision=self.revision)
        return Response({'detail': 'Set user last viewed'}, status=http_status.HTTP_200_OK)

    def can_read(self, user):
        return user in self.reviewdocument.participants

    def can_edit(self, user):
        return user in self.reviewdocument.participants

    def can_delete(self, user):
        return False


rulez_registry.register("can_read", ReviewerHasViewedRevision)
rulez_registry.register("can_edit", ReviewerHasViewedRevision)
rulez_registry.register("can_delete", ReviewerHasViewedRevision)
