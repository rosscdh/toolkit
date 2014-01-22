# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from .views import SignAndSendEngagementLetterView, SetupEngagementLetterView


urlpatterns = patterns('',
    url(r'^(?P<slug>[\w-]+)/lawyer/template/$', login_required(SetupEngagementLetterView.as_view()), name='lawyer_template'),
    url(r'^(?P<slug>[\w-]+)/sign/$', login_required(SignAndSendEngagementLetterView.as_view()), name='sign'),
)
