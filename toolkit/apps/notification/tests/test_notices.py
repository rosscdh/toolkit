# -*- coding: utf-8 -*-
from django.template import loader
from django.test import TestCase, Client
from django.core.urlresolvers import reverse

from toolkit.casper.workflow_case import BaseScenarios

from stored_messages.models import Inbox

from model_mommy import mommy

NOTICE_TEMPLATE = loader.get_template('notification/partials/notice.html')  # allow override of template_name


def _get_notice_html(ctx):
    return NOTICE_TEMPLATE.render(loader.Context(ctx))


class BaseListViewTest(BaseScenarios, TestCase):
    """
    Provides a base test method that can be compared with the main listing
    """
    endpoint = reverse('notification:default')

    def setUp(self):
        super(BaseListViewTest, self).setUp()
        self.client = Client()

    def assert_html_present(self, test_html, notice_pk, actor_name, actor_initials, message, date, base_url, target_name, client_name):
        expected_html = _get_notice_html({
            'pk': notice_pk,
            'actor_name': actor_name,
            'actor_initials': actor_initials,
            'message': message,
            'date': date,
            'base_url': base_url,
            'target_name': target_name,
            'client_name': client_name,
        })
        #
        # The actual test
        #
        self.assertTrue(expected_html in test_html)

    def get_inbox(self, user):
        return Inbox.objects.filter(user=user)

    def get_html(self, for_user):
        self.client.login(username=for_user.username, password=self.password)
        resp = self.client.get(self.endpoint)

        self.assertEqual(resp.status_code, 200)

        return resp.content


class NotificationEventsListTest(BaseListViewTest):
    """
    Test to ensure that each of the appropriate events are shown correctly

        workspace-added-participant: matter.actions.added_matter_participant
        workspace-removed-participant: matter.actions.removed_matter_participant

        item-reopened
        item-closed
        item-commented
        item-comment-created
        item-comment-deleted
        item-invited-reviewer
        item-provide-a-document
        item-added-revision-comment

        revision-created
        revision-comment-created
        revision-added-revision-comment
    """
    def setUp(self):
        super(BaseListViewTest, self).setUp()
        self.basic_workspace()
        Inbox.objects.all().delete()

    def test_added_matter_participant(self):
        self.matter.actions.added_matter_participant(matter=self.matter, adding_user=self.lawyer, added_user=self.user)
        inbox = self.get_inbox(user=self.user)

        self.assertEqual(inbox.count(), 1)
        notice = inbox.first()

        test_html = self.get_html(for_user=self.user)

        self.assert_html_present(test_html=test_html,
                                 notice_pk=notice.pk,
                                 actor_name=notice.message.data.get('actor').get('name'),
                                 actor_initials=notice.message.data.get('actor').get('initials'),
                                 message=notice.message.message,
                                 date=notice.message.date,
                                 base_url=notice.message.data.get('target').get('base_url'),
                                 target_name=notice.message.data.get('target').get('name'),
                                 client_name=notice.message.data.get('target').get('client').get('name'))


    def test_removed_matter_participant(self):
        """
        when you remove a user, obviously they dont get a notification; so we need to create another user
        and make them part of the matter
        """
        matter_participant = mommy.make('auth.User', username='matter-participant', email='matterparticipant@lawpal.com')
        self.matter.participants.add(matter_participant)
        self.matter.participants.remove(self.user)
        #self.matter.actions.removed_matter_participant(matter=self.matter, removing_user=self.lawyer, removed_user=self.user)

        inbox = self.get_inbox(user=self.user)
        self.assertEqual(inbox.count(), 1)  # should get the notification about adding matter_participant to matter

        inbox = self.get_inbox(user=matter_participant)
        # import pdb;pdb.set_trace()
        self.assertEqual(inbox.count(), 1)
        notice = inbox.first()

        test_html = self.get_html(for_user=matter_participant)

        self.assert_html_present(test_html=test_html,
                                 notice_pk=notice.pk,
                                 actor_name=notice.message.data.get('actor').get('name'),
                                 actor_initials=notice.message.data.get('actor').get('initials'),
                                 message=notice.message.message,
                                 date=notice.message.date,
                                 base_url=notice.message.data.get('target').get('base_url'),
                                 target_name=notice.message.data.get('target').get('name'),
                                 client_name=notice.message.data.get('target').get('client').get('name'))

