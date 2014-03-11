# -*- coding: utf-8 -*-
import json
from actstream.models import Action
from django.core.urlresolvers import reverse
from django.test import LiveServerTestCase
from model_mommy import mommy
from toolkit.api.tests import BaseEndpointTest

__author__ = 'Marius Burfey <marius.burfey@ambient-innovation.com> - 10.03.14'


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

        import pdb;pdb.set_trace()

        self.assertEqual(resp.status_code, 200)
        json_data = json.loads(resp.content)

        self.assertListEqual(json_data.keys(), [u'target_actions', u'name', u'closing_groups', u'date_modified', u'url', u'items', u'current_user', u'action_object_actions', u'comments', u'current_user_todo', u'participants', u'client', u'lawyer', u'activity', u'date_created', u'matter_code', u'slug', u'categories'])

