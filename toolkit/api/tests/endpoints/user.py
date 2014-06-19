# -*- coding: utf-8 -*-
from rest_framework.reverse import reverse

from . import BaseEndpointTest

from model_mommy import mommy

import json


class UsersTest(BaseEndpointTest):
    """
    /users/:username/ (GET,PATCH,DELETE)
        Allow all user to get user objects
        Allow the user to update his own data
        Allow the staff and superuser to delete user objects
    """
    def setUp(self):
        super(UsersTest, self).setUp()
        self.testuser = mommy.make('auth.User',
                                username='testuser-123',
                                email='testuser-123@lawpal.com')

    @property
    def endpoint(self):
        return reverse('user-detail', kwargs={'username': self.testuser.username })

    def get_own_user_endpoint(self, username):
        return reverse('user-detail', kwargs={'username': username })

    def test_endpoint_name(self):
        self.assertEqual(self.endpoint, '/api/v1/users/%s' % self.testuser.username)

    def test_lawyer_get(self):
        self.client.login(username=self.lawyer.username, password=self.password)
        resp = self.client.get(self.endpoint)

        self.assertEqual(resp.status_code, 200)

        json_data = json.loads(resp.content)
        self.assertEqual(json_data['username'], self.testuser.username)

    def test_lawyer_post(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        resp = self.client.post(self.endpoint, {}, content_type='application/json')

        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_lawyer_patch(self):
        self.client.login(username=self.lawyer.username, password=self.password)
        resp = self.client.patch(self.endpoint, json.dumps({}), content_type='application/json')

        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_lawyer_delete(self):
        self.client.login(username=self.lawyer.username, password=self.password)
        resp = self.client.delete(self.endpoint, json.dumps({}), content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_customer_get(self):
        self.client.login(username=self.user.username, password=self.password)
        resp = self.client.get(self.endpoint)
        self.assertEqual(resp.status_code, 200)

        json_data = json.loads(resp.content)
        self.assertEqual(json_data['username'], self.testuser.username)

    def test_customer_post(self):
        self.client.login(username=self.user.username, password=self.password)
        resp = self.client.post(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_customer_patch(self):
        self.client.login(username=self.user.username, password=self.password)
        resp = self.client.patch(self.endpoint, json.dumps({}), content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

        self.client.login(username=self.user.username, password=self.password)
        resp = self.client.patch(self.get_own_user_endpoint(self.user.username), json.dumps({'first_name':'NewName'}), content_type='application/json')
        self.assertEqual(resp.status_code, 200)  # forbidden

        json_data = json.loads(resp.content)
        self.assertEqual(json_data['first_name'], 'NewName')

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