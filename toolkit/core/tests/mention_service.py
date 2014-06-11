# -*- coding: utf-8 -*-
from django.core import mail
from django.test import TestCase
from django.db.models.query import QuerySet

from model_mommy import mommy

from toolkit.casper.workflow_case import BaseScenarios
from toolkit.core.services.mentions import MentionsService
from toolkit.apps.default.templatetags.toolkit_tags import ABSOLUTE_BASE_URL


class MentionsServiceTest(BaseScenarios, TestCase):
    subject = MentionsService

    def setUp(self):
        super(MentionsServiceTest, self).setUp()
        self.basic_workspace()

    def test_correct_init(self):
        with self.assertRaises(TypeError):
            service = self.subject()

    def test_detects_mentions(self):
        service = self.subject(mentioned_by=self.lawyer)
        users = service.process(text='@test-customer I thought I saw you buying bananas at the flea-market the other day?')

        self.assertEqual(type(users), QuerySet)
        self.assertEqual(users.count(), 1)
        self.assertEqual(service.mentioned_usernames, ['test-customer'])
        # no mail should be sent unless specifically requested
        self.assertEqual(len(mail.outbox), 0)

    def test_detects_multiple_mentions(self):
        service = self.subject(mentioned_by=self.lawyer)
        users = service.process(text='@test-customer I thought I saw you and @test-lawyer buying pineapples at the flea-market the other day?')

        self.assertEqual(type(users), QuerySet)
        self.assertEqual(users.count(), 2)
        self.assertEqual(service.mentioned_usernames, ['test-customer', 'test-lawyer'])
        # no mail should be sent unless specifically requested
        self.assertEqual(len(mail.outbox), 0)


    def test_multiple_mailouts(self):
        service = self.subject(mentioned_by=self.lawyer)

        users = service.process(notify=True,
                                text='@test-customer I thought I saw you and @test-lawyer buying pineapples at the flea-market the other day?')

        self.assertEqual(type(users), QuerySet)
        self.assertEqual(users.count(), 2)
        self.assertEqual(service.mentioned_usernames, ['test-customer', 'test-lawyer'])
        # no mail should be sent unless specifically requested
        # in this case there are 2 because we specified notify=True
        self.assertEqual(len(mail.outbox), 2)

        email_a = mail.outbox[0]
        email_b = mail.outbox[1]

        self.assertEqual(email_a.subject, u'Lawyër Tëst mentioned you in a comment')
        self.assertEqual(email_b.subject, u'Lawyër Tëst mentioned you in a comment')

        # handle ordering items issue in postgres vs sqlite
        self.assertItemsEqual(email_a.recipients() + email_b.recipients(), [u'test+customer@lawpal.com', u'test+lawyer@lawpal.com'])

        self.assertTrue(u'<p>{mentioned_by} has mentioned you in a comment.</p>'.format(mentioned_by=self.lawyer) in email_a.body)
        self.assertTrue(u'<p>{mentioned_by} has mentioned you in a comment.</p>'.format(mentioned_by=self.lawyer) in email_b.body)

        self.assertTrue(u'<blockquotes>@test-customer I thought I saw you and @test-lawyer buying pineapples at the flea-market the other day?</blockquotes>' in email_a.body)
        self.assertTrue(u'<blockquotes>@test-customer I thought I saw you and @test-lawyer buying pineapples at the flea-market the other day?</blockquotes>' in email_b.body)

        # we sent no access url so its just a simple reference
        self.assertTrue(u'You can view this mention at:' not in email_a.body)
        self.assertTrue(u'You can view this mention at:' not in email_b.body)

    def test_mention_with_access_url(self):
        expected_access_url = 'https://lawpal.com/some/url/that/goes/somewhere/good/'
        service = self.subject(mentioned_by=self.lawyer)
        users = service.process(notify=True,
                                text='@test-customer I imagine that you will have some way of paying for that kiwi?',
                                access_url=expected_access_url)

        self.assertEqual(type(users), QuerySet)
        self.assertEqual(users.count(), 1)
        self.assertEqual(service.mentioned_usernames, ['test-customer'])
        # no mail should be sent unless specifically requested
        self.assertEqual(len(mail.outbox), 1)

        email_a = mail.outbox[0]

        self.assertEqual(email_a.subject, u'Lawyër Tëst mentioned you in a comment')

        self.assertEqual(email_a.recipients(), [u'test+customer@lawpal.com'])

        self.assertTrue(u'<p>{mentioned_by} has mentioned you in a comment.</p>'.format(mentioned_by=self.lawyer) in email_a.body)

        self.assertTrue(u'<blockquotes>@test-customer I imagine that you will have some way of paying for that kiwi?' in email_a.body)

        # we sent an access url so it shuold now show
        self.assertTrue(u'<p>You can view this mention at: <a href="{url}">{url}</a></p>'.format(url=expected_access_url) in email_a.body)


    def test_mention_with_action_object(self):
        """
        If we pass in an action_object the service should change the message slightly
        if action_object has a .matter attribute it will use that and mention the item (action_object) and matter by name
        """
        item = mommy.make('item.Item', matter=self.matter, name='Test Item No. 1', category="A")

        expected_access_url = ABSOLUTE_BASE_URL(item.get_absolute_url())

        service = self.subject(mentioned_by=self.lawyer)
        users = service.process(notify=True,
                                text='@test-customer the kiwi is NOT off, how dare you imply we are selling faulty goods here.',
                                access_url=expected_access_url,
                                action_object=item)

        self.assertEqual(type(users), QuerySet)
        self.assertEqual(users.count(), 1)
        self.assertEqual(service.mentioned_usernames, ['test-customer'])
        # no mail should be sent unless specifically requested
        self.assertEqual(len(mail.outbox), 1)

        email_a = mail.outbox[0]

        self.assertEqual(email_a.subject, u'Lawyër Tëst mentioned you in a comment')

        self.assertEqual(email_a.recipients(), [u'test+customer@lawpal.com'])

        self.assertTrue(u'<p>{mentioned_by} has mentioned you in a comment on "{action_object}" in "{matter}".</p>'.format(mentioned_by=self.lawyer, action_object=item, matter=item.matter) in email_a.body)

        self.assertTrue(u'<blockquotes>@test-customer the kiwi is NOT off, how dare you imply we are selling faulty goods here.' in email_a.body)

        # we sent an access url so it shuold now show
        self.assertTrue(u'<p>You can view this mention at: <a href="{url}">{url}</a></p>'.format(url=expected_access_url) in email_a.body)

