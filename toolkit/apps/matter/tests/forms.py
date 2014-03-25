# -*- coding: utf-8 -*-
import json

from django.test import TestCase

from toolkit.apps.workspace.models import Workspace
from toolkit.core.client.models import Client
from toolkit.casper.workflow_case import BaseScenarios

from ..forms import MatterForm


class MatterFormTest(BaseScenarios, TestCase):
    def setUp(self):
        super(MatterFormTest, self).setUp()
        self.basic_workspace()

    def test_initial_values(self):
        workspace = Workspace(
            client=Client(name='Acme Inc', lawyer=self.lawyer),
            name='Incorporation & Financing'
        )

        form = MatterForm(instance=workspace, user=self.lawyer)
        self.assertEqual(form.initial['client_name'], 'Acme Inc')
        self.assertEqual(form.initial['name'], 'Incorporation & Financing')

    def test_success(self):
        data = {
            'client_name': 'Acme Inc',
            'name': 'Incorporation & Financing'
        }
        form = MatterForm(user=self.lawyer, data=data)
        self.assertTrue(form.is_valid())

        m = form.save()
        self.assertEqual(m.name, 'Incorporation & Financing')

        # make sure the client and lawyer have been set
        self.assertEqual(m.client.name, 'Acme Inc')
        self.assertEqual(m.client.lawyer, self.lawyer)
        self.assertEqual(m.lawyer, self.lawyer)

        # make sure the lawyer is a participant
        self.assertEqual(m.participants.count(), 1)
        self.assertEqual(m.participants.all()[0], self.lawyer)

    def test_client_name_data_source(self):
        Client.objects.all().delete()
        Client.objects.create(name='Acme Inc', lawyer=self.lawyer)
        Client.objects.create(name='Bar Inc', lawyer=self.lawyer)
        Client.objects.create(name='Foo Inc', lawyer=self.lawyer)

        form = MatterForm(user=self.lawyer)
        self.assertItemsEqual(form.fields['client_name'].widget.attrs['data-source'], json.dumps(list(['Acme Inc', 'Bar Inc', 'Foo Inc'])))
