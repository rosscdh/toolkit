from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from .views import DashboardView


urlpatterns = patterns('',
    url(r'^$', login_required(DashboardView.as_view()), name='default'),
)
