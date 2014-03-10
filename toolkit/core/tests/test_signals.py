# -*- coding: utf-8 -*-
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.dispatch import receiver

from model_mommy import mommy
from actstream.models import Action
from actstream.models import action_object_stream

from toolkit.casper import BaseScenarios
from toolkit.api.serializers import ItemSerializer
from toolkit.core.signals import send_activity_log

import json

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
        self.assertItemsEqual(cache_obj.keys(), ['sender', 'signal', 'actor', 'verb', 'action_object', 'target', 'ip'])
        self.assertItemsEqual(cache_obj.values(), ["<class 'django.db.models.base.ModelBase'>", '127.0.0.1', "<class 'django.dispatch.dispatcher.Signal'>", "<class 'django.contrib.auth.models.User'>", u'created', "<class 'toolkit.apps.workspace.models.Workspace'>", "<class 'toolkit.apps.workspace.models.Workspace'>"])
        cache.delete(cache_key)

    def test_stream_item_created_manually(self):
        workspace = mommy.make('workspace.Workspace', name='Action Created by Signal Workspace', lawyer=self.lawyer)
        stream = action_object_stream(workspace)
        self.assertEqual(len(stream), 1)

        stream_item = stream[0]
        self.assertEqual(stream_item.verb, 'created')
        self.assertEqual(stream_item.target, workspace)
        self.assertEqual(stream_item.actor, self.lawyer)
