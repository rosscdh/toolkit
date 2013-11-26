from django.conf.urls import patterns, url
from django.views.generic import TemplateView


urlpatterns = patterns('',
    url(r'^dash/$', TemplateView.as_view(template_name='dash/dash.html'), name='default'),
)

