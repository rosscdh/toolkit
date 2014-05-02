# -*- coding: utf-8 -*-
from django.test import LiveServerTestCase
from django.core.urlresolvers import reverse

from model_mommy import mommy

from toolkit.casper.workflow_case import BaseScenarios
from toolkit.casper.base import BaseCasperJs


class MatterSearchClientSideTest(BaseScenarios, BaseCasperJs, LiveServerTestCase):
    def setUp(self):
        super(MatterSearchClientSideTest, self).setUp()
        self.basic_workspace()

    def test_lawyer_matter_list(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        for i in range(0,5):
            matter = mommy.make('workspace.Workspace', name='Lawpal (test) %d' % i, lawyer=self.lawyer, client=self.workspace_client)
            matter.participants.add(self.lawyer)

        url = reverse('matter:list')
        self.assertTrue(self.load_casper_file(js_file='matter_list_basic.js', test_label='Basic Tests of the matter list for a lawyer', url=url))
