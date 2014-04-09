# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from .views import MatterCreateView, MatterDeleteView, MatterDetailView, MatterListView, MatterUpdateView


urlpatterns = patterns('',
    url(r'^$', login_required(MatterListView.as_view()), name='list'),
    url(r'^create/$', login_required(MatterCreateView.as_view()), name='create'),
    url(r'^(?P<matter_slug>[\w\d-]+)/requests/$', login_required(MatterDetailView.as_view()), name='requests'),
    url(r'^(?P<matter_slug>[\w\d-]+)/delete/$', login_required(MatterDeleteView.as_view()), name='delete'),
    url(r'^(?P<matter_slug>[\w\d-]+)/edit/$', login_required(MatterUpdateView.as_view()), name='edit'),
    url(r'^(?P<matter_slug>[\w\d-]+)/$', login_required(MatterDetailView.as_view()), name='detail'),
)
