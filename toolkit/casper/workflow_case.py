# -*- coding: utf-8 -*-
from django.test import LiveServerTestCase
from django.core.files.storage import FileSystemStorage
from django.test.client import Client

from model_mommy import mommy
from pyquery import PyQuery as pq

from .base import BaseCasperJs

import mock
import logging
logger = logging.getLogger('django.test')


class PyQueryMixin(LiveServerTestCase):
    """
    Base mixin for using PyQuery for response.content selector lookups
    https://pypi.python.org/pypi/pyquery
    """
    def setUp(self):
        super(PyQueryMixin, self).setUp()
        self.pq = pq


class BaseProjectCaseMixin(BaseCasperJs):
    """
    Base mixin for a Setup to be used in lawyer/customer/project analysis
    https://github.com/dobarkod/django-casper/
    """
    fixtures = ['sites', 'tools']

    @mock.patch('django_filepicker.models.FPFileField', FileSystemStorage)
    def setUp(self):
        super(BaseProjectCaseMixin, self).setUp()
        self.client = Client()
