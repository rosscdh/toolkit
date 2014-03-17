from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from .views import RequestListView


urlpatterns = patterns('',
    url(r'^$', login_required(RequestListView.as_view())),
)
