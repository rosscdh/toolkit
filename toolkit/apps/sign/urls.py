# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

from .views import SignRevisionView


urlpatterns = patterns('',
    url(r'^(?P<slug>[\w-]+)/(?P<auth_slug>[\w\W]+)/$', SignRevisionView.as_view(), name='sign_document'),
)
