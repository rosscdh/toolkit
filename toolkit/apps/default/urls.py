# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required

from .views import (DisclaimerView,
                    HomePageView,
                    InviteKeySignInView,
                    LogoutView,
                    PrivacyView,
                    SignUpView,
                    StartView,
                    TermsView)


urlpatterns = patterns('',
    # Legal Pages
    url(r'^legal/disclaimer/$', DisclaimerView.as_view(), name='disclaimer'),
    url(r'^legal/privacy/$', PrivacyView.as_view(), name='privacy'),
    url(r'^legal/terms/$', TermsView.as_view(), name='terms'),

    url(r'^start/$', StartView.as_view(), name='signin'),
    url(r'^start/signup/$', SignUpView.as_view(), name='signup'),
    url(r'^start/invite/(?P<key>.+)/$', InviteKeySignInView.as_view(), name='invite'),
    url(r'^start/invite/$', InviteKeySignInView.as_view(), name='invite_form'),
    url(r'^end/$', LogoutView.as_view(), name='logout'),
    url(r'^$', HomePageView.as_view(), name='home'),
)
