# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse

from model_mommy import mommy
from pyquery import PyQuery as pq

from .base import BaseCasperJs

from toolkit.core.item.models import Item
from toolkit.api.serializers import MatterSerializer

import json
import logging
import datetime
logger = logging.getLogger('django.test')


class PyQueryMixin(object):
    """
    Base mixin for using PyQuery for response.content selector lookups
    https://pypi.python.org/pypi/pyquery
    """
    def setUp(self):
        super(PyQueryMixin, self).setUp()
        self.pq = pq


class BaseScenarios(object):
    fixtures = ['sites', 'tools']
    password = 'password'

    def basic_workspace(self):
        from toolkit.apps.workspace.models import Tool
        from toolkit.apps.eightythreeb.models import EightyThreeB
        from toolkit.apps.eightythreeb.tests.data import EIGHTYTHREEB_DATA as BASE_EIGHTYTHREEB_DATA

        self.user = mommy.make('auth.User', username='test-customer', first_name='Customër', last_name='Tëst',
                               email='test+customer@lawpal.com')
        self.user.set_password(self.password)
        self.user.save()

        user_profile = self.user.profile
        user_profile.validated_email = True
        user_profile.save(update_fields=['data'])

        self.lawyer = mommy.make('auth.User', username='test-lawyer', first_name='Lawyër', last_name='Tëst',
                                 email='test+lawyer@lawpal.com')
        self.lawyer.set_password(self.password)
        self.lawyer.save()

        lawyer_profile = self.lawyer.profile
        lawyer_profile.validated_email = True
        lawyer_profile.data['user_class'] = 'lawyer'
        lawyer_profile.save(update_fields=['data'])

        self.workspace_client = mommy.make('client.Client', name='Test Client Namë', lawyer=self.lawyer)
        # have to set worksace as well as matter
        # @TODO remove tests using workspace and use matter instead
        self.workspace = self.matter = mommy.make('workspace.Workspace', name='Lawpal (test)', lawyer=self.lawyer,
                                                  client=self.workspace_client)

        # Add all the toolks to the workspace
        for tool in Tool.objects.all():
            self.workspace.tools.add(tool)

        eightythreeb_data = BASE_EIGHTYTHREEB_DATA
        eightythreeb_data['markers'] = {}  # set the markers to nothing

        self.eightythreeb = mommy.make('eightythreeb.EightyThreeB',
                            slug='e0c545082d1241849be039e338e47a0f',
                            workspace=self.workspace,
                            user=self.user,
                            data=eightythreeb_data,
                            filing_date=datetime.date.today() + datetime.timedelta(days=30),
                            transfer_date=datetime.date.today(),
                            status=EightyThreeB.STATUS.lawyer_complete_form)

        # endpoint for api cretion via the api
        self.item_create_endpoint = reverse('matter_items', kwargs={'matter_slug': self.matter.slug})


    def _api_create_item(self, **kwargs):
        """
        Create items via the api (to get the activity)
        """
        if kwargs.get('matter'):
            kwargs['matter'] = MatterSerializer(kwargs['matter']).data.get('url')

        if not self.client.session:
            self.client.login(username=self.lawyer.username, password=self.password)

        resp = self.client.post(self.item_create_endpoint,
                                kwargs)
        json_resp = json.loads(resp.content)

        return Item.objects.get(slug=json_resp.get('slug'))


class BaseProjectCaseMixin(BaseScenarios, BaseCasperJs):
    """
    Base mixin for a Setup to be used in lawyer/customer/project analysis
    https://github.com/dobarkod/django-casper/
    @TODO no longer really required.. simply extend base scenarios
    """
    pass

