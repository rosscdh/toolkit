# -*- coding: utf-8 -*-
from django.test import TestCase
from model_mommy import mommy
from actstream.models import action_object_stream
from toolkit.casper import BaseScenarios


class WorkspaceSignalTest(BaseScenarios, TestCase):
    def setUp(self):
        super(WorkspaceSignalTest, self).setUp()
        self.basic_workspace()

    def test_add_participants(self):
        stream = action_object_stream(self.matter)
        self.assertEqual(stream[0].data['message'], u'Lawyer Test added Lawyer Test as a participant of Lawpal (test)')
        self.assertEqual(stream[1].data['message'], u'Lawyer Test added Customer Test as a participant of Lawpal (test)')