# -*- coding: utf-8 -*-
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.utils import simplejson as json

from toolkit.casper import BaseScenarios, PyQueryMixin
from toolkit.apps.workspace.forms import WorkspaceForm
from toolkit.apps.workspace.models import Workspace
from toolkit.apps.dash.views import DashView


class LawyerCreateWorkspaceTest(BaseScenarios, PyQueryMixin, TestCase):
    def setUp(self):
        super(LawyerCreateWorkspaceTest, self).setUp()
        self.basic_workspace()

        # self.client.login(username=self.lawyer.username, password=self.password)


    def test_lawyer_create_workspace(self):
        """
        The lawyer should be able to create a workspace
        and immediately be assigned as the workspace.lawyer
        """
        url = reverse('workspace:create')

        # User not logged in
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], 'http://testserver/start/?next=/workspace/create/')

        self.client.login(username=self.lawyer.username, password=self.password)

        # Valid user
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

        # Valid submission
        resp = self.client.post(url, {
            'name': 'Test Workspace'
        }, follow=True)

        redirect = reverse('workspace:view', kwargs={'slug': 'test-workspace'})

        actual_response = {
            'redirect': True,
            'url': redirect
        }

        self.assertEqual(resp.content, json.dumps(actual_response))

        # was it created? with the appropriate slug?
        workspace = Workspace.objects.get(slug='test-workspace')

        # the lawyer that created the worksapce is set as the lawyer
        self.assertEqual(workspace.lawyer, self.lawyer)
