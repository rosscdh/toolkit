# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse

from toolkit.core.item.models import Item

from .. import BaseEndpointTest

from model_mommy import mommy

import json


class ItemsRequestDocumentTest(BaseEndpointTest):
    """
    /matters/:matter_slug/items/ (GET,POST)
        Allow the [lawyer,customer] user to list items that belong to them
    """
    def setUp(self):
        super(ItemsRequestDocumentTest, self).setUp()
        self.item = mommy.make('item.Item',
                                matter=self.workspace,
                                name='Test Item No. 1', # test that "(Requested document)" get appended
                                responsible_party=self.user,
                                status=Item.ITEM_STATUS.new)

    @property
    def endpoint(self):
        return reverse('matter_item_request_doc', kwargs={'matter_slug': self.matter.slug, 'item_slug': self.item.slug})

    def test_endpoint_name(self):
        self.assertEqual(self.endpoint, '/api/v1/matters/lawpal-test/items/%s/request_document' % self.item.slug)

    def test_lawyer_post(self):
        self.client.login(username=self.lawyer.username, password=self.password)
        resp = self.client.post(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 405)  # not allowed

    def test_lawyer_patch(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        data = {
            'email': 'new+user@lawpal.com',
            'first_name': 'Bob',
            'last_name': 'Da hoon',
            'message': 'Bob you are being added here please provide me with a monkey!',
        }

        self.set_user_matter_perms(user=self.lawyer, manage_document_reviews=False)
        resp = self.client.patch(self.endpoint, json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

        self.set_user_matter_perms(user=self.lawyer, manage_document_reviews=True)
        resp = self.client.patch(self.endpoint, json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 200)  # ok patch accepted


class ItemsRequestDocumentReminderTest(BaseEndpointTest):
    """
    /matters/:matter_slug/request_document/remind/ (POST)
        Allow the [lawyer,customer] user to list items that belong to them
    """
    def setUp(self):
        super(ItemsRequestDocumentReminderTest, self).setUp()
        self.item = mommy.make('item.Item',
                                matter=self.workspace,
                                name='Test Item No. 1', # test that "(Requested document)" get appended
                                responsible_party=self.user,
                                is_requested=True,
                                status=Item.ITEM_STATUS.new)

    @property
    def endpoint(self):
        return reverse('revision_request_document_reminder', kwargs={'matter_slug': self.matter.slug, 'item_slug': self.item.slug})

    def test_endpoint_name(self):
        self.assertEqual(self.endpoint, '/api/v1/matters/%s/items/%s/request_document/remind' % (self.matter.slug, self.item.slug))

    def test_lawyer_post(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        self.set_user_matter_perms(user=self.lawyer, manage_document_reviews=False)
        resp = self.client.post(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

        self.set_user_matter_perms(user=self.lawyer, manage_document_reviews=True)
        resp = self.client.post(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 202)  # accepted
