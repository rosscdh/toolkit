# -*- coding: UTF-8 -*-
from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from .views import ConfirmAccountView, ChangePasswordView, AccountSettingsView


urlpatterns = patterns(
    '',
    url(r'^settings/confirm/$', login_required(ConfirmAccountView.as_view()), name='confirm-account'),
    url(r'^settings/change-password/$', login_required(ChangePasswordView.as_view()), name='change-password'),
    url(r'^settings/$', login_required(AccountSettingsView.as_view()), name='settings'),
)
