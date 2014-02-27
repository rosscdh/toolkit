# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
#from django.views.decorators.cache import cache_page
from django.contrib.auth.decorators import login_required

from ..views import (ToolObjectListView,
                    CreateToolObjectView,
                    UpdateViewToolObjectView,
                    DeleteToolObjectView,
                    InviteClientToolObjectView,
                    ToolObjectPostFormPreviewView,
                    ToolObjectPreviewView,
                    ToolObjectDisplayView,
                    ToolObjectDownloadView)


urlpatterns = patterns('',

    url(r'^(?P<workspace>[\w-]+)/tool/(?P<tool>[\w-]+)/$',
        login_required(ToolObjectListView.as_view()),
        name='tool_object_list'),

    url(r'^(?P<workspace>[\w-]+)/tool/(?P<tool>[\w-]+)/create/$',
        login_required(CreateToolObjectView.as_view()),
        name='tool_object_new'),

    url(r'^(?P<workspace>[\w-]+)/tool/(?P<tool>[\w-]+)/(?P<slug>[\w-]+)/overview/$',
        login_required(ToolObjectPreviewView.as_view()),
        name='tool_object_overview'),

    url(r'^(?P<workspace>[\w-]+)/tool/(?P<tool>[\w-]+)/(?P<slug>[\w-]+)/edit/$',
        login_required(UpdateViewToolObjectView.as_view()),
        name='tool_object_edit'),

    url(r'^(?P<workspace>[\w-]+)/tool/(?P<tool>[\w-]+)/(?P<slug>[\w-]+)/delete/$',
        login_required(DeleteToolObjectView.as_view()),
        name='tool_object_delete'),

    url(r'^(?P<workspace>[\w-]+)/tool/(?P<tool>[\w-]+)/(?P<slug>[\w-]+)/invite/client/$',
        login_required(InviteClientToolObjectView.as_view()),
        name='tool_object_invite'),

    url(r'^(?P<workspace>[\w-]+)/tool/(?P<tool>[\w-]+)/(?P<slug>[\w-]+)/preview/$',
        login_required(ToolObjectPostFormPreviewView.as_view()),
        name='tool_object_after_save_preview'),

    url(r'^(?P<workspace>[\w-]+)/tool/(?P<tool>[\w-]+)/(?P<slug>[\w-]+)/display/$',
        login_required(ToolObjectDisplayView.as_view()),
        name='tool_object_display'),

    url(r'^(?P<workspace>[\w-]+)/tool/(?P<tool>[\w-]+)/(?P<slug>[\w-]+)/download/$',
        login_required(ToolObjectDownloadView.as_view()),
        name='tool_object_download'),
)
