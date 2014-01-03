# -*- coding: utf-8 -*-
from django.test import LiveServerTestCase
from django.core.files.storage import FileSystemStorage
from django.test.client import Client

from model_mommy import mommy
from pyquery import PyQuery as pq

from .base import BaseCasperJs

import mock
import logging
import datetime
logger = logging.getLogger('django.test')


class PyQueryMixin(LiveServerTestCase):
    """
    Base mixin for using PyQuery for response.content selector lookups
    https://pypi.python.org/pypi/pyquery
    """
    def setUp(self):
        super(PyQueryMixin, self).setUp()
        self.pq = pq


class BaseScenarios(object):
    fixtures = ['sites', 'tools']

    def basic_workspace(self):
        from toolkit.apps.workspace.models import Tool
        from toolkit.apps.eightythreeb.models import EightyThreeB
        from toolkit.apps.eightythreeb.tests.data import EIGHTYTHREEB_DATA as BASE_EIGHTYTHREEB_DATA

        self.user = mommy.make('auth.User', first_name='Customer', last_name='Test', email='test+customer@lawpal.com')
        self.lawyer = mommy.make('auth.User', first_name='Lawyer', last_name='Test', email='test+lawyer@lawpal.com')

        self.workspace = mommy.make('workspace.Workspace', name='Lawpal (test)')
        self.workspace.tools.add(Tool.objects.get(slug='83b-election-letters'))
        self.workspace.participants.add(self.user)
        self.workspace.participants.add(self.lawyer)

        eightythreeb_data = BASE_EIGHTYTHREEB_DATA.copy()
        eightythreeb_data['markers'] = {}  # set teh markers to nothing

        self.eightythreeb = mommy.make('eightythreeb.EightyThreeB',
                            slug='e0c545082d1241849be039e338e47a0f',
                            workspace=self.workspace,
                            user=self.user,
                            data=eightythreeb_data,
                            filing_date=datetime.date.today() + datetime.timedelta(days=30),
                            transfer_date=datetime.date.today(),
                            status=EightyThreeB.STATUS_83b.lawyer_complete_form)


class BaseProjectCaseMixin(BaseScenarios, BaseCasperJs):
    """
    Base mixin for a Setup to be used in lawyer/customer/project analysis
    https://github.com/dobarkod/django-casper/
    """
    @mock.patch('storages.backends.s3boto.S3BotoStorage', FileSystemStorage)
    def setUp(self):
        super(BaseProjectCaseMixin, self).setUp()
        self.client = Client()

