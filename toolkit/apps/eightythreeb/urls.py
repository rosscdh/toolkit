from django.conf import settings
from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

from django.contrib import admin

url(r'^', TemplateView.as_view(template_name='dash.html')),  # @TODO ross will probably reorg this
