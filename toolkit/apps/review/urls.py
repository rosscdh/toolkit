# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

from .views import ApproveRevisionView, ReviewRevisionView


urlpatterns = patterns('',
    url(r'^(?P<slug>[\w-]+)/(?P<auth_slug>[\w\W]+)/approve/$', ApproveRevisionView.as_view(), name='approve_document'),
    url(r'^(?P<slug>[\w-]+)/(?P<auth_slug>[\w\W]+)/$', ReviewRevisionView.as_view(), name='review_document'),
)
