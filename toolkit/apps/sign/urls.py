# -*- coding: utf-8 -*-
from django.views.generic import TemplateView
from django.conf.urls import patterns, url, include

from .views import SignRevisionView, ClaimSignRevisionView


urlpatterns = patterns('',
    # Base
    url(r'^in_progress/$', TemplateView.as_view(template_name='sign/in_progress.html'), name='sign_in_progress'),

    url(r'^claim/(?P<slug>[\w-]+)/$', ClaimSignRevisionView.as_view(), name='claim_sign_document'),
    url(r'^signature/(?P<slug>[\w-]+)/(?P<username>.*)/$', SignRevisionView.as_view(), name='sign_document'),
    # HelloSign
    url(r'^hellosign/', include('hello_sign.urls')),
)
