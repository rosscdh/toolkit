# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

from .views import (InboxNotificationsView,
                    ReadNotificationsView,
                    InboxViewSet,
                    MarkAllAsReadEndpoint,)


urlpatterns = patterns('',
    url(r'^endpoints/inbox/all/read/$', MarkAllAsReadEndpoint.as_view(), name='inbox-mark-all-read'),
    url(r'^endpoints/inbox/(?P<pk>\d+)/read/$', InboxViewSet.as_view(), name='inbox-read'),
    #
    url(r'^read/$', ReadNotificationsView.as_view(), name='default'),
    url(r'^$', InboxNotificationsView.as_view(), name='default'),
)
