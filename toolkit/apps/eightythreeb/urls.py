# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required

from .views import CreateEightyThreeBView


urlpatterns = patterns('',
    url(r'^create/$', login_required(CreateEightyThreeBView.as_view()), name='create'),
)

