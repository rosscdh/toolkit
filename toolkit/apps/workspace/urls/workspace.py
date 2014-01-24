# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from django.views.generic import DetailView, UpdateView
from django.contrib.auth.decorators import login_required

from ..views import (CreateWorkspaceView,
                    WorkspaceToolsView,
                    AddUserToWorkspace)

from ..models import Workspace
from ..forms import WorkspaceForm


urlpatterns = patterns('',

    url(r'^create/$',
        login_required(CreateWorkspaceView.as_view()), name='create'),

    url(r'^(?P<slug>[\w-]+)/edit/$',
        login_required(UpdateView.as_view(model=Workspace,
                                          form_class=WorkspaceForm)),
        name='edit'),

    url(r'^(?P<slug>[\w-]+)/$',
        login_required(DetailView.as_view(model=Workspace)),
        name='view'),

    url(r'^(?P<slug>[\w-]+)/team_member/add/$',
        login_required(AddUserToWorkspace.as_view()),
        name='add_team_member'),

    url(r'^(?P<workspace>[\w-]+)/tools/$',
        login_required(WorkspaceToolsView.as_view()),
        name='tools_list'),
)
