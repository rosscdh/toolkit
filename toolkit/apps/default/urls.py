# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required

from .views import StartView, SignUpView, LogoutView


urlpatterns = patterns('',
    url(r'^start/$', StartView.as_view(), name='signin'),
    url(r'^start/signup/$', SignUpView.as_view(), name='signup'),
    url(r'^end/$', LogoutView.as_view(), name='logout'),
    url(r'^$', TemplateView.as_view(template_name='public/home.html')),
)

