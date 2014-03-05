# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

from .views import ReviewRevisionView


urlpatterns = patterns('',
    url(r'^(?P<slug>[\w-]+)/(?P<auth_slug>[\w\W]+)/$', ReviewRevisionView.as_view(), name='review_document'),
)
