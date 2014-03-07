from django.test import TestCase
from .models import ActivityTester
from toolkit.core.signals import send_activity_log


class ActivitySignalTestCase(TestCase):
    def setUp(self):
        # create user, action_object and target
        ActivityTester.objects.create(name='actor', type=1)
        ActivityTester.objects.create(name='letter', type=2)
        ActivityTester.objects.create(name='workspace', type=3)

    def test_activity(self):
        actor = ActivityTester.objects.get(type=1)
        verb = u'edited'
        letter = ActivityTester.objects.get(type=2)
        workspace = ActivityTester.objects.get(type=3)
        ip = '127.0.0.1'

        information_to_send = dict(
            actor=actor,
            verb=verb,
            action_object=letter,
            target=workspace,
            ip=ip
        )

        send_activity_log.send("somesender", **information_to_send)

        # If I import it on top the test won't run. Any clues?
        from actstream.models import Action

        # generic relation lookup not working, but database is empty anyway
        action = Action.objects.get(actor=actor, verb=verb, action_object=letter, target=workspace)
        self.assertEqual(action.data['ip'], ip)