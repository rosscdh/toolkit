# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse

from actstream.models import target_stream

from model_mommy import mommy

from toolkit.api.tests import BaseEndpointTest

import json


class MatterActivityEndpointTest(BaseEndpointTest):
    @property
    def endpoint(self):
        return reverse('matter_activity', kwargs={'matter_slug': self.matter.slug})

    def test_endpoint_name(self):
        self.assertEqual(self.endpoint, '/api/v1/matters/%s/activity' % self.matter.slug)

    def setUp(self):
        super(MatterActivityEndpointTest, self).setUp()
        # setup the items for testing
        self.item = mommy.make('item.Item', matter=self.matter, name='Test Item with Revision', category=None)
        self.revision = mommy.make('attachment.Revision', executed_file=None, slug=None, item=self.item, uploaded_by=self.lawyer)

    def test_activitystream_in_response_name(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        resp = self.client.get(self.endpoint)

        self.assertEqual(resp.status_code, 200)
        json_data = json.loads(resp.content)

        events = json_data['results']

        self.assertEqual(len(events), 3)  # create matter, create item, added participant; we dont record the participant add because participant add where the adding user is teh same as the added user is skipped
        self.assertGreater(len(events[0]['event']), 10)  # just to see if event-text contains information. username is not fix.
        #self.assertEqual(events[0]['event'], u'%s created 1 %s on %s' % (self.lawyer, self.item.slug, self.matter,))
        self.assertItemsEqual(events[0].keys(), [u'timestamp', u'timesince', u'data', u'id', u'actor', u'event'])

        # check if actor was added correctly
        self.assertEqual(events[0]['actor']['name'], u'Lawyer Test')


class ItemActivityEndpointTest(BaseEndpointTest):
    @property
    def endpoint(self):
        return reverse('item_activity', kwargs={'matter_slug': self.matter.slug, 'item_slug': self.item.slug})

    def test_endpoint_name(self):
        self.assertEqual(self.endpoint, '/api/v1/matters/%s/items/%s/activity' % (self.matter.slug, self.item.slug))

    def setUp(self):
        super(ItemActivityEndpointTest, self).setUp()
        # setup the items for testing
        self.item = mommy.make('item.Item', matter=self.matter, name='Test Item with Revision', category=None)
        self.revision = mommy.make('attachment.Revision', executed_file=None, slug=None, item=self.item, uploaded_by=self.lawyer)

    def test_activitystream_in_response_name(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        resp = self.client.get(self.endpoint)

        self.assertEqual(resp.status_code, 200)
        json_data = json.loads(resp.content)

        events = json_data['results']

        self.assertEqual(len(events), 1)  # we should have 1, the create of the item

    def test_comments_in_activitystream(self):
        # create comment and see if *special* template is used
        self.client.login(username=self.lawyer.username, password=self.password)

        mommy.make('actstream.Action',
                              actor=self.user,
                              verb=u'commented',
                              action_object=self.item,
                              target=self.matter,
                              data={'comment': u'I"m a test comment #1'})

        resp = self.client.get(self.endpoint)
        self.assertEqual(resp.status_code, 200)
        json_data = json.loads(resp.content)
        events = json_data['results']

        self.assertEqual(len(events), 2)

        event = events[0]['event']
        self.assertEqual(event[:18], '<div class="media"')