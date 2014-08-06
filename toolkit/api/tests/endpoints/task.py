# -*- coding: utf-8 -*-
from django.core import mail

from rest_framework.reverse import reverse

from . import BaseEndpointTest
from toolkit.apps.default.templatetags.toolkit_tags import ABSOLUTE_BASE_URL

from model_mommy import mommy

import json


class BaseTaskSetup(BaseEndpointTest):
    def setUp(self):
        super(BaseTaskSetup, self).setUp()

        self.forbidden_user = mommy.make('auth.User', username='forbidden-user', email='forbidden+user@lawpal.com')
        self.forbidden_user.set_password(self.password)
        self.forbidden_user.save()

        self.item = mommy.make('item.Item', matter=self.workspace, name='Test Item No. 1')
        self.task = mommy.make('task.Task', item=self.item, created_by=self.lawyer, assigned_to=[self.user], name='Test Task No. 1')
        self.no_asignees_task = mommy.make('task.Task', item=self.item, created_by=self.lawyer, assigned_to=[], name='Test No Assignees Task No. 2')


class TaskListTest(BaseTaskSetup):
    """
    /matters/:matter_slug/items/:item_slug/tasks (GET,POST)
        Allow the [lawyer,customer] user to list and create items
    """
    @property
    def endpoint(self):
        return reverse('item_tasks', kwargs={'matter_slug': self.workspace.slug, 'item_slug': self.item.slug})

    def test_endpoint_name(self):
        self.assertEqual(self.endpoint, '/api/v1/matters/%s/items/%s/tasks' % (self.matter.slug, self.item.slug))

    def test_participant_can_read(self):
        self.client.login(username=self.user.username, password=self.password)

        resp = self.client.get(self.endpoint)
        self.assertEqual(resp.status_code, 200)  # ok list

        json_data = json.loads(resp.content)

        self.assertEqual(len(json_data['results']), 1)

    def test_participant_create(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        resp = self.client.post(self.endpoint, {
            'name': 'My first task',
            'description': 'do something to get the elephant to stand on a cup with a mouse on it',
        })
        self.assertEqual(resp.status_code, 201)  # created

        json_data = json.loads(resp.content)

        self.assertEqual(json_data.keys(), [u'date_due', u'name', u'date_modified', u'url', u'created_by', u'is_complete', u'item', u'assigned_to', u'date_created', u'slug', u'description'])
        self.assertEqual(json_data.get('item'), u'http://testserver/api/v1/items/%s' % self.item.slug)
        self.assertEqual(json_data.get('created_by'), 'test-lawyer')

    def test_non_participant_cant_read(self):
        self.client.login(username=self.forbidden_user.username, password=self.password)

        resp = self.client.get(self.endpoint)
        self.assertEqual(resp.status_code, 403)  # forbidden


class TaskDetailTest(BaseTaskSetup):
    """
    /matters/:matter_slug/items/:item_slug/tasks/:task_slug (GET,DELETE,PATCH)
        Allow the [lawyer,customer] user to list and create items
    """
    @property
    def endpoint(self):
        return reverse('item_task', kwargs={'matter_slug': self.workspace.slug, 'item_slug': self.item.slug, 'slug': self.task.slug})

    def test_endpoint_name(self):
        self.assertEqual(self.endpoint, '/api/v1/matters/%s/items/%s/tasks/%s' % (self.matter.slug, self.item.slug, self.task.slug))

    def test_participant_can_read(self):
        self.client.login(username=self.user.username, password=self.password)

        resp = self.client.get(self.endpoint)
        self.assertEqual(resp.status_code, 200)  # ok list

        json_data = json.loads(resp.content)

        self.assertEqual(type(json_data), dict)
        self.assertEqual(json_data.keys(), [u'date_due', u'name', u'date_modified', u'url', u'created_by', u'is_complete', u'item', u'assigned_to', u'date_created', u'slug', u'description'])
        self.assertEqual(json_data.get('item'), u'http://testserver/api/v1/items/%s' % self.item.slug)
        self.assertEqual(json_data.get('created_by'), {u'username': u'test-lawyer', u'name': u'Lawy\xebr T\xebst', u'url': u'http://testserver/api/v1/users/test-lawyer', u'role': None, u'user_class': u'lawyer', u'initials': u'LT'})


    def test_participant_update_own(self):
        self.client.login(username=self.user.username, password=self.password)

        # CREATE my own task for the standard user
        create_endpoint = reverse('item_tasks', kwargs={'matter_slug': self.workspace.slug, 'item_slug': self.item.slug})

        resp = self.client.post(create_endpoint, {
            'name': 'User creates own task',
            'description': 'A standard client user can create tasks',
            'assigned_to': ['test-lawyer'],
        })
        self.assertEqual(resp.status_code, 201)  # created
        created_json_data = json.loads(resp.content)

        self.assertEqual(created_json_data.get('assigned_to'), ['test-lawyer'])  # only returns the username on post (as we assume gui has all the required data already)

        # see if they can patch their own items
        endpoint = reverse('item_task', kwargs={'matter_slug': self.workspace.slug, 'item_slug': self.item.slug, 'slug': created_json_data.get('slug')})

        resp = self.client.patch(endpoint, json.dumps({
            'name': 'Update to My first task',
            'assigned_to': ['test-customer'],  # replace the current set of assigned_to users with this one
        }), content_type='application/json; charset=utf-8')
        self.assertEqual(resp.status_code, 200)  # ok

        json_data = json.loads(resp.content)

        self.assertEqual(json_data.keys(), [u'date_due', u'name', u'date_modified', u'url', u'created_by', u'is_complete', u'item', u'assigned_to', u'date_created', u'slug', u'description'])
        self.assertEqual(json_data.get('created_by'), {u'username': u'test-customer', u'name': u'Custom\xebr T\xebst', u'url': u'http://testserver/api/v1/users/test-customer', u'role': None, u'user_class': u'customer', u'initials': u'CT'})
        self.assertEqual(json_data.get('assigned_to'), [{u'username': u'test-lawyer', u'name': u'Lawy\xebr T\xebst', u'url': u'http://testserver/api/v1/users/test-lawyer', u'role': None, u'user_class': u'lawyer', u'initials': u'LT'}])

    def test_assigned_to_can_update(self):
        self.client.login(username=self.user.username, password=self.password)

        resp = self.client.patch(self.endpoint, json.dumps({
            'name': 'Update to My first task',
        }), content_type='application/json; charset=utf-8')

        # Cannot update, as this task is owned by the lawyer
        self.assertEqual(resp.status_code, 200)  # updated

    def test_participant_cant_edit_other_participants_tasks(self):
        self.client.login(username=self.user.username, password=self.password)

        endpoint = reverse('item_task', kwargs={'matter_slug': self.workspace.slug, 'item_slug': self.item.slug, 'slug': self.no_asignees_task.slug})

        resp = self.client.patch(endpoint, json.dumps({
            'name': 'Update to My first task',
        }), content_type='application/json; charset=utf-8')

        # Cannot update, as this task is owned by the lawyer
        self.assertEqual(resp.status_code, 404)  # not found

    def test_non_participant_cant_read(self):
        self.client.login(username=self.forbidden_user.username, password=self.password)

        resp = self.client.get(self.endpoint)
        self.assertEqual(resp.status_code, 404)  # not found


class TaskReminderTest(BaseTaskSetup):
    """
    matters/:matter_slug/items/:item_slug/tasks/:slug/remind
    send reminders to people assigned to this task
    """
    @property
    def endpoint(self):
        return reverse('item_task_reminder', kwargs={'matter_slug': self.workspace.slug, 'item_slug': self.item.slug, 'slug': self.task.slug})

    def test_endpoint_name(self):
        self.assertEqual(self.endpoint, '/api/v1/matters/%s/items/%s/tasks/%s/remind' % (self.matter.slug, self.item.slug, self.task.slug))

    def test_send_reminder(self):
        self.client.login(username=self.lawyer.username, password=self.password)
        resp = self.client.post(self.endpoint, {})

        self.assertEqual(resp.status_code, 202)  # accepted
        # sent email
        self.assertTrue(len(mail.outbox) == 1)
        email = mail.outbox[0]
        self.assertEqual(email.subject, '[ACTION REQUIRED] Please complete the task')
        expected_action_url = ABSOLUTE_BASE_URL(self.task.get_absolute_url())
        self.assertTrue(expected_action_url in email.body)

