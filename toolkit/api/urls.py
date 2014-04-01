# -*- coding: UTF-8 -*-
from django.conf.urls import patterns, url

from rest_framework import routers

from .views import UserEndpoint
from .views import AccountEndpoint
from .views import ClientEndpoint

from .views import (MatterEndpoint,
                    MatterCategoryView,
                    MatterClosingGroupView,
                    MatterRevisionLabelView,
                    MatterSortView,
                    MatterParticipant,)

from .views import (ActivityEndpoint,
                    MatterActivityEndpoint,
                    ItemActivityEndpoint)

from .views import (MatterItemsView,
                    MatterItemView,

                    MatterItemRequestRevisionView,
                    RemindRequestedRevisionInvitee,

                    MatterItemCurrentRevisionView,
                    MatterItemSpecificReversionView,)

from .views import (ItemRevisionReviewersView,
                    ItemRevisionReviewerView,
                    RemindReviewers,

                    ItemRevisionSignatoriesView,
                    ItemRevisionSignatoryView,
                    RemindSignatories)

from .views import ItemEndpoint
from .views import RevisionEndpoint
from .views import ItemCommentEndpoint
from .views import ReviewEndpoint
#from .views import WorkflowEndpoint

router = routers.SimpleRouter(trailing_slash=False)

"""
ViewSets
"""
router.register(r'users', UserEndpoint)

router.register(r'matters', MatterEndpoint)
router.register(r'activity', ActivityEndpoint)
router.register(r'clients', ClientEndpoint)
router.register(r'items', ItemEndpoint)
router.register(r'revisions', RevisionEndpoint)
router.register(r'reviews', ReviewEndpoint)

"""
Generics
"""


urlpatterns = router.urls + patterns('',
    #
    # Account
    #
    url(r'^account/?$', AccountEndpoint.as_view(), name='account'),
    #
    # Matter Specific
    #
    url(r'^matters/(?P<matter_slug>[\w-]+)/category/(?P<category>[\w\W\s]*)/?$', MatterCategoryView.as_view(), name='matter_category'),
    url(r'^matters/(?P<matter_slug>[\w-]+)/closing_group/(?P<closing_group>[\w-]+)/?$', MatterClosingGroupView.as_view(), name='matter_closing_group'),
    url(r'^matters/(?P<matter_slug>[\w-]+)/revision_label/?$', MatterRevisionLabelView.as_view(), name='matter_revision_label'),

    url(r'^matters/(?P<matter_slug>[\w-]+)/sort/?$', MatterSortView.as_view(), name='matter_sort'),
    url(r'^matters/(?P<matter_slug>[\w-]+)/participant(/(?P<email>.+))?/?$', MatterParticipant.as_view(), name='matter_participant'),

    url(r'^matters/(?P<matter_slug>[\w-]+)/activity/?$', MatterActivityEndpoint.as_view(), name='matter_activity'),

    #
    # Matter Items
    #
    url(r'^matters/(?P<matter_slug>[\w-]+)/items/?$', MatterItemsView.as_view(), name='matter_items'),
    url(r'^matters/(?P<matter_slug>[\w-]+)/items/(?P<item_slug>[\d\w-]+)/request_document/remind/?$', RemindRequestedRevisionInvitee.as_view(), name='revision_request_document_reminder'),
    url(r'^matters/(?P<matter_slug>[\w-]+)/items/(?P<item_slug>[\d\w-]+)/request_document/?$', MatterItemRequestRevisionView.as_view(), name='matter_item_request_doc'),
    url(r'^matters/(?P<matter_slug>[\w-]+)/items/(?P<item_slug>[\d\w-]+)/activity/?$', ItemActivityEndpoint.as_view(), name='item_activity'),
    url(r'^matters/(?P<matter_slug>[\w-]+)/items/(?P<item_slug>[\d\w-]+)/comment/(?P<id>\d+)/?$', ItemCommentEndpoint.as_view(), name='item_comment'),
    url(r'^matters/(?P<matter_slug>[\w-]+)/items/(?P<item_slug>[\d\w-]+)/comment/?$', ItemCommentEndpoint.as_view(), name='item_comment'),
    url(r'^matters/(?P<matter_slug>[\w-]+)/items/(?P<item_slug>[\d\w-]+)/?$', MatterItemView.as_view(), name='matter_item'),
    #
    # Revisions
    #
    url(r'^matters/(?P<matter_slug>[\w-]+)/items/(?P<item_slug>[\d\w-]+)/revision/?$', MatterItemCurrentRevisionView.as_view(), name='matter_item_revision'),
    url(r'^matters/(?P<matter_slug>[\w-]+)/items/(?P<item_slug>[\d\w-]+)/revision/v(?P<version>[\d]+)/?$', MatterItemSpecificReversionView.as_view(), name='matter_item_specific_revision'),
    #
    # Revision reviewers and signatories
    #
    url(r'^matters/(?P<matter_slug>[\w-]+)/items/(?P<item_slug>[\d\w-]+)/revision/reviewers/?$', ItemRevisionReviewersView.as_view(), name='item_revision_reviewers'),
    url(r'^matters/(?P<matter_slug>[\w-]+)/items/(?P<item_slug>[\d\w-]+)/revision/reviewer/(?P<username>[\w\W\-\_]+)/?$', ItemRevisionReviewerView.as_view(), name='item_revision_reviewer'),
    url(r'^matters/(?P<matter_slug>[\w-]+)/items/(?P<item_slug>[\d\w-]+)/revision/reviewers/remind/?$', RemindReviewers.as_view(), name='item_revision_remind_reviewers'),

    url(r'^matters/(?P<matter_slug>[\w-]+)/items/(?P<item_slug>[\d\w-]+)/revision/signatories/?$', ItemRevisionSignatoriesView.as_view(), name='item_revision_signatories'),
    url(r'^matters/(?P<matter_slug>[\w-]+)/items/(?P<item_slug>[\d\w-]+)/revision/signatory/(?P<username>[\w\W\-\_]+)/?$', ItemRevisionSignatoryView.as_view(), name='item_revision_signatory'),
    url(r'^matters/(?P<matter_slug>[\w-]+)/items/(?P<item_slug>[\d\w-]+)/revision/signatories/remind/?$', RemindSignatories.as_view(), name='item_revision_remind_signatories'),
)