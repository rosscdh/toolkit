# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url, include

from .views import SignRevisionView, ClaimSignRevisionView


urlpatterns = patterns('',
    # Base
    url(r'^claim/(?P<slug>[\w-]+)/$', ClaimSignRevisionView.as_view(), name='claim_sign_document'),
    url(r'^signature/(?P<slug>[\w-]+)/(?P<username>.*)/$', SignRevisionView.as_view(), name='sign_document'),
    # HelloSign
    url(r'^', include('hello_sign.urls')),
)
