# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from django.views.generic import DetailView, UpdateView
from django.contrib.auth.decorators import login_required

from .views import TrackingCodeView
from .models import EightyThreeB
from .forms import TrackingCodeForm


urlpatterns = patterns('',
    # url(r'^create/$', login_required(CreateEightyThreeBView.as_view()), name='create'),
    url(r'^(?P<slug>[\w-]+)/tracking_code/$', login_required(TrackingCodeView.as_view()), name='tracking_code'),
    # url(r'^(?P<slug>[\w-]+)/edit/$', login_required(UpdateView.as_view(model=EightyThreeB, form_class=EightyThreeBForm)), name='edit'),
    url(r'^(?P<slug>[\w-]+)/$', login_required(DetailView.as_view(model=EightyThreeB)), name='view'),
)

