# -*- coding: utf-8 -*-
from rest_framework.reverse import reverse

from . import BaseEndpointTest
from ...serializers import ClientSerializer

from model_mommy import mommy

import json


class ClientsTest(BaseEndpointTest):
    """
    /clients/ (GET,POST)
        Allow the [lawyer] user to list and create client objects

    /clients/:slug/ (GET,PATCH,DELETE)
        Allow the [lawyer] user to list, update and delete client objects
    """
    endpoint = reverse('client-list')

    def test_endpoint_name(self):
        self.assertEqual(self.endpoint, '/api/v1/clients')

    def test_lawyer_get(self):
        self.client.login(username=self.lawyer.username, password=self.password)
        resp = self.client.get(self.endpoint)

        self.assertEqual(resp.status_code, 200)

        json_data = json.loads(resp.content)
        self.assertEqual(json_data['count'], 2)
        self.assertEqual(json_data['results'][1]['name'], self.lawyer_client.__unicode__())

    def test_lawyer_post(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        new_client = mommy.prepare('client.Client', lawyer=self.lawyer, name='A new Client for Test Lawyer')

        resp = self.client.post(self.endpoint, json.dumps(ClientSerializer(new_client).data), content_type='application/json')

        self.assertEqual(resp.status_code, 201)  # created

        json_data = json.loads(resp.content)
        self.assertEqual(json_data['name'], new_client.name)

    def test_lawyer_patch(self):
        self.client.login(username=self.lawyer.username, password=self.password)
        resp = self.client.patch(self.endpoint, json.dumps({}), content_type='application/json')
        self.assertEqual(resp.status_code, 405)  # not allowed

    def test_lawyer_delete(self):
        self.client.login(username=self.lawyer.username, password=self.password)
        resp = self.client.delete(self.endpoint, json.dumps({}), content_type='application/json')
        self.assertEqual(resp.status_code, 405)  # not allowed

    def test_customer_get(self):
        self.client.login(username=self.user.username, password=self.password)
        resp = self.client.get(self.endpoint)
        self.assertEqual(resp.status_code, 403)

    def test_customer_post(self):
        self.client.login(username=self.user.username, password=self.password)
        resp = self.client.post(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_customer_patch(self):
        self.client.login(username=self.user.username, password=self.password)
        resp = self.client.patch(self.endpoint, json.dumps({}), content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_customer_delete(self):
        self.client.login(username=self.user.username, password=self.password)
        resp = self.client.delete(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_anon_get(self):
        resp = self.client.get(self.endpoint)
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_anon_post(self):
        resp = self.client.post(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_anon_patch(self):
        resp = self.client.patch(self.endpoint, {})
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_anon_delete(self):
        resp = self.client.delete(self.endpoint, {})
        self.assertEqual(resp.status_code, 403)  # forbidden
