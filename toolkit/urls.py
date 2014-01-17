# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

from django.contrib import admin
admin.autodiscover()

handler500 = 'toolkit.apps.default.views.handler500'

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include('toolkit.apps.api.urls', namespace='api')),
    url(r'^dash/', include('toolkit.apps.dash.urls', namespace='dash')),

    url(r'^me/pasword/', include('password_reset.urls')),
    url(r'^me/', include('toolkit.apps.me.urls', namespace='me')),

    url(r'^workspace/', include('toolkit.apps.workspace.urls', namespace='workspace')),
    url(r'^83b/', include('toolkit.apps.eightythreeb.urls', namespace='eightythreeb')),

    # home default terminator
    url(r'^', include('toolkit.apps.default.urls', namespace='public')),
)
