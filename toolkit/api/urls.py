# -*- coding: UTF-8 -*-
from django.conf.urls import patterns, url

from rest_framework import routers

from .views import UserEndpoint
from .views import AccountEndpoint
from .views import ClientEndpoint
from .views import (MatterEndpoint,
                    MatterCategoryView,
                    MatterClosingGroupView,)

from .views import (MatterItemsView,
                    MatterItemView,
                    MatterItemCurrentRevisionView,
                    ItemRevisionReviewerView,
                    ItemRevisionSignatoryView,
                    RemindReviewers,
                    RemindSignatories)

from .views import ItemEndpoint
from .views import RevisionEndpoint
#from .views import WorkflowEndpoint

router = routers.SimpleRouter()

"""
ViewSets
"""
router.register(r'users', UserEndpoint)
router.register(r'account', AccountEndpoint, base_name='account')

router.register(r'matters', MatterEndpoint)
router.register(r'clients', ClientEndpoint)
router.register(r'items', ItemEndpoint)
router.register(r'revisions', RevisionEndpoint)


"""
Generics
"""
urlpatterns = patterns('',
    #
    # Matter Specific
    #
    url(r'^matters/(?P<matter_slug>[\w-]+)/category/(?P<category>[\w-]+)/$', MatterCategoryView.as_view(), name='matter_category'),
    url(r'^matters/(?P<matter_slug>[\w-]+)/closing_group/(?P<closing_group>[\w-]+)/$', MatterClosingGroupView.as_view(), name='matter_closing_group'),

    #
    # Matter Items
    #
    url(r'^matters/(?P<matter_slug>[\w-]+)/items/$', MatterItemsView.as_view(), name='matter_items'),
    url(r'^matters/(?P<matter_slug>[\w-]+)/items/(?P<item_slug>[\d\w-]+)/$', MatterItemView.as_view(), name='matter_item'),
    url(r'^matters/(?P<matter_slug>[\w-]+)/items/(?P<item_slug>[\d\w-]+)/revision/$', MatterItemCurrentRevisionView.as_view(), name='matter_item_revision'),
    url(r'^matters/(?P<matter_slug>[\w-]+)/items/(?P<item_slug>[\d\w-]+)/revision/reviewer/(?P<username>\w+)/$', ItemRevisionReviewerView.as_view(), name='item_revision_reviewer'),
    url(r'^matters/(?P<matter_slug>[\w-]+)/items/(?P<item_slug>[\d\w-]+)/revision/signatory/(?P<username>\w+)/$', ItemRevisionSignatoryView.as_view(), name='item_revision_signatory'),
    url(r'^matters/(?P<matter_slug>[\w-]+)/items/(?P<item_slug>[\d\w-]+)/revision/reviewers/remind/$', RemindReviewers.as_view(), name='item_revision_remind_reviewers'),
    url(r'^matters/(?P<matter_slug>[\w-]+)/items/(?P<item_slug>[\d\w-]+)/revision/signatories/remind/$', RemindSignatories.as_view(), name='item_revision_remind_signatories'),
)