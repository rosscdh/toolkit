# -*- coding: UTF-8 -*-
from django.conf.urls import patterns, url
from django.views.generic import UpdateView
from django.contrib.auth.decorators import login_required

from .views import ConfirmAccountView, ChangePasswordView, AccountSettingsView, LawyerLetterheadView


urlpatterns = patterns(
    '',
    url(r'^settings/letterhead/$', login_required(LawyerLetterheadView.as_view()), name='letterhead'),
    url(r'^settings/confirm/$', login_required(ConfirmAccountView.as_view()), name='confirm-account'),
    url(r'^settings/change-password/$', login_required(ChangePasswordView.as_view()), name='change-password'),
    url(r'^settings/$', login_required(AccountSettingsView.as_view()), name='settings'),
)
