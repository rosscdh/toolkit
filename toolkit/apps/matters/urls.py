from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from .views import MatterDetailView, MatterListView


urlpatterns = patterns('',
    url(r'^$', login_required(MatterListView.as_view()), name='list'),
    url(r'^(?P<matter_slug>[\w\d-]+)/$', login_required(MatterDetailView.as_view()), name='detail')
)
