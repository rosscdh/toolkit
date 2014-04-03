# -*- coding: UTF-8 -*-
from django.conf.urls import patterns, url
from django.views.generic import UpdateView
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required

from .views import (ConfirmAccountView,
                    ChangePasswordView,

                    ConfirmEmailValidationRequest,
                    SendEmailValidationRequest,

                    AccountSettingsView,
                    LawyerLetterheadView)


urlpatterns = patterns(
    '',
    url(r'^email_not_validated/$', login_required(TemplateView.as_view(template_name='me/email-validation-pending.html')), name='email-not-validated'),
    url(r'^email_not_validated/send/$', login_required(SendEmailValidationRequest.as_view()), name='send-email-validation-request'),
    url(r'^email_confirmed/(?P<token>[\w:-]+)/$', ConfirmEmailValidationRequest.as_view(), name='confirm-email-address'),
    
    
    url(r'^settings/letterhead/$', login_required(LawyerLetterheadView.as_view()), name='letterhead'),
    url(r'^settings/confirm/$', login_required(ConfirmAccountView.as_view()), name='confirm-account'),
    url(r'^settings/change-password/$', login_required(ChangePasswordView.as_view()), name='change-password'),
    url(r'^settings/$', login_required(AccountSettingsView.as_view()), name='settings'),
)
