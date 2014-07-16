from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from .views import CompletedRequestListView, OpenRequestListView


urlpatterns = patterns('',
    url(r'^$', login_required(OpenRequestListView.as_view()), name='list'),
    url(r'^completed/$', login_required(CompletedRequestListView.as_view()), name='list_completed'),
)
