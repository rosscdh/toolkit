# -*- coding: utf-8 -*-
from django.test import TestCase
from model_mommy import mommy

from toolkit.apps.default import _get_unique_username

from .fields import HTMLField


class UniqueUsernameTest(TestCase):
    def setUp(self):
        super(UniqueUsernameTest, self).setUp()
        self.userA = mommy.make('auth.User', username='customerA', first_name='Customer', last_name='TestA', email='testA+customer@lawpal.com')

    def test__get_unique_username(self):
        self.assertEqual(_get_unique_username('unique-monkey-nuts'), 'unique-monkey-nuts')

    def test__get_unique_username_not_unique(self):
        self.assertNotEqual(_get_unique_username('customerA'), 'customerA')


class HTMLFieldTests(TestCase):
    def test_microsoft_word_html(self):
        # test that we strip Microsoft Word HTML
        f = HTMLField()
        self.assertEqual(f.to_python("<p class=MsoNormal style='margin-top:3.0pt;margin-right:0in;margin-bottom:0in;margin-left:.2in;margin-bottom:.0001pt;text-indent:-.2in'>Hello world!</p>"), 'Hello world!')
        self.assertEqual(f.to_python("<p style='margin-top:3.0pt;margin-right:0in;margin-bottom:0in;margin-left:.2in;margin-bottom:.0001pt;text-indent:-.2in'><a name=ahali></a><b>Hello</b> <i>[...]</i> world!</p>"), 'Hello [...] world!')
