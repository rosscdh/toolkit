# -*- coding: utf-8 -*-
from django.test import LiveServerTestCase
from django.core.files.storage import FileSystemStorage
from django.test.client import Client

from model_mommy import mommy
from pyquery import PyQuery as pq

from .base import BaseCasperJs

from toolkit.apps.eightythreeb.tests.data import EIGHTYTHREEB_DATA

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

    def basic_workspace(self):
        self.user = mommy.make('auth.User', first_name='Customer', last_name='Test', email='test+customer@lawpal.com')
        self.lawyer = mommy.make('auth.User', first_name='Lawyer', last_name='Test', email='test+lawyer@lawpal.com')

        self.workspace = mommy.make('workspace.Workspace', name='Lawpal (test)')
        self.workspace.tools.add(Tool.objects.get(slug='83b-election-letters'))
        self.workspace.participants.add(self.user)
        self.workspace.participants.add(self.lawyer)

        EIGHTYTHREEB_DATA = EIGHTYTHREEB_DATA.copy()
        EIGHTYTHREEB_DATA['markers'] = {}  # set teh markers to nothing

        self.eightythreeb = mommy.make('eightythreeb.EightyThreeB',
                            slug='e0c545082d1241849be039e338e47a0f',
                            workspace=self.workspace,
                            user=self.user,
                            data=EIGHTYTHREEB_DATA,
                            filing_date=datetime.date.today() + datetime.timedelta(days=30),
                            transfer_date=datetime.date.today(),
                            status=EightyThreeB.lawyer_complete_form)
