# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from .views import (InboxNotificationsView,
                    ReadNotificationsView,
                    InboxViewSet,
                    MarkAllAsReadEndpoint,)


urlpatterns = patterns('',
    url(r'^endpoints/inbox/all/read/$', login_required(MarkAllAsReadEndpoint.as_view()), name='inbox-mark-all-read'),
    url(r'^endpoints/inbox/(?P<pk>\d+)/read/$', login_required(InboxViewSet.as_view()), name='inbox-read'),
    #
    url(r'^read/$', login_required(ReadNotificationsView.as_view()), name='read-notifications'),
    url(r'^$', login_required(InboxNotificationsView.as_view()), name='default'),
)
