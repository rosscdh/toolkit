# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

from .views import DownloadAttachment


urlpatterns = patterns('',
    url(r'^(?P<slug>[\w-]+)/download/$', DownloadAttachment.as_view(), name='download_attachment'),
)
