# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse

from .. import BaseEndpointTest
from ....serializers import ItemSerializer

from model_mommy import mommy

import json


class ItemsPermissionTest(BaseEndpointTest):
    """
    test workspace.manage_items permission
    """
    def setUp(self):
        super(ItemsPermissionTest, self).setUp()
        self.item = mommy.make('item.Item', matter=self.workspace, name='Test Item No. 1')

    @property
    def endpoint(self):
        return reverse('matter_items', kwargs={'matter_slug': self.workspace.slug})

    def test_endpoint_name(self):
        self.assertEqual(self.endpoint, '/api/v1/matters/lawpal-test/items')

    def test_lawyer_post(self):
        self.client.login(username=self.lawyer.username, password=self.password)
        new_item = mommy.prepare('item.Item', matter=self.workspace, name='New Test Item No. 2')

        self.set_user_permissions(self.lawyer, {'workspace.manage_items': False})
        resp = self.client.post(self.endpoint, json.dumps(ItemSerializer(new_item).data), content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

        self.set_user_permissions(self.lawyer, {'workspace.manage_items': True})
        resp = self.client.post(self.endpoint, json.dumps(ItemSerializer(new_item).data), content_type='application/json')
        self.assertEqual(resp.status_code, 202)  # created


class ItemDetailTest(BaseEndpointTest):
    """
    test workspace.manage_items permission
    """
    def setUp(self):
        super(ItemDetailTest, self).setUp()
        self.item = mommy.make('item.Item', matter=self.workspace, name='Test Item No. 1')

    @property
    def endpoint(self):
        return reverse('matter_item', kwargs={'matter_slug': self.workspace.slug, 'item_slug': self.item.slug})

    def test_endpoint_name(self):
        self.assertEqual(self.endpoint, '/api/v1/matters/lawpal-test/items/%s' % self.item.slug)

    def test_lawyer_patch(self):
        expected_name = 'Changed Name test'

        self.client.login(username=self.lawyer.username, password=self.password)

        self.set_user_permissions(self.lawyer, {'workspace.manage_items': False})
        resp = self.client.patch(self.endpoint, json.dumps({'name': expected_name}), content_type='application/json')
        self.assertEqual(resp.status_code, 403)

        self.set_user_permissions(self.lawyer, {'workspace.manage_items': True})
        resp = self.client.patch(self.endpoint, json.dumps({'name': expected_name}), content_type='application/json')
        self.assertEqual(resp.status_code, 200)

    def test_lawyer_delete(self):
        """
        Lawyers can delete items
        """
        self.client.login(username=self.lawyer.username, password=self.password)

        self.set_user_permissions(self.lawyer, {'workspace.manage_items': False})
        resp = self.client.delete(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

        self.set_user_permissions(self.lawyer, {'workspace.manage_items': True})
        resp = self.client.delete(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 204)  # no content but 2** success