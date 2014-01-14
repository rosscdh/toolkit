# -*- coding: utf-8 -*-
from django.test import TestCase
from django.core.urlresolvers import reverse

from toolkit.casper import BaseScenarios, PyQueryMixin
from toolkit.apps.workspace.forms import WorkspaceForm
from toolkit.apps.workspace.models import Workspace
from toolkit.apps.dash.views import DashView


class LawyerCreateWorkspaceTest(BaseScenarios, PyQueryMixin, TestCase):
    def setUp(self):
        super(LawyerCreateWorkspaceTest, self).setUp()
        self.basic_workspace()

        self.client.login(username=self.lawyer.username, password=self.password)


    def test_lawyer_create_workspace(self):
        """
        The lawyer should be able to create a workspace
        and immediately be assigned as the workspace.lawyer
        """
        create_url = reverse('workspace:create')
        resp = self.client.get(create_url, follow=True)
        # test general stuff
        self.assertEqual(resp.status_code, 200)

        # Setup the form variables for later
        form = resp.context_data.get('form')
        form_data = form.initial
        self.assertEqual(type(form), WorkspaceForm)

        # get HTML response
        html = resp.rendered_content
        context = self.pq(html)
        # test we have the form inputs
        self.assertEqual(len(context('form input')), 3)  # we have the id_name present
        # test the id_name is present
        self.assertEqual(len(context('form input#id_name')), 1)  # we have the id_name present

        # submit the form and make it good
        form_data.update({
            'name': 'Test Workspace',
        })
        form_resp = self.client.post(create_url, form_data, follow=True)
        self.assertEqual(form_resp.status_code, 200)
        self.assertEqual(type(form_resp.context_data.get('view')), DashView)

        # was it created? with the appropriate slug?
        workspace = Workspace.objects.get(slug='test-workspace')
        # the lawyer that created the worksapce is set as the lawyer
        self.assertEqual(workspace.lawyer, self.lawyer)
