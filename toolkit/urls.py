# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls import patterns, include, url
from django.views.generic.base import RedirectView

from toolkit.static import static

from django.contrib import admin
admin.autodiscover()

handler500 = 'toolkit.apps.default.views.handler500'

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),

    url(r'^api/v1/', include('toolkit.api.urls')),
    url(r'^api/', include('toolkit.apps.api.urls', namespace='api')),

    url(r'^dash/', include('toolkit.apps.dash.urls', namespace='dash')),

    url(r'^notifications/', include('toolkit.apps.notification.urls', namespace='notification')),

    url(r'^matters/', include('toolkit.apps.matter.urls', namespace='matter')),
    url(r'^requests/', include('toolkit.apps.request.urls', namespace='request')),

    url(r'^me/pasword/', include('password_reset.urls')),
    url(r'^me/', include('toolkit.apps.me.urls', namespace='me')),

    # primary workspace
    url(r'^workspace/', include('toolkit.apps.workspace.urls', namespace='workspace')),

    # apps
    url(r'^83b/', include('toolkit.apps.eightythreeb.urls', namespace='eightythreeb')),
    url(r'^engagement-letters/', include('toolkit.apps.engageletter.urls', namespace='engageletter')),

    # reviews
    url(r'^review/', include('toolkit.apps.review.urls', namespace='review')),
    url(r'^crocodoc/', include('dj_crocodoc.urls')),

    # signing events
    url(r'^sign/', include('toolkit.apps.sign.urls', namespace='sign')),

    # Authy authentication
    url(r'^authy/', include('dj_authy.urls', namespace='dj_authy')),

    # Payments
    url(r'^payments/', include('payments.urls')),

    url(r'^favicon\.ico$', RedirectView.as_view(url='%simages/favicon.ico' % settings.STATIC_URL)),

    # home default terminator
    url(r'^', include('toolkit.apps.default.urls', namespace='public')),
)

if settings.DEBUG is True or settings.TEST_PREPROD is True:
    # Add the MEDIA_URL to the dev environment
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.IS_TESTING is True:
    #
    # Have to manually append complicated sub urls included in sub apps here
    # for test environment
    #
    urlpatterns += patterns('', url(r'^hellosign/', include('hello_sign.urls')))
