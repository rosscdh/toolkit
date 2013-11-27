# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required

from .views import DashView

urlpatterns = patterns('',
    url(r'^$', login_required(DashView.as_view()), name='default'),
)

