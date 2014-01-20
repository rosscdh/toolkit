# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url, include
from rest_framework import routers

from toolkit.apps.eightythreeb.api import EightyThreeBViewSet, AttachmentDeleteView
from toolkit.apps.workspace.api import InviteKeyViewSet, WorkspaceToolsView

router = routers.DefaultRouter()
router.register(r'invite', InviteKeyViewSet)
router.register(r'83b', EightyThreeBViewSet)


urlpatterns = patterns('',
    url(r'^', include(router.urls)),
    url(r'^workspace/(?P<slug>[\w-]+)/tools/$', WorkspaceToolsView.as_view(), name='workspacetools'),
    url(r'^83b/attachments/(?P<pk>\d+)/$', AttachmentDeleteView.as_view(), name='attachment-delete'),
)
