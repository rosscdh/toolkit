from django.conf import settings
from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'toolkit.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^docs/', include('rest_framework_swagger.urls')),

    # new home
    url(r'^$', TemplateView.as_view(template_name='index.html')),  # @TODO ross will probably reorg this

    url(r'^dash/', TemplateView.as_view(template_name='dash.html')),  # @TODO ross will probably reorg this
    
    url(r'^forms/', include('toolkit.apps.eightythreeb')),

)
