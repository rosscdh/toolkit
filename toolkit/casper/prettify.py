# -*- coding: utf-8 -*-
from django.conf import settings
from functools import wraps

import re
import inspect
import httpretty

import logging
logger = logging.getLogger('django.test')


ABRIDGE_API_URL = getattr(settings, 'ABRIDGE_API_URL', 'http://abridge.local.dev/')


def mock_http_requests(view_func):
    """
    A generic decorator to be called on all methods that do somethign with
    external apis
    """
    @httpretty.activate
    def _decorator(request, *args, **kwargs):
        from toolkit.apps.eightythreeb.tests.usps_trackfield_response import TRACK_RESPONSE_XML_BODY
        from toolkit.apps.workspace.tests.data import HELLOSIGN_200_RESPONSE
        #
        # HelloSign
        #
        httpretty.register_uri(httpretty.POST, re.compile(r"^https://api.hellosign.com/v3/(.*)$"),
                               body=HELLOSIGN_200_RESPONSE,
                               status=200)
        #
        # Crocdoc
        #
        httpretty.register_uri(httpretty.POST, "https://crocodoc.com/api/v2/session/create",
                       body='{"session": "i_12345-123_123_123-12345_123"}',
                       status=200)
        httpretty.register_uri(httpretty.GET, "https://crocodoc.com/api/v2/document/status",
                       body='{"success": true}',
                       status=200)
        httpretty.register_uri(httpretty.POST, "https://crocodoc.com/api/v2/document/upload",
                       body='{"success": true, "uuid": "1ad40181-605c-0747-8dc5-5cacf8b3faa9"}',
                       status=200)
        httpretty.register_uri(httpretty.POST, "https://crocodoc.com/api/v2/document/delete",
                       body='{"token": "aHzHhSK4jaGes193db28vwjw", "uuid": "1ad40181-605c-0747-8dc5-5cacf8b3faa9"}',
                       status=200)
        httpretty.register_uri(httpretty.GET, re.compile("https://crocodoc.com/view/(.*)"),
                       body='This is a document',
                       status=200)
        #
        # USPS
        # POST and GET are the same as USPS is not REST or even RESTFUL
        #
        httpretty.register_uri(httpretty.POST, "http://production.shippingapis.com/ShippingAPI.dll",
                               body=TRACK_RESPONSE_XML_BODY,
                               status=200)
        httpretty.register_uri(httpretty.GET, "http://production.shippingapis.com/ShippingAPI.dll",
                               body=TRACK_RESPONSE_XML_BODY,
                               status=200)
        #
        # Abridge
        #
        httpretty.register_uri(httpretty.POST, re.compile("%s(.*)" % ABRIDGE_API_URL),
                               body='{"success": true}',
                               status=200)
        httpretty.register_uri(httpretty.GET, re.compile("%s(.*)" % ABRIDGE_API_URL),
                               body='{"success": true}',
                               status=200)
        #
        # Intercom & misc
        #
        httpretty.register_uri(httpretty.GET, re.compile("https://api.intercom.io/(.+)"),
                               body='{"success": true}',
                               status=200)
        httpretty.register_uri(httpretty.GET, re.compile("http://www.google-analytics.com/ga.js"),
                               body='{"success": true}',
                               status=200)

        # maybe do something before the view_func call
        response = view_func(request, *args, **kwargs)
        # maybe do something after the view_func call
        return response
    return wraps(view_func)(_decorator)



def httprettify_methods():
    """
    Method to wrap all methods within a decorated class
    with another decorator
    wraps all test methods with the "mock_http_requests" method which in turn
    sets up the httpretty mocks
    """
    def decorate(cls):
        for mthd in [name for name, mthd in inspect.getmembers(cls, predicate=inspect.ismethod) if name.endswith('_test') or name.startswith('test_') or name == 'setUp']:  # there's propably a better way to do this
            if callable(getattr(cls, mthd)):
                logger.info("Applying HTTP Mock to %s.%s" % (cls.__name__, mthd))
                setattr(cls, mthd, mock_http_requests(getattr(cls, mthd)))
        return cls
    return decorate
