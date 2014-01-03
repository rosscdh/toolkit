# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from django.views.generic import DetailView
from django.contrib.auth.decorators import login_required

from .views import Preview83bView, TrackingCodeView, UploadFileView, AttachmentView
from .models import EightyThreeB


urlpatterns = patterns('',
    url(r'^(?P<slug>[\w-]+)/preview/$', login_required(Preview83bView.as_view()), name='preview'),

    url(r'^(?P<slug>[\w-]+)/tracking_code/$', login_required(TrackingCodeView.as_view()), name='tracking_code'),

    url(r'^(?P<slug>[\w-]+)/attachment/$', login_required(AttachmentView.as_view()), name='attachment'),
    url(r'^(?P<slug>[\w-]+)/attachment/upload/$', login_required(UploadFileView.as_view()), name='upload_file'),

    url(r'^(?P<slug>[\w-]+)/$', login_required(DetailView.as_view(model=EightyThreeB)), name='view'),
)
