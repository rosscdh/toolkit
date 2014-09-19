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

    def test_field_on_new(self):
        form = MatterForm(instance=self.matter, user=self.lawyer)

        # defaults to is_new=True
        self.assertItemsEqual(form.helper.layout.get_field_names(), [[[0], 'name'], [[1], 'client_name'], [[2], 'matter_code'], [[3], 'is_secure'], [[4, 0], 'template']])

        # manual
        form = MatterForm(instance=self.matter, user=self.lawyer, is_new=True)
        self.assertItemsEqual(form.helper.layout.get_field_names(), [[[0], 'name'], [[1], 'client_name'], [[2], 'matter_code'], [[3], 'is_secure'], [[4, 0], 'template']])

        form = MatterForm(instance=self.matter, user=self.lawyer, is_new=False)

        self.assertItemsEqual(form.helper.layout.get_field_names(), [[[0], 'name'], [[1], 'client_name'], [[2], 'matter_code'], [[3], 'is_secure']])

    def test_user_can_modify(self):
        form = MatterForm(instance=self.matter, user=self.lawyer, is_new=True)
        self.assertTrue(form.user_can_modify)

        form = MatterForm(instance=self.matter, user=self.lawyer, is_new=False)
        self.assertTrue(form.user_can_modify)

        # Normal Users can modify the form if it is new i.e. they are creating it
        form = MatterForm(instance=self.matter, user=self.user, is_new=True)
        self.assertTrue(form.user_can_modify)

        form = MatterForm(instance=self.matter, user=self.user, is_new=False)
        self.assertFalse(form.user_can_modify)

    def test_delete_button_shows(self):
        #
        # Only the matter owner/lawyer can delete the matter
        #
        form = MatterForm(instance=self.matter, user=self.lawyer, is_new=False)       
        self.assertItemsEqual([b.name for b in form.helper.inputs if b.input_type in ('button', 'submit',)], ['delete', 'cancel', 'submit'])

        # The participants should only have the ability to stop participating
        form = MatterForm(instance=self.matter, user=self.user, is_new=False)
        self.assertItemsEqual([b.name for b in form.helper.inputs if b.input_type in ('button', 'submit',)], ['stop-participating', 'cancel'])

    def test_stop_participating_button_shows(self):
        # The participants should only have the ability to stop participating
        form = MatterForm(instance=self.matter, user=self.user, is_new=False)
        self.assertItemsEqual([b.name for b in form.helper.inputs if b.input_type in ('button', 'submit',)], ['stop-participating', 'cancel'])
        
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
