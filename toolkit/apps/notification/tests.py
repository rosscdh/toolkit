# -*- coding: utf-8 -*-
from django.test import TestCase
from django.db.models.query import QuerySet
from django.core.urlresolvers import reverse

from model_mommy import mommy
from stored_messages.models import Inbox

from toolkit.casper.workflow_case import BaseScenarios


class NotificationsViewTest(BaseScenarios, TestCase):
    endpoint = reverse('notification:default')

    def setUp(self):
        super(NotificationsViewTest, self).setUp()
        # basics
        self.basic_workspace()

        self.item = mommy.make('item.Item', matter=self.matter, name='Test Item with Revision', category=None)

        Inbox.objects.all().delete() ## clear em all

        # fake create comment
        self.matter.actions.add_item_comment(user=self.lawyer, item=self.item, comment='Hi there,\nhow are you doing')
        self.expected_message = Inbox.objects.filter(user=self.user).first()


    def test_initial_notifiactions_lawyer(self):
        """
        Should be 0 notifications as the lawyer creates the object
        """
        self.client.login(username=self.lawyer.username, password=self.password)
        resp = self.client.get(self.endpoint)
        
        self.assertTrue(resp.status_code, 200)
        self.assertTrue('inbox_list' in resp.context_data)
        self.assertEqual(type(resp.context_data.get('inbox_list')), QuerySet)
        self.assertEqual(len(resp.context_data.get('inbox_list')), 0)

    def test_notifiaction_for_customer(self):
        """
        Should be 0 notifications as the lawyer creates the object
        """
        self.client.login(username=self.user.username, password=self.password)
        resp = self.client.get(self.endpoint)
        
        self.assertTrue(resp.status_code, 200)
        self.assertTrue('inbox_list' in resp.context_data)
        self.assertEqual(type(resp.context_data.get('inbox_list')), QuerySet)
        # should be a comment
        self.assertEqual(len(resp.context_data.get('inbox_list')), 1)
        inbox_message = resp.context_data.get('inbox_list')[0]
        #expected_message
        self.assertEqual(inbox_message, self.expected_message)

    def test_mark_signle_notification_as_read(self):
        """
        If we delete 1 of a set of 1; then has_notifications should be False
        """
        self.client.login(username=self.user.username, password=self.password)
        resp = self.client.delete(reverse('notification:inbox-read', kwargs={'pk': self.expected_message.pk}))
        self.assertEqual(self.user.profile.has_notifications, False)

    def test_mark_single_notification_as_read_but_with_others_present(self):
        """
        If we delete 1 of a set; of notifications we should stil have has_notifications = True
        """
        self.matter.actions.add_item_comment(user=self.lawyer, item=self.item, comment='Whats the time')
        self.matter.actions.add_item_comment(user=self.lawyer, item=self.item, comment='Half past 9')
        self.matter.actions.add_item_comment(user=self.lawyer, item=self.item, comment='Time for coffee')

        self.client.login(username=self.user.username, password=self.password)
        resp = self.client.delete(reverse('notification:inbox-read', kwargs={'pk': self.expected_message.pk}))
        self.assertEqual(self.user.profile.has_notifications, True)
