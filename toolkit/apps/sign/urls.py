# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url, include

from .views import SignRevisionView, ClaimSignRevisionView


urlpatterns = patterns('',
    # Base
    #url(r'^(?P<slug>[\w-]+)/(?P<auth_slug>[\w\W]+)/$', SignRevisionView.as_view(), name='sign_document'),
    url(r'^(?P<slug>[\w-]+)/$', SignRevisionView.as_view(), name='sign_document'),
    url(r'^claim/(?P<slug>[\w-]+)/$', ClaimSignRevisionView.as_view(), name='claim_sign_document'),
)
