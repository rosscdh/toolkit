# -*- coding: utf-8 -*-
import json
from django.template import loader
from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.utils.html import strip_spaces_between_tags as minify_html

from toolkit.apps.default.templatetags.toolkit_tags import ABSOLUTE_BASE_URL
from toolkit.apps.matter.services.matter_permission import MightyMatterUserPermissionService
from toolkit.apps.notification.templatetags.notice_tags import get_notification_template
from toolkit.apps.workspace.models import ROLES
from toolkit.casper.workflow_case import BaseScenarios

from stored_messages.models import Inbox

from model_mommy import mommy


def _get_notice_html(verb_slug, ctx):
    t = get_notification_template(verb_slug)
    #
    # minify the html (as were using minification middleware)
    # also remove \r\n chars
    #
    return minify_html(t.render(loader.Context(ctx)).strip())


class BaseListViewTest(BaseScenarios, TestCase):
    """
    Provides a base test method that can be compared with the main listing
    """
    endpoint = reverse('notification:default')

    def setUp(self):
        super(BaseListViewTest, self).setUp()
        self.client = Client()

    def assert_html_present(self, test_html, verb_slug, notice_pk, actor_name, actor_initials, message, date, base_url,
                            target_name, client_name, action_object_name, action_object_url):


        # TODO rebuild function to contain the ctx-elemtens used in partials/default.html

        expected_html = _get_notice_html(verb_slug, {
            'notice_pk': notice_pk,
            'actor_name': actor_name,
            'actor_initials': actor_initials,
            'message': message,
            'date': date,
            'base_url': ABSOLUTE_BASE_URL(base_url),
            'target_name': target_name,
            'client_name': client_name,
            'action_object_name': action_object_name,
            'action_object_url': ABSOLUTE_BASE_URL(action_object_url),
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

        message = notice.message.data
        actor = message.get('actor')
        target = message.get('target')
        client = target.get('client')
        verb_slug = message.get('verb_slug')

        action_object_name = message.get('action_object', {}).get('name')
        action_object_url = message.get('action_object', {}).get('regular_url')

        self.assert_html_present(test_html=test_html,
                                 verb_slug=verb_slug,
                                 notice_pk=notice.pk,
                                 actor_name=actor.get('name') if actor else None,
                                 actor_initials=actor.get('initials') if actor else None,
                                 message=notice.message.message,
                                 date=notice.message.date,
                                 base_url=target.get('base_url') if target else None,
                                 target_name=target.get('name') if target else None,
                                 client_name=client.get('name') if client else None,
                                 action_object_name=action_object_name,
                                 action_object_url=action_object_url)

    def test_removed_matter_participant(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        MightyMatterUserPermissionService(matter=self.matter,
                                          role=ROLES.colleague,
                                          user=self.lawyer,
                                          changing_user=self.lawyer)\
            .process(permissions={'workspace.manage_participants': True})

        endpoint_url = reverse('matter_participant', kwargs={'matter_slug': self.matter.slug})
        """
        when you remove a user, obviously they dont get a notification; so we need to create another user
        and make them part of the matter
        """
        matter_participant = mommy.make('auth.User', first_name='Matter', last_name='Participant',
                                        username='matter-participant', email='matterparticipant@lawpal.com')
        matter_participant.set_password(self.password)
        matter_participant.save()
        matter_participant_profile = matter_participant.profile
        matter_participant_profile.validated_email = True
        matter_participant_profile.save(update_fields=['data'])

        # add the user
        data = {
            'email': matter_participant.email,
            'first_name': 'Bob',
            'last_name': 'Crockett',
            'message': 'Bob you are being added here please do something',
        }

        resp = self.client.post(endpoint_url,
                                json.dumps(data),
                                content_type='application/json')

        self.assertEqual(resp.status_code, 202)  # accepted

        # remove it again:
        # append the email to the url for DELETE
        endpoint = '%s/%s' % (endpoint_url, matter_participant.email)
        resp = self.client.delete(endpoint, None)
        self.assertEqual(resp.status_code, 202)  # accepted

        inbox = self.get_inbox(user=self.user)

        self.assertEqual(inbox.count(), 2)  # should get the notification about adding matter_participant to matter
        # for i in inbox:
        #     print i.__unicode__()
        self.assertTrue(all(i.__unicode__() in [u'[Customër Tëst] Lawyër Tëst added a new member to Lawpal (test)',
                                                u'[Customër Tëst] Lawyër Tëst removed Matter Participant as a participant of Lawpal (test)'] for i in inbox))

        inbox = self.get_inbox(user=matter_participant)

        self.assertEqual(inbox.count(), 1)  # should get the notification about adding matter_participant to matter
        notice = inbox.first()

        test_html = self.get_html(for_user=matter_participant)

        message = notice.message.data
        actor = message.get('actor')
        target = message.get('target')
        client = target.get('client')
        verb_slug = message.get('verb_slug')

        action_object_name = message.get('action_object', {}).get('name')
        action_object_url = message.get('action_object', {}).get('regular_url')
        #/matters/test-matter-1/#/checklist/d777c6c9fbfb4e53baf3efa896111972/revision/v1/review/bcfbea3b32a0476bb141a677746349a0

        self.assert_html_present(test_html=test_html,
                                 verb_slug=verb_slug,
                                 notice_pk=notice.pk,
                                 actor_name=actor.get('name') if actor else None,
                                 actor_initials=actor.get('initials') if actor else None,
                                 message=notice.message,
                                 date=notice.message.date,
                                 base_url=target.get('base_url') if target else None,
                                 target_name=target.get('name') if target else None,
                                 client_name=client.get('name') if client else None,
                                 action_object_name=action_object_name,
                                 action_object_url=action_object_url)