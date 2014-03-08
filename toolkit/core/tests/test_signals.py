import json
from actstream.models import Action
from django.test import TestCase
from django.core.cache import cache
from django.dispatch import receiver
from model_mommy import mommy
from toolkit.api.serializers import ItemSerializer
from toolkit.casper import BaseScenarios
from toolkit.core.signals import send_activity_log


expected_keys = ['sender', 'signal', 'actor', 'verb', 'action_object', 'target', 'ip']
cache_key = 'activity_stream_signal_received_keys'


@receiver(send_activity_log)
def on_activity_received(**kwargs):
    """
    Test signal listener to handle the signal fired event
    """
    cache.set(cache_key, kwargs.keys())


"""
I left out the "simple" test if the signal gets received because the signal needs Model-objects to send them to
actstream, so I would need to create fake-models which lead to the same test as the scenario-test.
"""


class ActivitySignalTestCase(BaseScenarios, TestCase):
    def setUp(self):
        super(ActivitySignalTestCase, self).setUp()
        self.basic_workspace()

    def test_signal_received(self):
        """
        for now: DIRECTLY send the event to the signal

        TODO: as soon as signal is used (meaning: it got bound to certain events (object got modified, object got commented, ...))
                we should call these events instead of directly calling the signal.
                As it is now we just test django signals.
        """
        send_activity_log.send('somesender', **dict(
            actor=self.lawyer,
            verb=u'edited',
            action_object=self.eightythreeb,
            target=self.matter,
            ip='127.0.0.1'
        ))
        self.assertItemsEqual(cache.get(cache_key), expected_keys)
        cache.delete(cache_key)

    # copied from api-endpoints-test
    def test_lawyer_post(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        new_item = mommy.prepare('item.Item', matter=self.workspace, name='New Test Item No. 2')

        resp = self.client.post(self.endpoint, json.dumps(ItemSerializer(new_item).data), content_type='application/json')

        self.assertEqual(resp.status_code, 201)  # created

        json_data = json.loads(resp.content)
        self.assertEqual(json_data['name'], new_item.name)

    def test_item_created(self):
        # do API-request to create new item and afterwards check if the corresponding action got created
        self.test_lawyer_post()

        # missing part in API or item-model: send signal

        # TODO: get action and think of assertion
        # action = Action.objects.get(verb=u'created')
        # self.assertEqual(action.data['ip'], '127.0.0.1')