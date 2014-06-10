# -*- coding: utf-8 -*-
from rest_framework.reverse import reverse

from toolkit.apps.workspace.models import Workspace

from . import BaseEndpointTest
#from ...serializers import ClientSerializer

from model_mommy import mommy

import json


class MatterCategoryTest(BaseEndpointTest):
    """
    Test that matter categories can be listed, created and deleted

    /matters/:matter_slug/category/:category (GET,POST,DELETE)
        [lawyer] can assign an item to a category
    """

    def setUp(self):
        super(MatterCategoryTest, self).setUp()

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

    def test_category_update(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        current_category = u'My Test Category with Mönchengladbach unicode'

        mommy.make('item.Item', matter=self.matter, name='Test Item: category change 1', category=current_category)
        mommy.make('item.Item', matter=self.matter, name='Test Item: category change 2', category=current_category)
        mommy.make('item.Item', matter=self.matter, name='Test Item: category change 3', category=current_category)

        # we have the items associatd with the current_category
        self.assertEqual(self.matter.item_set.filter(category=current_category).count(), 3)

        expected_category = u'Mönchengladbach vs Bayern'

        endpoint = reverse('matter_category', kwargs={"matter_slug": self.matter.slug, "category": current_category})

        # send a json PATCH request with data attaches
        data = {
            "category": expected_category
        }

        resp = self.client.patch(endpoint, json.dumps(data), content_type='application/json')
        resp_json = json.loads(resp.content)
        #
        # the new category should be present and not the old one
        #
        self.assertEqual(resp_json, [expected_category, "C", "B", "A"])
        self.assertTrue(current_category not in resp_json)
        self.assertEqual(self.matter.item_set.filter(category=current_category).count(), 0)
        self.assertEqual(self.matter.item_set.filter(category=expected_category).count(), 3)

    def test_category_delete(self):
        """
        Delete an existing Category
        """
        category_to_delete = u'My Test Category with Mönchengladbach unicode'
        # create an item which will now be deleted
        mommy.make('item.Item', matter=self.matter, name='Test Item No. 6', category=category_to_delete)
        mommy.make('item.Item', matter=self.matter, name='Test Item No. 7', category=category_to_delete)

        self.categories.insert(0, category_to_delete)
        self.matter.categories = self.categories
        self.matter.save(update_fields=['data'])

        # we have 7 items in the set
        self.assertEqual(self.matter.item_set.all().count(), 7)

        endpoint = reverse('matter_category', kwargs={"matter_slug": self.matter.slug, "category": category_to_delete})
        self.client.login(username=self.lawyer.username, password=self.password)

        # dont send any data
        # just the endpoint defines the category name to add list or delete
        resp = self.client.delete(endpoint, json.dumps({}), content_type='application/json')
        resp_json = json.loads(resp.content)

        # refresh
        self.matter = Workspace.objects.get(pk=self.matter.pk)

        #
        # Should be first in the list and present
        #
        self.assertEqual(resp_json, [u'A', u'B', u'C'])
        #
        # We should have 5 items now and not 6 because we just removed the
        # 2 category_to_delete items
        #
        self.assertEqual(self.matter.item_set.all().count(), 5)  # the item above that was created should be deleted
        self.assertEqual(self.matter.item_set.deleted().count(), 2) # we have 2 deleted items

    def test_item_category_create(self):
        """
        Can set an item category to a value and that value should then be added to the matter
        categories
        """
        item = self.items.first()  # pick an item to use
        item.category = u'Mönkey' # set a new category with unicode
        # save the new category
        item.save()

        self.assertEqual(item.matter.categories, [u'M\xf6nkey', 'C', 'B', 'A'])

    def test_item_category_delete(self):
        """
        Set an items category to None. When multipe items belong to the category
        we are deleting they.. the category should stay in place (can delete items
        and categories by DELETE to the matter/category/:cat_name endpoint)
        """
        self.assertEqual(self.matter.categories, ['C', 'B', 'A'])
        self.assertEqual(self.matter.item_set.all().count(), 5)

        item = self.matter.item_set.first()  # pick an item to use
        item.category = None # set to None
        # save the new category
        item.save()

        self.assertEqual(item.matter.categories, ['C', 'B', 'A'])
        # we should stil have 5
        self.assertEqual(item.matter.item_set.all().count(), 5)
        # that same first item is now category = None
        # either the first or the last must be done
        # for testing in sqlite its the last in postgres its the first
        self.assertTrue(any(i.category is None for i in [item.matter.item_set.all().order_by('-category').first(), item.matter.item_set.all().order_by('-category').last()]))
