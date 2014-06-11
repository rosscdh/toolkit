# -*- coding: utf-8 -*-
from django.test import TestCase

from model_mommy import mommy

from toolkit.casper.workflow_case import BaseScenarios

import json
import random


class BaseEndpointTest(BaseScenarios, TestCase):
    """
    /clients/ (GET,POST)
        Allow the [lawyer] user to list and create client objects

    /clients/:slug/ (GET,PATCH,DELETE)
        Allow the [lawyer] user to list, update and delete client objects
    """
    endpoint = None

    def setUp(self):
        super(BaseEndpointTest, self).setUp()
        # basics
        self.basic_workspace()

        # provide a lawyer client
        self.lawyer_client = mommy.make('client.Client', lawyer=self.lawyer, name='Test Client for Test Lawyer')

    def tearDown(self):
        """
        Cleanup items
        """
        for item in self.matter.item_set.all().iterator():
            latest_revision = item.latest_revision
            if latest_revision is not None:
                latest_revision.executed_file.delete()

    def test_endpoint_name(self):
        self.assertEqual(self.endpoint, None)

    def add_signers(self, data=None):
        if data is None:
            rand_num = random.random()
            data = {'signers': [{
                'email': 'invited-signer-%s@lawpal.com' % rand_num,
                'first_name': '%s' % rand_num,
                'last_name': 'Invited Signer',
                'message': 'Please sign this documnet'}]
            }
        # must be logged in in order for this to work
        return self.client.post(self.endpoint, json.dumps(data), content_type='application/json')