# -*- coding: utf-8 -*-
from django.test import TestCase
from model_mommy import mommy

from toolkit.apps.default import _get_unique_username


class UniqueUsernameTest(TestCase):
    def setUp(self):
        super(UniqueUsernameTest, self).setUp()
        self.userA = mommy.make('auth.User', username='customerA', first_name='Customer', last_name='TestA', email='testA+customer@lawpal.com')

    def test__get_unique_username(self):
        self.assertEqual(_get_unique_username('unique-monkey-nuts'), 'unique-monkey-nuts')

    def test__get_unique_username_not_unique(self):
        self.assertNotEqual(_get_unique_username('customerA'), 'customerA')

