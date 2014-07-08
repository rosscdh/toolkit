# -*- coding: utf-8 -*-
from actstream.models import model_stream
from rest_framework.reverse import reverse

from toolkit.core.item.models import Item

from . import BaseEndpointTest
from ...serializers import ItemSerializer

from model_mommy import mommy

import json


class ItemsTest(BaseEndpointTest):
    """
    /matters/:matter_slug/items/ (GET,POST)
        Allow the [lawyer,customer] user to list items that belong to them
    """
    def setUp(self):
        super(ItemsTest, self).setUp()
        self.item = mommy.make('item.Item', matter=self.workspace, name='Test Item No. 1')

    @property
    def endpoint(self):
        return reverse('matter_items', kwargs={'matter_slug': self.workspace.slug})

    def test_endpoint_name(self):
        self.assertEqual(self.endpoint, '/api/v1/matters/lawpal-test/items')

    def test_lawyer_get(self):
        self.client.login(username=self.lawyer.username, password=self.password)
        resp = self.client.get(self.endpoint)

        self.assertEqual(resp.status_code, 200)

        json_data = json.loads(resp.content)
        self.assertEqual(json_data['count'], 1)
        self.assertEqual(json_data['results'][0]['name'], self.item.name)

    def test_lawyer_post(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        new_item = mommy.prepare('item.Item', matter=self.workspace, name='New Test Item No. 2')

        resp = self.client.post(self.endpoint, json.dumps(ItemSerializer(new_item).data),
                                content_type='application/json')
        self.assertEqual(resp.status_code, 201)  # created

        json_data = json.loads(resp.content)
        self.assertEqual(json_data['name'], new_item.name)

    def test_lawyer_patch(self):
        self.client.login(username=self.lawyer.username, password=self.password)
        resp = self.client.patch(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 405)  # not allowed

    def test_lawyer_delete(self):
        self.client.login(username=self.lawyer.username, password=self.password)
        resp = self.client.delete(self.endpoint, {})
        self.assertEqual(resp.status_code, 405)  # not allowed


    def test_customer_get(self):
        self.client.login(username=self.user.username, password=self.password)
        resp = self.client.get(self.endpoint)

        self.assertEqual(resp.status_code, 200)

        json_data = json.loads(resp.content)
        self.assertEqual(json_data['count'], 1)
        self.assertEqual(json_data['results'][0]['name'], self.item.name)

    def test_customer_post(self):
        self.client.login(username=self.user.username, password=self.password)

        # for non-colleagues the permission is required to be allowed to create it.
        self.set_user_matter_perms(self.user, self.matter, manage_items=True)
        new_item = mommy.prepare('item.Item', matter=self.workspace, name='New Test Item No. 2')

        resp = self.client.post(self.endpoint, json.dumps(ItemSerializer(new_item).data),
                                content_type='application/json')
        self.assertEqual(resp.status_code, 201)

    def test_customer_patch(self):
        self.client.login(username=self.user.username, password=self.password)
        resp = self.client.patch(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden
        # (MatterItemsView.can_delete stops access BEFORE django-rest-framework stops it because of missing PATCH.

    def test_customer_delete(self):
        self.client.login(username=self.user.username, password=self.password)
        resp = self.client.delete(self.endpoint, {})
        self.assertEqual(resp.status_code, 403)  # forbidden
        # (MatterItemsView.can_delete stops access BEFORE django-rest-framework stops it because of missing DELETE.

    def test_anon_get(self):
        resp = self.client.get(self.endpoint)
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_anon_post(self):
        resp = self.client.post(self.endpoint, {})
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_anon_patch(self):
        resp = self.client.patch(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_anon_delete(self):
        resp = self.client.delete(self.endpoint, {})
        self.assertEqual(resp.status_code, 403)  # forbidden


class ItemDetailTest(BaseEndpointTest):
    """
    /matters/:matter_slug/items/:item_slug/ (GET,PATCH,DELETE)
        Allow the [lawyer,customer] user to list, and update an existing item
        objects; that belong to them
    """
    def setUp(self):
        super(ItemDetailTest, self).setUp()
        self.item = mommy.make('item.Item', matter=self.workspace, name='Test Item No. 1')

    @property
    def endpoint(self):
        return reverse('matter_item', kwargs={'matter_slug': self.workspace.slug, 'item_slug': self.item.slug})

    def test_endpoint_name(self):
        self.assertEqual(self.endpoint, '/api/v1/matters/lawpal-test/items/%s' % self.item.slug)

    def test_lawyer_get(self):
        self.client.login(username=self.lawyer.username, password=self.password)
        resp = self.client.get(self.endpoint)

        self.assertEqual(resp.status_code, 200)

        json_data = json.loads(resp.content)
        self.assertEqual(json_data['name'], self.item.name)

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
        Lawyers can delete items
        """
        self.client.login(username=self.lawyer.username, password=self.password)
        resp = self.client.delete(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 204)  # no content but 2** success

        deleted_items = Item.objects.deleted()
        self.assertEqual(len(deleted_items), 1)

        deleted_item = deleted_items[0]
        self.assertEqual(deleted_item.name, self.item.name)

    def test_customer_get(self):
        self.client.login(username=self.user.username, password=self.password)
        resp = self.client.get(self.endpoint)

        self.assertEqual(resp.status_code, 200)

        json_data = json.loads(resp.content)
        self.assertEqual(json_data['name'], self.item.name)

    def test_customer_post(self):
        self.client.login(username=self.user.username, password=self.password)
        resp = self.client.post(self.endpoint)
        self.assertEqual(resp.status_code, 403)

    def test_customer_patch(self):
        self.client.login(username=self.user.username, password=self.password)

        resp = self.client.patch(self.endpoint, json.dumps({}), content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_customer_delete(self):
        """
        Customers cannot delete items
        """
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
        resp = self.client.patch(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_anon_delete(self):
        resp = self.client.delete(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden


class ItemDataTest(BaseEndpointTest):
    """
    Test the various object attributes are as they should be
    """
    def setUp(self):
        super(ItemDataTest, self).setUp()
        # get the signal
        self.client.login(username=self.lawyer.username, password=self.password)
        self.item = self._api_create_item(matter=self.matter, name='Item Data Test No. 1')

    @property
    def endpoint(self):
        return reverse('matter_item', kwargs={'matter_slug': self.workspace.slug, 'item_slug': self.item.slug})

    def test_endpoint_name(self):
        self.assertEqual(self.endpoint, '/api/v1/matters/lawpal-test/items/%s' % self.item.slug)

    def test_default_status(self):
        self.assertEqual(self.item.status, Item.ITEM_STATUS.new)

    def test_json_details(self):
        self.client.login(username=self.user.username, password=self.password)
        resp = self.client.get(self.endpoint)

        json_data = json.loads(resp.content)

        # test status is correct
        self.assertEqual(type(json_data['status']), int)
        self.assertEqual(json_data['status'], 0)  # New == 0

    def test_change_status_signal(self):
        self.client.login(username=self.lawyer.username, password=self.password)
        resp = self.client.patch(self.endpoint, json.dumps({'status': 1}), content_type='application/json')
        self.assertEqual(resp.status_code, 200)

        stream = model_stream(Item)
        self.assertEqual(len(stream), 2)

        self.assertEqual(stream[0].data['override_message'],
                         u'Lawyër Tëst set Item Data Test No. 1 to Final')

    def test_change_name_signal(self):
        self.client.login(username=self.lawyer.username, password=self.password)
        resp = self.client.patch(self.endpoint, json.dumps({'name': 'New Name'}), content_type='application/json')
        self.assertEqual(resp.status_code, 200)

        stream = model_stream(Item)
        self.assertEqual(len(stream), 2)

        self.assertEqual(stream[0].data['override_message'],
                         u'Lawyër Tëst renamed Item Data Test No. 1 to New Name')

    def test_item_reopened_signal(self):
        self.client.login(username=self.lawyer.username, password=self.password)
        resp = self.client.patch(self.endpoint, json.dumps({'is_complete': 'true'}), content_type='application/json')
        self.assertEqual(resp.status_code, 200)

        stream = model_stream(Item)
        self.assertEqual(len(stream), 2)  # shall only find the newest entry, the 2 other ones are too old.

        self.assertEqual(stream[0].data['override_message'], u'Lawyër Tëst closed Item Data Test No. 1')

        resp = self.client.patch(self.endpoint, json.dumps({'is_complete': 'false'}), content_type='application/json')
        self.assertEqual(resp.status_code, 200)

        stream = model_stream(Item)
        self.assertEqual(len(stream), 3)

        self.assertEqual(stream[0].data['override_message'], 'Lawyër Tëst reopened Item Data Test No. 1')