# -*- coding: utf-8 -*-
from django.core.cache import cache
from django.test import TestCase
from django.dispatch import receiver

import time
from model_mommy import mommy
from actstream.models import action_object_stream, model_stream

from toolkit.casper import BaseScenarios
from toolkit.core.attachment.models import Revision
from toolkit.core.item.models import Item

from toolkit.core.signals.activity_listener import send_activity_log

expected_cache_keys = {
    'workspace-created': ["<type 'NoneType'>", u'workspace-created', "<type 'NoneType'>",
                          "<class 'toolkit.core.services.matter_activity.MatterActivityEventService'>",
                          "<class 'django.dispatch.dispatcher.Signal'>",
                          "<type 'NoneType'>",
                          "<class 'django.contrib.auth.models.User'>",
                          "<type 'NoneType'>",
                          "<type 'NoneType'>",
                          u'created',
                          "<type 'NoneType'>",
                          "<type 'NoneType'>",
                          "<class 'toolkit.apps.workspace.models.Workspace'>",
                          "<type 'NoneType'>",
                          "<type 'NoneType'>",
                          "<type 'NoneType'>",
                          "<type 'NoneType'>",
                          "<class 'toolkit.apps.workspace.models.Workspace'>"],
    'workspace-added-participant': ["<type 'NoneType'>",
                                    u'workspace-added-participant',
                                    u'Lawyër Tëst added a new member to Lawpal (test)',
                                    "<class 'toolkit.core.services.matter_activity.MatterActivityEventService'>",
                                    "<class 'django.dispatch.dispatcher.Signal'>",
                                    "<type 'NoneType'>",
                                    "<class 'django.contrib.auth.models.User'>",
                                    "<type 'NoneType'>",
                                    "<type 'NoneType'>",
                                    u'added participant',
                                    "<class 'rest_framework.serializers.SortedDictWithMetadata'>",
                                    "<type 'NoneType'>",
                                    "<class 'toolkit.apps.workspace.models.Workspace'>",
                                    "<type 'NoneType'>",
                                    "<type 'NoneType'>",
                                    "<type 'NoneType'>",
                                    "<type 'NoneType'>",
                                    "<class 'toolkit.apps.workspace.models.Workspace'>"],
    'item-created': ["<type 'NoneType'>",
                     u'item-created',
                     "<type 'NoneType'>",
                     "<class 'toolkit.core.services.matter_activity.MatterActivityEventService'>",
                     "<class 'django.dispatch.dispatcher.Signal'>",
                     "<type 'NoneType'>",
                     "<class 'django.contrib.auth.models.User'>",
                     "<type 'NoneType'>",
                     "<type 'NoneType'>",
                     u'created',
                     "<type 'NoneType'>",
                     "<type 'NoneType'>",
                     "<class 'toolkit.core.item.models.Item'>",
                     "<type 'NoneType'>",
                     "<type 'NoneType'>",
                     "<type 'NoneType'>",
                     "<type 'NoneType'>",
                     "<class 'toolkit.apps.workspace.models.Workspace'>"],
    'item-commented': [u'Sleep with one eye open',
                       u'item-commented',
                       u'Lawyër Tëst commented on Test Item #1 "Sleep with one eye open"',
                       "<class 'toolkit.core.services.matter_activity.MatterActivityEventService'>",
                       "<class 'django.dispatch.dispatcher.Signal'>",
                       "<type 'NoneType'>",
                       "<class 'django.contrib.auth.models.User'>",
                       "<type 'NoneType'>",
                       "<type 'NoneType'>",
                       u'commented',
                       "<type 'NoneType'>",
                       "<type 'NoneType'>",
                       "<class 'toolkit.core.item.models.Item'>",
                       "<type 'NoneType'>",
                       "<type 'NoneType'>",
                       "<type 'NoneType'>",
                       "<type 'NoneType'>",
                       "<class 'toolkit.apps.workspace.models.Workspace'>"],
}

@receiver(send_activity_log)
def on_activity_received(**kwargs):
    """
    Test signal listener to handle the signal fired event
    """
    cache_key = kwargs.get('verb_slug')
    for i in kwargs:
        if type(kwargs[i]) not in [str, unicode, ]:
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
        for cache_key in expected_cache_keys.keys():
            # in setUp the workspace was created which should have reached on_activity_received above:
            cache_obj = cache.get(cache_key)

            self.assertItemsEqual(cache_obj.keys(), ['sender', 'signal', 'actor', 'verb', 'verb_slug', 'action_object',
                                                     'target', 'item', 'user', 'override_message', 'comment',
                                                     'previous_name', 'current_status', 'previous_status', 'filename',
                                                     'date_created', 'version', 'message'])
            #print '%s has these values: %s' % (cache_key, cache_obj.values())
            self.assertItemsEqual(cache_obj.values(), expected_cache_keys[cache_key])
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

    def test_item_renamed(self):
        item = mommy.make('item.Item', name='Test Item #1', matter=self.workspace)
        item.name = 'New Name'
        item.save()
        stream = action_object_stream(item)
        self.assertEqual(len(stream), 2)
        stream_item = stream[0]
        self.assertEqual(stream_item.verb, 'renamed')
        self.assertEqual(stream_item.target, self.workspace)
        self.assertEqual(stream_item.action_object, item)
        self.assertEqual(stream_item.actor, self.lawyer)
        self.assertEqual(stream_item.data['override_message'],
                         u'Lawyër Tëst renamed Test Item #1 to New Name')

    def test_item_status_changed(self):
        item = mommy.make('item.Item', name='Test Item #1', matter=self.workspace)
        item.status = 2
        item.save()
        stream = action_object_stream(item)
        self.assertEqual(len(stream), 2)
        stream_item = stream[0]
        self.assertEqual(stream_item.verb, 'changed the status')
        self.assertEqual(stream_item.target, self.workspace)
        self.assertEqual(stream_item.action_object, item)
        self.assertEqual(stream_item.actor, self.lawyer)
        self.assertEqual(stream_item.data['override_message'],
                         u'Lawyër Tëst set Test Item #1 to Executed')

    def test_revision_signals(self):
        """
        first create a revision and call the service which would be called from the api in reality.
        test, if stream entry was created
        """
        item = mommy.make('item.Item', name='Test Item #1', matter=self.workspace)
        revision1 = mommy.make('attachment.Revision', name='Test Revision #1', item=item, uploaded_by=self.user)
        self.matter.actions.created_revision(user=self.user,
                                             item=item,
                                             revision=revision1)
        stream = model_stream(Revision)
        self.assertEqual(len(stream), 1)
        self.assertEqual(stream[0].action_object, revision1)
        self.assertEqual(stream[0].actor, self.user)

        """
        add a user as reviewer and check if it worked
        """
        reviewer = mommy.make('auth.User', username='test-reviewer', first_name='Customër', last_name='Tëst', email='testreviewer@lawpal.com')
        self.matter.actions.invite_user_as_reviewer(item, self.lawyer, reviewer)
        stream = model_stream(Item)
        self.assertEqual(len(stream), 2)  # first one was the creation
        self.assertEqual(stream[0].action_object, item)
        self.assertEqual(stream[0].actor, self.lawyer)
        self.assertEqual(stream[0].data['override_message'],
                         u'Lawyër Tëst invited Customër Tëst to review Revision v1 of Test Item #1')

        """
        delete user as reviewer and check if it worked
        """
        self.matter.actions.cancel_user_upload_revision_request(item, self.user, reviewer)
        stream = model_stream(Item)
        self.assertEqual(len(stream), 3)
        self.assertEqual(stream[0].action_object, item)
        self.assertEqual(stream[0].actor, self.user)
        self.assertEqual(stream[0].data['override_message'],
                         u'Customër Tëst canceled their request for Customër Tëst to provide a document on Test Item #1')

        """
        remove revision again and check if it worked
        """
        self.matter.actions.deleted_revision(self.lawyer, item, revision1)
        stream = model_stream(Revision)
        self.assertEqual(len(stream), 2)
        self.assertEqual(stream[0].action_object, revision1)
        self.assertEqual(stream[0].actor, self.lawyer)
        self.assertEqual(stream[0].data['override_message'], u'Lawyër Tëst destroyed a revision for Test Item #1')

    def test_add_comment(self):
        item = mommy.make('item.Item', name='Test Item #1', matter=self.matter)
        comment_text = u'Sleep with one eye open'

        self.matter.actions.add_item_comment(self.lawyer, item, comment_text)

        stream = model_stream(Item)
        self.assertEqual(len(stream), 2)  # create item, and add comment -> 2
        self.assertEqual(stream[0].data['comment'], comment_text)

    def test_customer_stream(self):
        from actstream.models import Action
        # just for testing during development, only works because of hard set starting time in target_by_customer_stream
        workspace = mommy.make('workspace.Workspace', name='Action Created by Signal Workspace', lawyer=self.lawyer)
        mommy.make('item.Item', name='Test Item #1', matter=workspace)
        time.sleep(2)
        mommy.make('item.Item', name='Test Item #2', matter=workspace)

        stream = Action.objects.target_by_customer_stream(workspace, self.lawyer)
        self.assertEqual(len(stream), 1)  # shall only find the newest entry, the 2 other ones are too old.