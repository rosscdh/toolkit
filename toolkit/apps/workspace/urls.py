# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
#from django.views.decorators.cache import cache_page
from django.views.generic import DetailView, UpdateView
from django.contrib.auth.decorators import login_required

from .views import (CreateWorkspaceView,
                    AddUserToWorkspace,
                    WorkspaceToolObjectsListView,
                    CreateWorkspaceToolObjectView,
                    UpdateViewWorkspaceToolObjectView,
                    InviteClientWorkspaceToolObjectView,
                    WorkspaceToolObjectPreviewView,
                    WorkspaceToolObjectDisplayView,
                    WorkspaceToolObjectDownloadView)
from .models import Workspace
from .forms import WorkspaceForm


urlpatterns = patterns('',
    url(r'^(?P<workspace>[\w-]+)/tool/(?P<tool>[\w-]+)/$',
        login_required(WorkspaceToolObjectsListView.as_view()),
        name='tool_object_list'),
    url(r'^(?P<workspace>[\w-]+)/tool/(?P<tool>[\w-]+)/create/$',
        login_required(CreateWorkspaceToolObjectView.as_view()),
        name='tool_object_new'),
    url(r'^(?P<workspace>[\w-]+)/tool/(?P<tool>[\w-]+)/(?P<slug>[\w-]+)/edit/$',
        login_required(UpdateViewWorkspaceToolObjectView.as_view()),
        name='tool_object_edit'),
    url(r'^(?P<workspace>[\w-]+)/tool/(?P<tool>[\w-]+)/(?P<slug>[\w-]+)/invite/client/$',
        login_required(InviteClientWorkspaceToolObjectView.as_view()),
        name='tool_object_invite'),
    url(r'^(?P<workspace>[\w-]+)/tool/(?P<tool>[\w-]+)/(?P<slug>[\w-]+)/preview/$',
        login_required(WorkspaceToolObjectPreviewView.as_view()),
        name='tool_object_preview'),
    url(r'^(?P<workspace>[\w-]+)/tool/(?P<tool>[\w-]+)/(?P<slug>[\w-]+)/display/$',
        login_required(WorkspaceToolObjectDisplayView.as_view()),
        name='tool_object_display'),
    url(r'^(?P<workspace>[\w-]+)/tool/(?P<tool>[\w-]+)/(?P<slug>[\w-]+)/download/$',
        login_required(WorkspaceToolObjectDownloadView.as_view()),
        name='tool_object_download'),


    url(r'^create/$', login_required(CreateWorkspaceView.as_view()), name='create'),

    url(r'^(?P<slug>[\w-]+)/team_member/add/$',
        login_required(AddUserToWorkspace.as_view()),
        name='add_team_member'),

    url(r'^(?P<slug>[\w-]+)/edit/$',
        login_required(UpdateView.as_view(model=Workspace, form_class=WorkspaceForm)),
        name='edit'),

    url(r'^(?P<slug>[\w-]+)/$',
        login_required(DetailView.as_view(model=Workspace)),
        name='view'),
)
