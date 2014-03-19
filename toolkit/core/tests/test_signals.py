# -*- coding: utf-8 -*-
import datetime
from abridge.services.abridge_service import AbridgeService
from django.core.cache import cache
from django.test import TestCase
from django.dispatch import receiver

from model_mommy import mommy
from actstream.models import action_object_stream, Action, model_stream
import time

from toolkit.casper import BaseScenarios
from toolkit.casper.prettify import mock_http_requests
from toolkit.core.attachment.models import Revision
from toolkit.core.item.models import Item
from toolkit.core.services import MatterActivityEventService
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
        self.assertItemsEqual(cache_obj.keys(), ['sender', 'signal', 'actor', 'verb', 'action_object', 'target', 'item',
                                                 'user', 'message'])
        self.assertItemsEqual(cache_obj.values(), ["<class 'toolkit.core.services.MatterActivityEventService'>",
                                                   "<class 'django.dispatch.dispatcher.Signal'>",
                                                   "<class 'django.contrib.auth.models.User'>",
                                                   u'created',
                                                   "<class 'toolkit.apps.workspace.models.Workspace'>",
                                                   "<class 'toolkit.apps.workspace.models.Workspace'>",
                                                   "<type 'NoneType'>",
                                                   "<type 'NoneType'>",
                                                   "<type 'NoneType'>"])
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

    def test_revision_signals(self):
        """
        first create a revision and call the service which would be called from the api in reality.
        test, if stream entry was created
        """
        item = mommy.make('item.Item', name='Test Item #1', matter=self.workspace)
        revision1 = mommy.make('attachment.Revision', name='Test Revision #1', item=item, uploaded_by=self.user)
        MatterActivityEventService(self.matter).created_revision(user=self.user,
                                                                 item=item,
                                                                 revision=revision1)
        stream = model_stream(Revision)
        self.assertEqual(len(stream), 1)
        self.assertEqual(stream[0].action_object, revision1)
        self.assertEqual(stream[0].actor, self.user)

        """
        add a user as reviewer and check if it worked
        """
        reviewer = mommy.make('auth.User', username='test-reviewer', first_name='Customer', last_name='Test', email='testreviewer@lawpal.com')
        MatterActivityEventService(self.matter).added_user_as_reviewer(item, self.lawyer, reviewer)
        stream = model_stream(Item)
        self.assertEqual(len(stream), 2)  # first one was the creation
        self.assertEqual(stream[0].action_object, item)
        self.assertEqual(stream[0].actor, self.lawyer)
        self.assertEqual(stream[0].data['message'], u'Lawyer Test added Customer Test as reviewer for Test Item #1')

        """
        delete user as reviewer and check if it worked
        """
        MatterActivityEventService(self.matter).removed_user_as_reviewer(item, self.user, reviewer)
        stream = model_stream(Item)
        self.assertEqual(len(stream), 3)
        self.assertEqual(stream[0].action_object, item)
        self.assertEqual(stream[0].actor, self.user)
        self.assertEqual(stream[0].data['message'], u'Customer Test removed Customer Test as reviewer for Test Item #1')

        """
        remove revision again and check if it worked
        """
        MatterActivityEventService(self.matter).deleted_revision(self.lawyer, item, revision1)
        stream = model_stream(Revision)
        self.assertEqual(len(stream), 2)
        self.assertEqual(stream[0].action_object, revision1)
        self.assertEqual(stream[0].actor, self.lawyer)
        self.assertEqual(stream[0].data['message'], u'Lawyer Test destroyed a revision for Test Item #1')

    def test_customer_stream(self):
        # just for testing during development, only works because of hard set starting time in target_by_customer_stream
        workspace = mommy.make('workspace.Workspace', name='Action Created by Signal Workspace', lawyer=self.lawyer)
        mommy.make('item.Item', name='Test Item #1', matter=workspace)
        time.sleep(2)
        mommy.make('item.Item', name='Test Item #2', matter=workspace)

        stream = Action.objects.target_by_customer_stream(workspace, self.lawyer)
        self.assertEqual(len(stream), 1)  # shall only find the newest entry, the 2 other ones are too old.

    """
        TODO:
            test created_revision (via API)
            test deleted_revision (via API)
            test added_user_as_reviewer
            test removed_user_as_reviewer
    """
