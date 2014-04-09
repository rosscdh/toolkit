# -*- coding: UTF-8 -*-
# settings-dev.py
from django.conf import settings


class NonHtmlDebugToolbarMiddleware(object):
    """
    To allow us to debug api requests

    This middleware should be place AFTER Django Debug Toolbar middleware

    In your local_settings.py override the MIDDLEWARE_CLASSES and add this middleware

    MIDDLEWARE_CLASSES += (
        'debug_toolbar.middleware.DebugToolbarMiddleware',
        'toolkit.middleware.NonHtmlDebugToolbarMiddleware',
    )
    """
    def process_response(self, request, response):

        #not for production or production like environment
        if not settings.DEBUG:
            return response

        #do nothing for actual ajax requests
        if request.is_ajax():
            return response

        #only do something if this is a json response
        if "application/json" in response['Content-Type'].lower():
            title = "JSON as HTML Middleware for: %s" % request.get_full_path()
            response.content = "<html><head><title>%s</title></head><body>%s</body></html>" % (title, response.content)
            response['Content-Type'] = 'text/html'
        return response