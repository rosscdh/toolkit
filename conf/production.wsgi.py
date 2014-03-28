"""
WSGI config for toolkit project.

This module contains the WSGI application used by Django's development server
and any production WSGI deployments. It should expose a module-level variable
named ``application``. Django's ``runserver`` and ``runfcgi`` commands discover
this application via the ``WSGI_APPLICATION`` setting.

Usually you will have the standard Django WSGI application here, but it also
might make sense to replace the whole Django WSGI application with a custom one
that later delegates to the Django one. For example, you could introduce WSGI
middleware here, or combine a Django application with an application of another
framework.

"""
import os, sys, site

# Tell wsgi to add the Python site-packages to its path. 
site.addsitedir('/var/apps/lib/python2.7/site-packages')
site.addsitedir('/var/apps/.toolkit-live-venv/lib/python2.7/site-packages')
site.addsitedir('/var/apps/toolkit/toolkit')
site.addsitedir('/var/apps/toolkit/toolkit/toolkit')

os.environ['DJANGO_SETTINGS_MODULE'] = 'toolkit.settings'

# Calculate the path based on the location of the WSGI script
project = '/var/apps/toolkit/toolkit/toolkit/'
workspace = os.path.dirname(project)
sys.path.append(workspace)

import newrelic.agent
newrelic.agent.initialize('/var/apps/toolkit/toolkit/toolkit/newrelic.ini')

from django.core.handlers.wsgi import WSGIHandler
application = WSGIHandler()
application = newrelic.agent.wsgi_application()(application)