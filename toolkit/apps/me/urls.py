from django.conf.urls import patterns, url

from .views import ConfirmAccountView, ChangePasswordView, AccountSettingsView


urlpatterns = patterns(
    '',
    url(r'^settings/confirm/$', ConfirmAccountView.as_view(), name='confirm-account'),
    url(r'^settings/change-password/$', ChangePasswordView.as_view(), name='change-password'),
    url(r'^settings/$', AccountSettingsView.as_view(), name='settings'),
)
