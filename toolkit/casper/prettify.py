# -*- coding: utf-8 -*-
from functools import wraps

import re
import inspect
import httpretty

import logging
logger = logging.getLogger('django.test')


def mock_http_requests(view_func):
    """
    A generic decorator to be called on all methods that do somethign with
    external apis
    """
    def _decorator(request, *args, **kwargs):
        #
        # Abridge
        #
        httpretty.register_uri(httpretty.POST, re.compile("http://abridge.local.dev/(.+)"),
                               body='{"success": true}',
                               status=200)
        httpretty.register_uri(httpretty.GET, re.compile("http://abridge.local.dev/(.+)"),
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
    @httpretty.activate
    def decorate(cls):
        for mthd in [name for name, mthd in inspect.getmembers(cls, predicate=inspect.ismethod) if name.endswith('_test') or name.startswith('test_') or name == 'setUp']:  # there's propably a better way to do this
            if callable(getattr(cls, mthd)):
                logger.info("Applying HTTP Mock to %s.%s" % (cls.__name__, mthd))
                setattr(cls, mthd, mock_http_requests(getattr(cls, mthd)))
        return cls
    return decorate
