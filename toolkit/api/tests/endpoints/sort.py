# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse

from toolkit.apps.workspace.models import Workspace

from . import BaseEndpointTest
from ...serializers import ClientSerializer

from model_mommy import mommy

import json
import random



class MatterSortTest(BaseEndpointTest):
    """
    Test that the matter and its items can be updated with a sort order

    PATCH /matters/:matter_slug/sort
    {
        "categories": ["cat 1", "cat 2", "im not a cat, im a dog"],
        "items": [2,5,7,1,12,22,4]
    }
    """
    # fixtures = ['sites', 'tools', 'dev-fixtures']

    @property
    def endpoint(self):
        return reverse('matter_sort', kwargs={'matter_slug': self.matter.slug})

    def setUp(self):
        super(MatterSortTest, self).setUp()

        # setup the items for testing
        mommy.make('item.Item', matter=self.matter, name='Test Item No. 1', category="A")
        mommy.make('item.Item', matter=self.matter, name='Test Item No. 2', category="A")
        mommy.make('item.Item', matter=self.matter, name='Test Item No. 3', category="B")
        mommy.make('item.Item', matter=self.matter, name='Test Item No. 4', category="C")
        mommy.make('item.Item', matter=self.matter, name='Test Item No. 5', category=None)

        self.items = self.matter.item_set.all()
        self.categories = ["A", "B", "C"]

    def test_endpoint_name(self):
        self.assertEqual(self.endpoint, '/api/v1/matters/lawpal-test/sort')

    def test_lawyer_get(self):
        """
        No get on this endpoint as its only allows update
        """
        self.client.login(username=self.lawyer.username, password=self.password)
        resp = self.client.get(self.endpoint)

        self.assertEqual(resp.status_code, 405)  # method not allowed

    def test_lawyer_post(self):
        """
        No post on this endpoint as its only allows update
        """
        self.client.login(username=self.lawyer.username, password=self.password)
        resp = self.client.post(self.endpoint)

        self.assertEqual(resp.status_code, 405)  # method not allowed

    def test_lawyer_patch(self):
        """
        Allow the lawyer to update the categories based on the posted dict in
        __doc__ string above
        """
        # when these items are created in setUp they get the following sort order
        # as we use .insert(0, value) and not .append

        self.assertEqual(self.matter.categories, [u'C', u'B', u'A'])

        self.client.login(username=self.lawyer.username, password=self.password)

        item_order = [i.get('pk') for i in self.matter.item_set.all().values('pk')]
        random.shuffle(item_order)

        data = {
            "categories": self.categories,
            "items": item_order,
        }

        resp = self.client.patch(self.endpoint, json.dumps(data), content_type='application/json')
        resp_json = json.loads(resp.content)

        self.assertEqual(resp.status_code, 200)  # all ok
        self.assertEqual(json.loads(resp_json), {"items": item_order, "categories": self.categories})

        # refresh
        self.matter = Workspace.objects.get(pk=self.matter.pk)

        # test categories are as we expect them
        self.assertEqual(self.matter.categories, [u'A', u'B', u'C'])

        # rely on the item.Meta.sort_order
        # the items should return from .all() in the same order as they are specified
        self.assertTrue(all(i.pk is item_order[sort_index] for sort_index, i in enumerate(self.matter.item_set.all())))

    def test_lawyer_patch_invalid(self):
        self.client.login(username=self.lawyer.username, password=self.password)
        resp = self.client.patch(self.endpoint, json.dumps({}), content_type='application/json')
        resp_json = json.loads(resp.content)

        self.assertEqual(resp.status_code, 400)  # invalid data
        self.assertEqual(resp_json['detail'], 'request.DATA must be: {"categories": [], "items": []}')  # correct message

        resp = self.client.patch(self.endpoint, json.dumps({"items": {}, "categories": ""}), content_type='application/json')
        resp_json = json.loads(resp.content)

        self.assertEqual(resp.status_code, 400)  # invalid data
        self.assertEqual(resp_json['detail'], 'categories and items must be of type list {"categories": [], "items": []}')  # correct message

    def test_lawyer_delete(self):
        self.client.login(username=self.lawyer.username, password=self.password)
        resp = self.client.delete(self.endpoint, json.dumps({}), content_type='application/json')
        self.assertEqual(resp.status_code, 405)  # not allowed


    def test_customer_cant(self):
        self.client.login(username=self.user.username, password=self.password)
        for event, status_code in [('get', 405), ('post', 403), ('patch', 403), ('delete', 403)]:
            resp = getattr(self.client, event)(self.endpoint, {}, content_type='application/json')
            self.assertEqual(resp.status_code, status_code)

    def test_anon_cant(self):
        for event in ['get', 'post', 'patch', 'delete']:
            resp = getattr(self.client, event)(self.endpoint, {}, content_type='application/json')
            self.assertEqual(resp.status_code, 401)  # denied
