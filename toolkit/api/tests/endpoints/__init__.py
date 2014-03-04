# -*- coding: utf-8 -*-
from django.test import TestCase

from model_mommy import mommy

from toolkit.casper.workflow_case import BaseScenarios


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

        self.matter = self.workspace  # alias

        # provide a lawyer client
        self.lawyer_client = mommy.make('client.Client', lawyer=self.lawyer, name='Test Client for Test Lawyer')

    def test_endpoint_name(self):
        raise NotImplementedError
