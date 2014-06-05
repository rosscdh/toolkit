# -*- coding: utf-8 -*-
from django.template import loader
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType

from actstream.models import Action

from model_mommy import mommy

from toolkit.api.tests import BaseEndpointTest
from toolkit.api.serializers import ItemSerializer

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
        self.item = self._api_create_item(matter=self.matter, name='Test Item with Revision', category=None)
        self.revision = mommy.make('attachment.Revision', executed_file=None, slug=None, item=self.item, uploaded_by=self.lawyer)

    def test_activitystream_in_response_name(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        resp = self.client.get(self.endpoint)

        self.assertEqual(resp.status_code, 200)
        json_data = json.loads(resp.content)

        events = json_data['results']

        self.assertEqual(len(events), 2)  # create matter, create item
        self.assertGreater(len(events[0]['event']), 10)  # just to see if event-text contains information. username is not fix.

        stream_event = Action.objects.filter(action_object_object_id=self.item.id,
                                             action_object_content_type=ContentType.objects.get_for_model(self.item))\
            .first()

        t = loader.get_template('activity/default.html')
        ctx = loader.Context({'message': u'%s created %s' % (self.lawyer, self.item.name),
                              'timesince': stream_event.timesince})

        rendered = t.render(ctx)

        self.assertEqual(rendered, events[0].get('event'))

        self.assertItemsEqual(events[0].keys(),
                              [u'timestamp', u'id', u'event', u'type', u'username'])


class ItemActivityEndpointTest(BaseEndpointTest):
    @property
    def endpoint(self):
        return reverse('item_activity', kwargs={'matter_slug': self.matter.slug, 'item_slug': self.item.slug})

    def test_endpoint_name(self):
        self.assertEqual(self.endpoint, '/api/v1/matters/%s/items/%s/activity' % (self.matter.slug, self.item.slug))

    def setUp(self):
        super(ItemActivityEndpointTest, self).setUp()
        # setup the items for testing
        self.item = self._api_create_item(matter=self.matter, name='Test Item with Revision', category=None)

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
        self.assertEqual(event[:18], '<div class="commen')