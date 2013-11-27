from django.conf.urls import patterns, url
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required


urlpatterns = patterns('',
    url(r'^$', login_required(TemplateView.as_view(template_name='dash/dash.html')), name='default'),
)

