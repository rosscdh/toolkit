# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url, include

from .views import SignRevisionView


urlpatterns = patterns('',
    # Base
    #url(r'^(?P<slug>[\w-]+)/(?P<auth_slug>[\w\W]+)/$', SignRevisionView.as_view(), name='sign_document'),
    url(r'^(?P<slug>[\w-]+)/$', SignRevisionView.as_view(), name='sign_document'),
)
