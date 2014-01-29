# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from .views import SignAndSendEngagementLetterView, SetupEngagementLetterTemplateView


urlpatterns = patterns('',
    url(r'^(?P<slug>[\w-]+)/template/lawyer/$', login_required(SetupEngagementLetterTemplateView.as_view()), name='lawyer_template'),
    url(r'^(?P<slug>[\w-]+)/sign/$', login_required(SignAndSendEngagementLetterView.as_view()), name='sign'),
)
