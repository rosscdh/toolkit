# -*- coding: utf-8 -*-
from actstream.models import Action
from django.core.urlresolvers import reverse

from . import BaseEndpointTest
from ...serializers import ClientSerializer, ItemActivitySerializer

from model_mommy import mommy

import json


class CommentTest(BaseEndpointTest):
    """
    /comment/ (POST)
        create comments

    (GET not needed, because comments are saved as actions)
    """
    def setUp(self):
        super(CommentTest, self).setUp()
        self.item = mommy.make('item.Item', matter=self.workspace, name='Comment Test Item #1')

    @property
    def endpoint(self):
        return reverse('item_comment', kwargs={'matter_slug': self.matter.slug, 'item_slug': self.item.slug})

    def test_endpoint_name(self):
        self.assertEqual(self.endpoint, '/api/v1/matters/%(matter_slug)s/items/%(item_slug)s/comment' % {
            'matter_slug': self.matter.slug,
            'item_slug': self.item.slug,
        })

    def test_empty_post(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        data = {
            "comment": ""
        }
        resp = self.client.post(self.endpoint, json.dumps(data), content_type='application/json')

        self.assertEqual(resp.status_code, 400)  # bad request

    def test_lawyer_post(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        data = {
            "comment": "The rain in spain, falls mainly on a monkey."
        }
        resp = self.client.post(self.endpoint, json.dumps(data), content_type='application/json')

        self.assertEqual(resp.status_code, 201)  # created

    def test_customer_post(self):
        self.client.login(username=self.user.username, password=self.password)

        data = {
            "comment": "The rain in spain, falls mainly on a monkey."
        }
        resp = self.client.post(self.endpoint, json.dumps(data), content_type='application/json')

        self.assertEqual(resp.status_code, 201)  # created

    def test_anon_post(self):
        data = {
            "comment": "The rain in spain, falls mainly on a monkey."
        }
        resp = self.client.post(self.endpoint, json.dumps(data), content_type='application/json')

        self.assertEqual(resp.status_code, 401)  # denied