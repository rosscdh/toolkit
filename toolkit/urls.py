# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),

    #url(r'^docs/', include('rest_framework_swagger.urls')),

    url(r'^83b/', include('toolkit.apps.eightythreeb.urls', namespace='eightythreeb')),
    url(r'^workspace/', include('toolkit.apps.workspace.urls', namespace='workspace')),

    url(r'^dash/', include('toolkit.apps.dash.urls', namespace='dash')),

    # home default terminator
    url(r'^', include('toolkit.apps.default.urls', namespace='public')),

)
