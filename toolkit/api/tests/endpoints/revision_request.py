# -*- coding: utf-8 -*-
from django.core import mail
from django.test.client import RequestFactory
from actstream.models import action_object_stream, target_stream

from toolkit.core.item.models import Item

from . import BaseEndpointTest
from ...serializers import ItemSerializer

from model_mommy import mommy
from rest_framework.reverse import reverse

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

    def test_lawyer_get(self):
        self.client.login(username=self.lawyer.username, password=self.password)
        resp = self.client.get(self.endpoint)

        self.assertEqual(resp.status_code, 200)
        serializer = ItemSerializer(
            self.item,
            context={'request': RequestFactory().get(self.endpoint)}
        )
        self.assertEqual(serializer.data, resp.data)

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

        resp = self.client.patch(self.endpoint, json.dumps(data), content_type='application/json')

        self.assertEqual(resp.status_code, 200)  # ok patch accepted
        json_data = json.loads(resp.content)

        new_item = Item.objects.requested(matter=self.matter, slug=json_data['slug']).first()

        self.assertEqual(json_data['name'], new_item.name)

        # we should have this new item in the standard item objects
        self.assertTrue(new_item in Item.objects.filter(matter=self.matter))

        outbox = mail.outbox
        self.assertEqual(len(outbox), 1)

        email = outbox[0]
        self.assertEqual(email.subject, u'[ACTION REQUIRED] Request to provide a document')
        self.assertEqual(email.recipients(), [u'new+user@lawpal.com'])
        # test the custom message is present
        self.assertTrue(data.get('message') in email.body)

        # this should have created a new revision upload invite
        stream = action_object_stream(self.item)
        self.assertEqual(stream[0].data['override_message'],
                         u'Lawyër Tëst requested a file from Bob Da hoon for Test Item No. 1')

        # now we patch again to remove the revision_request and see if the activity is created
        data = {
            'is_requested': False,
            'responsible_party': None
        }
        self.client.patch(self.endpoint, json.dumps(data), content_type='application/json')
        stream = target_stream(self.matter)
        self.assertEqual(stream[0].data['override_message'],
                         u'Lawyër Tëst canceled their request for Bob Da hoon to provide a document on Test Item No. 1')

    def test_lawyer_delete(self):
        self.client.login(username=self.lawyer.username, password=self.password)
        resp = self.client.delete(self.endpoint, {})
        self.assertEqual(resp.status_code, 405)  # not allowed


    def test_customer_get(self):
        self.client.login(username=self.user.username, password=self.password)
        resp = self.client.get(self.endpoint)

        self.assertEqual(resp.status_code, 200)
        serializer = ItemSerializer(
            self.item,
            context={'request': RequestFactory().get(self.endpoint)}
        )
        self.assertEqual(serializer.data, resp.data)

    def test_customer_post(self):
        self.client.login(username=self.user.username, password=self.password)
        resp = self.client.post(self.endpoint)
        self.assertEqual(resp.status_code, 403)

    def test_customer_patch(self):
        self.client.login(username=self.user.username, password=self.password)
        resp = self.client.patch(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # method forbidden

    def test_customer_delete(self):
        self.client.login(username=self.user.username, password=self.password)
        resp = self.client.delete(self.endpoint, {})
        self.assertEqual(resp.status_code, 403)  # method forbidden

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

    def test_lawyer_get(self):
        self.client.login(username=self.lawyer.username, password=self.password)
        resp = self.client.get(self.endpoint)
        self.assertEqual(resp.status_code, 405)

    def test_lawyer_post(self):
        self.client.login(username=self.lawyer.username, password=self.password)
        resp = self.client.post(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 202)  # accepted

        outbox = mail.outbox
        self.assertEqual(len(outbox), 1)

        email = outbox[0]
        self.assertEqual(email.subject, u'[REMINDER] Please provide a document')
        self.assertEqual(email.recipients(), [u'test+customer@lawpal.com'])

    def test_lawyer_patch(self):
        self.client.login(username=self.lawyer.username, password=self.password)
        resp = self.client.patch(self.endpoint, {}, content_type='application/json')

        self.assertEqual(resp.status_code, 405)  # method not allowed

    def test_lawyer_delete(self):
        self.client.login(username=self.lawyer.username, password=self.password)
        resp = self.client.delete(self.endpoint, {})
        self.assertEqual(resp.status_code, 405)  # not allowed


    def test_customer_get(self):
        self.client.login(username=self.user.username, password=self.password)
        resp = self.client.get(self.endpoint)

        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_customer_post(self):
        self.client.login(username=self.user.username, password=self.password)
        resp = self.client.post(self.endpoint)
        self.assertEqual(resp.status_code, 403)

    def test_customer_patch(self):
        self.client.login(username=self.user.username, password=self.password)
        resp = self.client.patch(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # method forbidden

    def test_customer_delete(self):
        self.client.login(username=self.user.username, password=self.password)
        resp = self.client.delete(self.endpoint, {})
        self.assertEqual(resp.status_code, 403)  # method forbidden

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
