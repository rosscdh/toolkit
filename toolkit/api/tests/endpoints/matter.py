# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse

from toolkit.apps.workspace.models import Workspace

from . import BaseEndpointTest
from ...serializers import ClientSerializer

from model_mommy import mommy

import json


class MattersTest(BaseEndpointTest):
    """
    /matters/ (GET,POST)
        Allow the [lawyer] user to list, and create new matter ("workspace") objects
    """
    endpoint = reverse('workspace-list')

    def test_endpoint_name(self):
        self.assertEqual(self.endpoint, '/api/v1/matters')

    def test_lawyer_get(self):
        self.client.login(username=self.lawyer.username, password=self.password)
        resp = self.client.get(self.endpoint)

        self.assertEqual(resp.status_code, 200)

        json_data = json.loads(resp.content)
        self.assertEqual(json_data['count'], 1)
        self.assertEqual(json_data['results'][0]['name'], self.workspace.name)

    def test_lawyer_post(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        new_client = mommy.prepare('client.Client', lawyer=self.lawyer, name='A new Client for Test Lawyer')

        resp = self.client.post(self.endpoint, json.dumps(ClientSerializer(new_client).data), content_type='application/json')

        self.assertEqual(resp.status_code, 201)  # created

        json_data = json.loads(resp.content)
        self.assertEqual(json_data['name'], new_client.name)

    def test_lawyer_patch(self):
        self.client.login(username=self.lawyer.username, password=self.password)
        resp = self.client.patch(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 405)  # not allowed

    def test_lawyer_delete(self):
        self.client.login(username=self.lawyer.username, password=self.password)
        resp = self.client.delete(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 405)  # not allowed

    def test_customer_get(self):
        self.client.login(username=self.user.username, password=self.password)
        resp = self.client.get(self.endpoint)

        self.assertEqual(resp.status_code, 200)

        json_data = json.loads(resp.content)
        self.assertEqual(json_data['count'], 1)
        self.assertEqual(json_data['results'][0]['name'], self.workspace.name)

    def test_customer_post(self):
        self.client.login(username=self.user.username, password=self.password)
        resp = self.client.post(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)

    def test_customer_patch(self):
        self.client.login(username=self.user.username, password=self.password)
        resp = self.client.patch(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # method forbidden

    def test_customer_delete(self):
        self.client.login(username=self.user.username, password=self.password)
        resp = self.client.delete(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # method forbidden

    def test_anon_get(self):
        resp = self.client.get(self.endpoint)
        self.assertEqual(resp.status_code, 401)  # denied

    def test_anon_post(self):
        resp = self.client.post(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 401)  # denied

    def test_anon_patch(self):
        resp = self.client.patch(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 401)  # denied

    def test_anon_delete(self):
        resp = self.client.delete(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 401)  # denied



class MatterDetailTest(BaseEndpointTest):
    """
    /matters/:matter_slug/ (GET,PATCH,DELETE)
        Allow the [lawyer] user to list, and update an existing matter ("workspace") object
    """
    @property
    def endpoint(self):
        return reverse('workspace-detail', kwargs={'slug': self.workspace.slug})

    def test_endpoint_name(self):
        self.assertEqual(self.endpoint, '/api/v1/matters/lawpal-test')

    def test_lawyer_get(self):
        self.client.login(username=self.lawyer.username, password=self.password)
        resp = self.client.get(self.endpoint)

        self.assertEqual(resp.status_code, 200)

        json_data = json.loads(resp.content)
        self.assertEqual(json_data['name'], self.workspace.name)

    def test_lawyer_post(self):
        self.client.login(username=self.lawyer.username, password=self.password)
        resp = self.client.post(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 405)  # not implemented

    def test_lawyer_patch(self):
        expected_name = 'Changed Name test'

        self.client.login(username=self.lawyer.username, password=self.password)

        resp = self.client.patch(self.endpoint, json.dumps({'name': expected_name}), content_type='application/json')
        self.assertEqual(resp.status_code, 200)  # patched

        json_data = json.loads(resp.content)
        self.assertEqual(json_data['name'], expected_name)

    def test_lawyer_delete(self):
        """
        Lawyer can Soft delete workspaces
        """
        self.client.login(username=self.lawyer.username, password=self.password)
        resp = self.client.delete(self.endpoint, {}, content_type='application/json')

        self.assertEqual(resp.status_code, 204)  # no content but 2** success

        deleted_workspaces = Workspace.objects.deleted()
        self.assertEqual(len(deleted_workspaces), 1)

        deleted_workspace = deleted_workspaces[0]
        self.assertEqual(deleted_workspace.name, self.workspace.name)

    def test_customer_get(self):
        self.client.login(username=self.user.username, password=self.password)
        resp = self.client.get(self.endpoint)

        self.assertEqual(resp.status_code, 200)

        json_data = json.loads(resp.content)
        self.assertEqual(json_data['name'], self.workspace.name)

    def test_customer_post(self):
        self.client.login(username=self.user.username, password=self.password)
        resp = self.client.post(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)

    def test_customer_patch(self):
        self.client.login(username=self.user.username, password=self.password)

        resp = self.client.patch(self.endpoint, json.dumps({}), content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_customer_delete(self):
        """
        customers may not delete
        """
        self.client.login(username=self.user.username, password=self.password)
        resp = self.client.delete(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # method forbidden

    def test_anon_get(self):
        resp = self.client.get(self.endpoint)
        self.assertEqual(resp.status_code, 401)  # denied

    def test_anon_post(self):
        resp = self.client.post(self.endpoint, {})
        self.assertEqual(resp.status_code, 401)  # denied

    def test_anon_patch(self):
        resp = self.client.patch(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 401)  # denied

    def test_anon_delete(self):
        resp = self.client.delete(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 401)  # denied