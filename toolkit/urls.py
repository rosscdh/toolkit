# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required

from django.contrib import admin
admin.autodiscover()

handler500 = 'toolkit.apps.default.views.handler500'

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),

    url(r'^api/v1/', include('toolkit.api.urls')),
    url(r'^api/', include('toolkit.apps.api.urls', namespace='api')),

    url(r'^dash/', include('toolkit.apps.dash.urls', namespace='dash')),

    url(r'^me/pasword/', include('password_reset.urls')),
    url(r'^me/', include('toolkit.apps.me.urls', namespace='me')),

    # primary workspace
    url(r'^workspace/', include('toolkit.apps.workspace.urls', namespace='workspace')),

    #matter angular app
    url(r'^matters/(?P<matter_slug>[a-zA-Z0-9_.-]+)/$',
         login_required(TemplateView.as_view(template_name="index_deployed.html"), name="matter-details-view")),


    # apps
    url(r'^83b/', include('toolkit.apps.eightythreeb.urls', namespace='eightythreeb')),
    url(r'^engagement-letters/', include('toolkit.apps.engageletter.urls', namespace='engageletter')),

    # signing events
    url(r'^sign/', include('hello_sign.urls', namespace='sign')),

    # home default terminator
    url(r'^', include('toolkit.apps.default.urls', namespace='public')),
)

if settings.DEBUG:
    # Add the MEDIA_URL to the dev environment
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
