# -*- coding: UTF-8 -*-
from django.conf.urls import patterns, url

from rest_framework import routers

from .views import UserEndpoint
from .views import AccountEndpoint
from .views import ClientEndpoint
from .views import (MatterEndpoint, MatterItemsView, MatterItemView)
from .views import ItemEndpoint
from .views import RevisionEndpoint
#from .views import WorkflowEndpoint

router = routers.SimpleRouter()

"""
ViewSets
"""
router.register(r'users', UserEndpoint)
router.register(r'account', AccountEndpoint)

router.register(r'matters', MatterEndpoint)
router.register(r'clients', ClientEndpoint)
router.register(r'items', ItemEndpoint)
router.register(r'revisions', RevisionEndpoint)


"""
Generics
"""
urlpatterns = router.urls + patterns('',

    url(r'^matters/(?P<matter_slug>[\w-]+)/items/$', MatterItemsView.as_view(), name='matter_items'),
    url(r'^matters/(?P<matter_slug>[\w-]+)/items/(?P<item_slug>[\d\w-]+)/$', MatterItemView.as_view(), name='matter_item'),

)