# -*- coding: utf-8 -*-
from django.core import mail
from django.core.urlresolvers import reverse

from toolkit.core.item.models import Item

from . import BaseEndpointTest
from ...serializers import (ItemSerializer, UserSerializer,)


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

    def test_lawyer_get(self):
        self.client.login(username=self.lawyer.username, password=self.password)
        resp = self.client.get(self.endpoint)

        self.assertEqual(resp.status_code, 200)

        json_data = json.loads(resp.content)
        self.assertEqual(json_data['name'], self.item.name)
        # the user url is in the base
        # urls are different bcause the serializer here has no request object
        self.assertTrue(UserSerializer(self.user).data.get('url') in json_data['responsible_party'])

    def test_lawyer_post(self):
        self.client.login(username=self.lawyer.username, password=self.password)
        resp = self.client.post(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 405)  # not allowed

    def test_lawyer_patch(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        responsible_party_url = UserSerializer(self.user).data.get('url')

        data = {
            'email': 'new+user@lawpal.com',
            'first_name': 'Bob',
            'last_name': 'Da hoon',
            'message': 'Bob you are being added here please provide me with a monkey!',
        }

        resp = self.client.patch(self.endpoint, json.dumps(data), content_type='application/json')

        self.assertEqual(resp.status_code, 200)  # ok patch accepted
        json_data = json.loads(resp.content)

        new_item = Item.objects.awaiting_documents(matter=self.matter, slug=json_data['slug']).first()
        
        self.assertEqual(json_data['name'], new_item.name)

        # we shoudl have this new item in the standard item objects
        self.assertTrue(new_item in Item.objects.filter(matter=self.matter))

        outbox = mail.outbox
        self.assertEqual(len(outbox), 1)

        email = outbox[0]
        self.assertEqual(email.subject, u'[ACTION REQUIRED] Request to provide a document')
        self.assertEqual(email.recipients(), [u'new+user@lawpal.com'])


    def test_lawyer_delete(self):
        self.client.login(username=self.lawyer.username, password=self.password)
        resp = self.client.delete(self.endpoint, {})
        self.assertEqual(resp.status_code, 405)  # not allowed


    def test_customer_get(self):
        self.client.login(username=self.user.username, password=self.password)
        resp = self.client.get(self.endpoint)

        self.assertEqual(resp.status_code, 200)

        json_data = json.loads(resp.content)
        self.assertEqual(json_data['name'], self.item.name)
        # the user url is in the base
        # urls are different bcause the serializer here has no request object
        self.assertTrue(UserSerializer(self.user).data.get('url') in json_data['responsible_party'])

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
        self.assertEqual(resp.status_code, 401)  # denied

    def test_anon_post(self):
        resp = self.client.post(self.endpoint, {})
        self.assertEqual(resp.status_code, 401)  # denied

    def test_anon_patch(self):
        resp = self.client.patch(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 401)  # denied

    def test_anon_delete(self):
        resp = self.client.delete(self.endpoint, {})
        self.assertEqual(resp.status_code, 401)  # denied


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
        self.assertEqual(resp.status_code, 401)  # denied

    def test_anon_post(self):
        resp = self.client.post(self.endpoint, {})
        self.assertEqual(resp.status_code, 401)  # denied

    def test_anon_patch(self):
        resp = self.client.patch(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 401)  # denied

    def test_anon_delete(self):
        resp = self.client.delete(self.endpoint, {})
        self.assertEqual(resp.status_code, 401)  # denied
