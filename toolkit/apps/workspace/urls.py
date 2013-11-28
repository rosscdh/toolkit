# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from django.views.generic import DetailView, UpdateView
from django.contrib.auth.decorators import login_required

from .views import CreateWorkspaceView, WorkspaceToolObjectsListView, CreateWorkspaceToolObjectView
from .models import Workspace
from .forms import WorkspaceForm


urlpatterns = patterns('',
    url(r'^(?P<workspace>[\w-]+)/tool/(?P<tool>[\w-]+)/$',
        login_required(WorkspaceToolObjectsListView.as_view()),
        name='tool_object_list'),

    url(r'^(?P<workspace>[\w-]+)/tool/(?P<tool>[\w-]+)/create/$',
        login_required(CreateWorkspaceToolObjectView.as_view()),
        name='tool_object_new'),


    url(r'^create/$', login_required(CreateWorkspaceView.as_view()), name='create'),

    url(r'^(?P<slug>[\w-]+)/edit/$',
        login_required(UpdateView.as_view(model=Workspace, form_class=WorkspaceForm)),
        name='edit'),

    url(r'^(?P<slug>[\w-]+)/$',
        login_required(DetailView.as_view(model=Workspace)),
        name='view'),
)
