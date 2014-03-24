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
        new_user = mommy.make('auth.User', first_name='Customer', last_name='Test 2', email='test+customer+2@lawpal.com')



        self.matter.participants.add(new_user)
        self.matter.save()
        # does not call pre_save



        stream = action_object_stream(self.matter)
        import pdb;pdb.set_trace()