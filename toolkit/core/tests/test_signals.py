# -*- coding: utf-8 -*-
import datetime
from django.core.cache import cache
from django.test import TestCase
from django.dispatch import receiver

from model_mommy import mommy
from actstream.models import action_object_stream, Action, model_stream
import time

from toolkit.casper import BaseScenarios
from toolkit.core.attachment.models import Revision
from toolkit.core.signals import send_activity_log

cache_key = 'activity_stream_signal_received_keys'


@receiver(send_activity_log)
def on_activity_received(**kwargs):
    """
    Test signal listener to handle the signal fired event
    """
    for i in kwargs:
        if type(kwargs[i]) not in [str, unicode,]:
            kwargs[i] = str(type(kwargs[i]))

    cache.set(cache_key, kwargs)


class ActivitySignalTest(BaseScenarios, TestCase):

    def setUp(self):
        super(ActivitySignalTest, self).setUp()
        self.basic_workspace()

    def test_workspace_created_signal_received_on_basic_workspace(self):
        """
        Created by the self.basic_workspace() call
        """
        # in setUp the workspace was created which should have reached on_activity_received above:
        cache_obj = cache.get(cache_key)
        self.assertItemsEqual(cache_obj.keys(), ['sender', 'signal', 'actor', 'verb', 'action_object', 'target'])
        self.assertItemsEqual(cache_obj.values(), ["<class 'django.db.models.base.ModelBase'>", "<class 'django.dispatch.dispatcher.Signal'>", "<class 'django.contrib.auth.models.User'>", u'created', "<class 'toolkit.apps.workspace.models.Workspace'>", "<class 'toolkit.apps.workspace.models.Workspace'>"])
        cache.delete(cache_key)

    def test_stream_item_created_manually(self):
        workspace = mommy.make('workspace.Workspace', name='Action Created by Signal Workspace', lawyer=self.lawyer)
        stream = action_object_stream(workspace)
        self.assertEqual(len(stream), 1)

        stream_item = stream[0]
        self.assertEqual(stream_item.verb, 'created')
        self.assertEqual(stream_item.target, workspace)
        self.assertEqual(stream_item.actor, self.lawyer)

    def test_item_created(self):
        item = mommy.make('item.Item', name='Test Item #1', matter=self.workspace)
        stream = action_object_stream(item)
        self.assertEqual(len(stream), 1)

        stream_item = stream[0]
        self.assertEqual(stream_item.verb, 'created')
        self.assertEqual(stream_item.target, self.workspace)
        self.assertEqual(stream_item.action_object, item)
        self.assertEqual(stream_item.actor, self.lawyer)

    def test_revision_created(self):
        """
        create item and two revisions.
        then check, if objects of class Revision were created and if they belong to revision.
        """
        item = mommy.make('item.Item', name='Test Item #1', matter=self.workspace)
        revision1 = mommy.make('attachment.Revision', name='Test Revision #1', item=item, uploaded_by=self.user)
        revision2 = mommy.make('attachment.Revision', name='Test Revision #2', item=item, uploaded_by=self.user)
        stream = model_stream(Revision)
        self.assertEqual(len(stream), 2)

        stream_item = stream[0]
        self.assertEqual(stream_item.verb, 'created')
        self.assertEqual(stream_item.action_object, revision2)
        self.assertEqual(stream_item.actor, self.user)

        stream_item = stream[1]
        self.assertEqual(stream_item.verb, 'created')
        self.assertEqual(stream_item.action_object, revision1)
        self.assertEqual(stream_item.actor, self.user)

    def test_customer_stream(self):
        # just for testing during development, only works because of hard set starting time in target_by_customer_stream
        workspace = mommy.make('workspace.Workspace', name='Action Created by Signal Workspace', lawyer=self.lawyer)
        mommy.make('item.Item', name='Test Item #1', matter=workspace)
        time.sleep(2)
        mommy.make('item.Item', name='Test Item #2', matter=workspace)

        stream = Action.objects.target_by_customer_stream(workspace, self.lawyer)
        self.assertEqual(len(stream), 1)  # shall only find the newest entry, the 2 other ones are too old.