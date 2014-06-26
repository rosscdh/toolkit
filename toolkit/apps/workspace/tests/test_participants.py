# -*- coding: utf-8 -*-
from django.test import TestCase

from model_mommy import mommy

from toolkit.casper import BaseScenarios

from toolkit.api.serializers import LiteUserSerializer


class MatterParticipantsCacheTest(BaseScenarios, TestCase):
    """
    Test that when we add and remove a participant to the matter, they get added to the
    matter cache
    """
    def setUp(self):
        super(MatterParticipantsCacheTest, self).setUp()
        self.basic_workspace()
        self.user_to_add = mommy.make('auth.User', first_name='Billy', last_name='Goat', username='billy-goat',
                                      email='billy-goat@example.com')
        self.matter.add_participant(user=self.user_to_add)

        self.assertEqual(self.matter.participants.all().count(), 3)

        self.expected_participants = [LiteUserSerializer(p, context={'matter': self.matter}).data for p in self.matter.participants.all()]

    def test_participant_added(self):
        matter_data = self.matter.data
        self.assertTrue('participants' in matter_data.keys())

        self.assertEqual(len(matter_data.get('participants')), 3)

        expected_usernames = [p.get('username') for p in matter_data.get('participants')]
        # ensure that our user_to_add is NOT present in the new set
        self.assertTrue(self.user_to_add.username in expected_usernames)

    def test_participant_removed(self):
        self.matter.remove_participant(user=self.user_to_add)
        self.matter = self.matter.__class__.objects.get(pk=self.matter.pk)

        matter_data = self.matter.data
        self.assertTrue('participants' in matter_data.keys())
        #self.assertEqual(matter_data.get('participants'))
        self.assertEqual(len(matter_data.get('participants')), 2)

        expected_usernames = [p.get('username') for p in matter_data.get('participants')]
        # ensure that our user_to_add is NOT present in the new set
        self.assertTrue(self.user_to_add.username not in expected_usernames)
