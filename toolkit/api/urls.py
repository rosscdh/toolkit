# -*- coding: UTF-8 -*-
from django.conf.urls import patterns, url

from rest_framework import routers

from .views import AccountEndpoint
from .views import ClientEndpoint
#from .views import MatterEndpoint
#from .views import ItemEndpoint
#from .views import AttachmentEndpoint
#from .views import RevisionEndpoint
#from .views import WorkflowEndpoint

router = routers.SimpleRouter()
router.register(r'account', AccountEndpoint)

urlpatterns = router.urls + patterns('',
    #url(r'^account/', AccountEndpoint.as_view(), name='account'),
    url(r'^clients/', ClientEndpoint.as_view(), name='clients'),
#    url(r'^matters/', MatterEndpoint.as_view(), name='matters'),
#    url(r'^items/', ItemEndpoint.as_view(), name='items'),
#    url(r'^attachments/', AttachmentEndpoint.as_view(), name='attachments'),
#        url(r'^attachments/(?P<slug>(.*))/revisions/(?P<revision>(\d+))/', AttachmentEndpoint.as_view(), name='attachment_revision'),
#    url(r'^workflows/', WorkflowEndpoint.as_view(), name='workflows'),
)