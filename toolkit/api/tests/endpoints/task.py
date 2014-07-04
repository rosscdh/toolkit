# -*- coding: utf-8 -*-
from rest_framework.reverse import reverse

from . import BaseEndpointTest
#from ...serializers import TaskSerializer

from model_mommy import mommy

import json


class TaskTest(BaseEndpointTest):
    """
    /matters/:matter_slug/items/:item_slug/tasks (GET,POST)
        Allow the [lawyer,customer] user to list and create items
    """
    def setUp(self):
        super(TaskTest, self).setUp()

        self.forbidden_user = mommy.make('auth.User', username='forbidden-user', email='forbidden+user@lawpal.com')
        self.forbidden_user.set_password(self.password)
        self.forbidden_user.save()

        self.item = mommy.make('item.Item', matter=self.workspace, name='Test Item No. 1')
        self.task = mommy.make('task.Task', item=self.item, created_by=self.lawyer, assigned_to=[self.user], name='Test Task No. 1')

    @property
    def endpoint(self):
        return reverse('item_tasks', kwargs={'matter_slug': self.workspace.slug, 'item_slug': self.item.slug})

    def test_endpoint_name(self):
        self.assertEqual(self.endpoint, '/api/v1/matters/lawpal-test/items/%s/tasks' % self.item.slug)

    def test_participant_can_read(self):
        self.client.login(username=self.user.username, password=self.password)

        resp = self.client.get(self.endpoint)
        self.assertEqual(resp.status_code, 200)  # ok list

        json_data = json.loads(resp.content)

        self.assertEqual(len(json_data['results']), 1)

    def test_non_participant_cant_read(self):
        self.client.login(username=self.forbidden_user.username, password=self.password)

        resp = self.client.get(self.endpoint)
        self.assertEqual(resp.status_code, 403)  # forbidden
