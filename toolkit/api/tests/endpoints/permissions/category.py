# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse

from toolkit.apps.workspace.models import Workspace

from . import BaseEndpointTest
#from ...serializers import ClientSerializer

from model_mommy import mommy

import json


class MatterCategoryPermissionTest(BaseEndpointTest):
    """
    Test that matter categories can be listed, created and deleted

    /matters/:matter_slug/category/:category (GET,POST,DELETE)
        [lawyer] can assign an item to a category
    """

    def setUp(self):
        super(MatterCategoryPermissionTest, self).setUp()

        # setup the items for testing
        mommy.make('item.Item', matter=self.matter, name='Test Item No. 1', category="A")
        mommy.make('item.Item', matter=self.matter, name='Test Item No. 2', category="A")
        mommy.make('item.Item', matter=self.matter, name='Test Item No. 3', category="B")
        mommy.make('item.Item', matter=self.matter, name='Test Item No. 4', category="C")
        mommy.make('item.Item', matter=self.matter, name='Test Item No. 5', category=None)

        self.items = self.matter.item_set.all()
        self.categories = ["A", "B", "C"]

    def test_endpoint_name(self):
        """
        No endpoint to test here as the category is the endpoint
        """
        self.skipTest("No endpoint to test here as the category is the endpoint")

    def test_category_create(self):
        """
        Create a new Category
        """
        expected_category = u'My Test Category with Mönchengladbach unicode'
        endpoint = reverse('matter_category', kwargs={"matter_slug": self.matter.slug, "category": expected_category})
        self.client.login(username=self.lawyer.username, password=self.password)
        # dont send any data
        # just the endpoint defines the category name to add list or delete
        resp = self.client.post(endpoint, json.dumps({}), content_type='application/json')
        resp_json = json.loads(resp.content)
        self.assertEqual(resp_json, [expected_category, "C", "B", "A"])