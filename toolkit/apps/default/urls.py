# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required

from .views import HomePageView, InviteKeySignInView, LogoutView, SignUpView, StartView


urlpatterns = patterns('',
    url(r'^start/$', StartView.as_view(), name='signin'),
    url(r'^start/signup/$', SignUpView.as_view(), name='signup'),
    url(r'^start/invite/(?P<key>.+)/$', InviteKeySignInView.as_view(), name='invite'),
    url(r'^start/invite/$', InviteKeySignInView.as_view(), name='invite_form'),
    url(r'^end/$', LogoutView.as_view(), name='logout'),
    url(r'^legal/terms/$', TemplateView.as_view(template_name='terms.html'), name='terms'),
    url(r'^$', HomePageView.as_view(), name='home'),
)
