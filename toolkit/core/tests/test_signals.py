import json
from actstream.models import Action
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.core.cache import cache
from django.dispatch import receiver
from model_mommy import mommy
from toolkit.api.serializers import ItemSerializer
from toolkit.casper import BaseScenarios
from toolkit.core.signals import send_activity_log


cache_key = 'activity_stream_signal_received_keys'


@receiver(send_activity_log)
def on_activity_received(**kwargs):
    """
    Test signal listener to handle the signal fired event
    """
    cache.set(cache_key, kwargs.keys())


class ActivitySignalTestCase(BaseScenarios, TestCase):

    def setUp(self):
        super(ActivitySignalTestCase, self).setUp()
        self.basic_workspace()
        self.test_lawyer_post_item = mommy.prepare('item.Item', matter=self.workspace, name='New Test Item for test_lawyer_post')

    def test_workspace_created_signal_received(self):
        # in setUp the workspace was created which should have reached on_activity_received above:
        self.assertItemsEqual(cache.get(cache_key), ['sender', 'signal', 'actor', 'verb', 'action_object', 'target', 'ip'])
        cache.delete(cache_key)

    def test_workspace_created_action_created(self):
        action = Action.objects.get(
            actor_content_type=ContentType.objects.get_for_model(self.lawyer),
            actor_object_id=self.lawyer.id,
            verb=u'created',
            action_object_content_type=ContentType.objects.get_for_model(self.workspace),
            action_object_object_id=self.workspace.id,
            target_content_type=ContentType.objects.get_for_model(self.workspace),
            target_object_id=self.workspace.id
        )
        self.assertEqual(action.data['ip'], '127.0.0.1')

    """
    TODO: as soon as signal is used (meaning: it got bound to certain events (object got modified, object got commented, ...))
            we should add tests for these usages.

            possibly similar to the following.
    """

    @property
    def endpoint(self):
        return reverse('matter_items', kwargs={'matter_slug': self.workspace.slug})

    # adapted from api-endpoints-test
    def test_lawyer_post(self):
        self.client.login(username=self.lawyer.username, password=self.password)
        self.client.post(self.endpoint, json.dumps(ItemSerializer(self.test_lawyer_post_item).data), content_type='application/json')

    def test_item_created(self):
        # do API-request to create new item and afterwards check if the corresponding action got created
        self.test_lawyer_post()

        # missing part in API or item-model: send signal

        try:
            action = Action.objects.get(
                actor_content_type=ContentType.objects.get_for_model(self.lawyer),
                actor_object_id=self.lawyer.id,
                verb=u'created',
                action_object_content_type=ContentType.objects.get_for_model(self.test_lawyer_post_item),
                action_object_object_id=self.test_lawyer_post_item.id,
                target_content_type=ContentType.objects.get_for_model(self.workspace),
                target_object_id=self.workspace.id
            )
        except Action.DoesNotExist:
            pass
        # self.assertEqual(action.data['ip'], '127.0.0.1')