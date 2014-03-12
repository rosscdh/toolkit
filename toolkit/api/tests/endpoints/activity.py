# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.test import LiveServerTestCase

from model_mommy import mommy
from actstream.models import Action

from toolkit.api.tests import BaseEndpointTest

import json


class ActivityStreamGetActionTest(BaseEndpointTest, LiveServerTestCase):
    @property
    def endpoint(self):
        return reverse('matter_activity', kwargs={'matter_slug': self.matter.slug})

    def test_endpoint_name(self):
        self.assertEqual(self.endpoint, '/api/v1/matters/%s/activity' % self.matter.slug)

    def setUp(self):
        super(ActivityStreamGetActionTest, self).setUp()
        # setup the items for testing
        self.item = mommy.make('item.Item', matter=self.matter, name='Test Item with Revision', category=None)
        revision = mommy.make('attachment.Revision', executed_file=None, slug=None, item=self.item, uploaded_by=self.lawyer)

    def test_activitystream_in_response_name(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        resp = self.client.get(self.endpoint)

        self.assertEqual(resp.status_code, 200)
        json_data = json.loads(resp.content)

        events = json_data['results']

        self.assertEqual(len(events), 3)
        self.assertGreater(len(events[0]['event']), 10)  # just to see if event-text contains information. username is not fix.
        self.assertListEqual(events[0].keys(), [u'data', u'id', u'event'])