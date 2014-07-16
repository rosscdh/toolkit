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

        self.user = self.create_user(username='test-customer',
                                     first_name='Customër',
                                     last_name='Tëst',
                                     email='test+customer@lawpal.com')

        self.lawyer = self.create_user(username='test-lawyer',
                                       first_name='Lawyër',
                                       last_name='Tëst',
                                       email='test+lawyer@lawpal.com',
                                       user_class='lawyer')

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

    def set_user_matter_perms(self, user, matter=None, **kwargs):
        matter = self.matter if matter is None else matter
        user_perms = user.matter_permissions(matter=matter)
        user_perms.update_permissions(**kwargs)
        user_perms.save(update_fields=['data'])
        return user_perms.permissions

    def set_user_matter_role(self, user, role, matter=None):
        matter = self.matter if matter is None else matter
        user_perms = user.matter_permissions(matter=matter)
        user_perms.role = role
        user_perms.save(update_fields=['role'])
        return user_perms.role

    def create_user(self, username, email, user_class='customer', **extra_fields):
        user = mommy.make('auth.User', username=username, email=email, **extra_fields)
        user.set_password(self.password)
        user.save()

        profile = user.profile
        profile.user_class = user_class
        profile.validated_email = True
        profile.save(update_fields=['data'])

        return user


class BaseProjectCaseMixin(BaseScenarios, BaseCasperJs):
    """
    Base mixin for a Setup to be used in lawyer/customer/project analysis
    https://github.com/dobarkod/django-casper/
    @TODO no longer really required.. simply extend base scenarios
    """
    pass
