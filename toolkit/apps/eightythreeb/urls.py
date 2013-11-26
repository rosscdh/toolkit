# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

from .views import CreateEightyThreeBView


urlpatterns = patterns('',
    url(r'^create/$', CreateEightyThreeBView.as_view(), name='create'),
)

