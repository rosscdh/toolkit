# -*- coding: utf-8 -*-
from django.core import mail
from django.test import TestCase
from model_mommy import mommy

from toolkit.apps.workspace.services import EnsureCustomerService


class EnsureCustomerServiceTest(TestCase):
    """
    Test the ensure customer service
    """
    subject = EnsureCustomerService

    def test_username_exists_already(self):
        expected_full_name = u'Unique Person'
        self.userA = mommy.make('auth.User', username='testacustomer', first_name='Customer', last_name='TestA', email='testA+customer@lawpal.com')
        service = self.subject(email='%s@otherdomain.com' % self.userA.email.split('@')[0],
                               full_name=expected_full_name)
        service.process()

        self.assertTrue(service.user.username != self.userA.username)

        self.assertTrue(service.user.get_full_name() == expected_full_name)
        self.assertTrue(service.is_new is True)