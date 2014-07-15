# -*- coding: utf-8 -*-
import json

from django.contrib.auth.models import User
from django.core import mail

from model_mommy import mommy
from rest_framework.reverse import reverse

from toolkit.api.serializers import DiscussionSerializer
from toolkit.apps.workspace.models import ROLES, WorkspaceParticipants

from . import BaseEndpointTest


class BaseDiscussionEndpointTest(BaseEndpointTest):
    def setUp(self):
        super(BaseDiscussionEndpointTest, self).setUp()

        # not a matter participant
        self.forbidden_user = self.create_user(username='forbidden-user', email='forbidden+user@lawpal.com')

        # Not a thread participant
        self.invalid_user = self.create_user(username='invalid-user', email='invalid+user@lawpal.com')
        WorkspaceParticipants.objects.create(workspace=self.matter, user=self.invalid_user, role=ROLES.client)


"""
Matter Discussion tests
"""
class BaseMatterDiscussionEndpointTest(BaseDiscussionEndpointTest):
    def setUp(self):
        super(BaseMatterDiscussionEndpointTest, self).setUp()

        self.thread = mommy.make(
            'discussion.DiscussionComment',
            matter=self.matter,
            title='Thread',
            comment='Hello world!',
            participants=(self.lawyer, self.user),
            user=self.lawyer
        )

        self.comment = mommy.make(
            'discussion.DiscussionComment',
            matter=self.matter,
            parent=self.thread,
            comment='Hello world!',
            user=self.lawyer
        )


class MatterDiscussionsTest(BaseMatterDiscussionEndpointTest):
    @property
    def endpoint(self):
        return reverse('matter_discussion-list', kwargs={ 'matter_slug': self.matter.slug })

    def test_endpoint_name(self):
        self.assertEqual(self.endpoint, '/api/v1/matters/%(matter_slug)s/discussions' % {
            'matter_slug': self.matter.slug
        })

    def test_get(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        resp = self.client.get(self.endpoint, content_type='application/json')
        self.assertEqual(resp.status_code, 200)

        json_data = json.loads(resp.content)
        self.assertEqual(json_data['count'], 1)
        self.assertEqual(json_data['results'][0]['slug'], str(self.thread.slug))
        self.assertEqual(json_data['results'][0]['title'], self.thread.title)
        self.assertEqual(json_data['results'][0]['content'], self.thread.comment)

    def test_anon_get(self):
        resp = self.client.get(self.endpoint, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_forbidden_get(self):
        """ Non matter-participants can't see the list """
        self.client.login(username=self.forbidden_user.username, password=self.password)

        resp = self.client.get(self.endpoint, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_invalid_participant_get(self):
        """ Non thread-participants can't see the thread """
        self.client.login(username=self.invalid_user.username, password=self.password)

        resp = self.client.get(self.endpoint, content_type='application/json')
        self.assertEqual(resp.status_code, 200)

        json_data = json.loads(resp.content)
        self.assertEqual(json_data['count'], 0)

    def test_post(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        resp = self.client.post(self.endpoint, json.dumps({
            'title': 'New Thread',
            'content': 'Hello world!',
        }), content_type='application/json')
        self.assertEqual(resp.status_code, 201)  # created

        json_data = json.loads(resp.content)
        self.assertEqual(json_data['title'], 'New Thread')
        self.assertEqual(json_data['content'], 'Hello world!')
        self.assertEqual(len(json_data['participants']), 1)
        self.assertEqual(json_data['participants'][0]['username'], self.lawyer.username)

    # def test_post_with_participants(self):
        # self.client.login(username=self.lawyer.username, password=self.password)

        # @TODO: allow the setting of participants through the create
        # resp = self.client.post(self.endpoint, json.dumps({
            # 'title': 'New Thread',
            # 'content': 'Hello world!',
            # 'participants': ({
                # 'username': self.user.username
            # },)
        # }), content_type='application/json')
        # self.assertEqual(resp.status_code, 201)  # created

        # json_data = json.loads(resp.content)
        # self.assertEqual(json_data['title'], 'New Thread')
        # self.assertEqual(json_data['content'], 'Hello world!')
        # self.assertEqual(len(json_data['participants']), 2)
        # self.assertEqual(json_data['participants'][0]['username'], self.lawyer.username)
        # self.assertEqual(json_data['participants'][1]['username'], self.user.username)

    def test_anon_post(self):
        resp = self.client.post(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_forbidden_post(self):
        self.client.login(username=self.forbidden_user.username, password=self.password)

        resp = self.client.post(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_patch(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        resp = self.client.patch(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 405)  # not allowed

    def test_anon_patch(self):
        resp = self.client.patch(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_forbidden_patch(self):
        self.client.login(username=self.forbidden_user.username, password=self.password)

        resp = self.client.patch(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_delete(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        resp = self.client.delete(self.endpoint, content_type='application/json')
        self.assertEqual(resp.status_code, 405)  # not allowed

    def test_anon_delete(self):
        resp = self.client.delete(self.endpoint, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_forbidden_delete(self):
        self.client.login(username=self.forbidden_user.username, password=self.password)

        resp = self.client.delete(self.endpoint, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden


class MatterDiscussionDetailTest(BaseMatterDiscussionEndpointTest):
    @property
    def endpoint(self):
        return reverse('matter_discussion-detail', kwargs={ 'matter_slug': self.matter.slug, 'slug': self.thread.slug })

    def test_endpoint_name(self):
        self.assertEqual(self.endpoint, '/api/v1/matters/%(matter_slug)s/discussions/%(thread_slug)s' % {
            'matter_slug': self.matter.slug,
            'thread_slug': self.thread.slug
        })

    def test_get(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        resp = self.client.get(self.endpoint, content_type='application/json')
        self.assertEqual(resp.status_code, 200)

        json_data = json.loads(resp.content)
        self.assertEqual(json_data['slug'], str(self.thread.slug))
        self.assertEqual(json_data['title'], self.thread.title)
        self.assertEqual(json_data['content'], self.thread.comment)

    def test_anon_get(self):
        resp = self.client.get(self.endpoint, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_forbidden_get(self):
        """ Non matter-participants can't see the thread """
        self.client.login(username=self.forbidden_user.username, password=self.password)

        resp = self.client.get(self.endpoint, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_invalid_participant_get(self):
        """ Non thread-participants can't see the thread """
        self.client.login(username=self.invalid_user.username, password=self.password)

        resp = self.client.get(self.endpoint, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_post(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        resp = self.client.post(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 405)  # not allowed

    def test_anon_post(self):
        resp = self.client.post(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_forbidden_post(self):
        self.client.login(username=self.forbidden_user.username, password=self.password)

        resp = self.client.post(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_invalid_participant_post(self):
        self.client.login(username=self.invalid_user.username, password=self.password)

        resp = self.client.post(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 405)  # not allowed

    def test_put(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        resp = self.client.put(self.endpoint, json.dumps({
            'title': 'Updated Thread',
            'content': 'Goodbye world!',
        }), content_type='application/json')
        self.assertEqual(resp.status_code, 200)

        json_data = json.loads(resp.content)
        self.assertEqual(json_data['title'], 'Updated Thread')
        self.assertEqual(json_data['content'], 'Goodbye world!')

    # def test_put_with_participants(self):
        # @TODO: enable this
        # self.client.login(username=self.lawyer.username, password=self.password)

        # resp = self.client.put(self.endpoint, json.dumps({
            # 'title': 'Updated Thread',
            # 'participants': ({
                # 'username': self.forbidden_user.username,
            # },)
        # }), content_type='application/json')
        # self.assertEqual(resp.status_code, 200)

        # json_data = json.loads(resp.content)
        # self.assertEqual(json_data['title'], 'Updated Thread')
        # self.assertEqual(json_data['content'], 'Hello world!')
        # self.assertEqual(len(json_data['participants']), 2)
        # self.assertEqual(json_data['participants'][0]['username'], '')
        # self.assertEqual(json_data['participants'][1]['username'], '')

    def test_anon_put(self):
        resp = self.client.put(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_forbidden_put(self):
        self.client.login(username=self.forbidden_user.username, password=self.password)

        resp = self.client.put(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_invalid_participant_put(self):
        self.client.login(username=self.invalid_user.username, password=self.password)

        resp = self.client.put(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_non_author_put(self):
        """ Can other users (apart from the author) edit the thread """
        self.client.login(username=self.user.username, password=self.password)

        resp = self.client.put(self.endpoint, json.dumps({
            'title': 'Updated Thread',
        }), content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_delete(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        resp = self.client.delete(self.endpoint, content_type='application/json')
        self.assertEqual(resp.status_code, 204)  # deleted

    def test_anon_delete(self):
        resp = self.client.delete(self.endpoint, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_forbidden_delete(self):
        self.client.login(username=self.forbidden_user.username, password=self.password)

        resp = self.client.delete(self.endpoint, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_invalid_participant_delete(self):
        self.client.login(username=self.invalid_user.username, password=self.password)

        resp = self.client.delete(self.endpoint, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden


class MatterDiscussionCommentsTest(BaseMatterDiscussionEndpointTest):
    @property
    def endpoint(self):
        return reverse('matter_discussion_comment-list', kwargs={
            'matter_slug': self.matter.slug,
            'thread_slug': self.thread.slug
        })

    def test_endpoint_name(self):
        self.assertEqual(self.endpoint, '/api/v1/matters/%(matter_slug)s/discussions/%(thread_slug)s/comments' % {
            'matter_slug': self.matter.slug,
            'thread_slug': self.thread.slug
        })

    def test_get(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        resp = self.client.get(self.endpoint, content_type='application/json')
        self.assertEqual(resp.status_code, 200)

        json_data = json.loads(resp.content)
        self.assertEqual(json_data['count'], 1)
        self.assertEqual(json_data['results'][0]['slug'], str(self.comment.slug))
        self.assertEqual(json_data['results'][0]['content'], self.comment.comment)

    def test_anon_get(self):
        resp = self.client.get(self.endpoint, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_forbidden_get(self):
        """ Non matter-participants can't see the comments """
        self.client.login(username=self.forbidden_user.username, password=self.password)

        resp = self.client.get(self.endpoint, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_invalid_participant_get(self):
        """ Non thread-participants can't see the comments """
        self.client.login(username=self.invalid_user.username, password=self.password)

        resp = self.client.get(self.endpoint, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_post(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        resp = self.client.post(self.endpoint, json.dumps({
            'content': 'Goodbye world!',
        }), content_type='application/json')
        self.assertEqual(resp.status_code, 201)  # created

        json_data = json.loads(resp.content)
        self.assertEqual(json_data['content'], 'Goodbye world!')

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].from_email, 'support@lawpal.com')
        self.assertEqual(mail.outbox[0].to, [self.user.email])
        self.assertEqual(mail.outbox[0].subject, u'{actor} commented on the thread {thread} in {matter}'.format(
            actor=self.lawyer,
            matter=self.workspace,
            thread=self.thread,
        ))

    def test_anon_post(self):
        resp = self.client.post(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_forbidden_post(self):
        self.client.login(username=self.forbidden_user.username, password=self.password)

        resp = self.client.post(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_patch(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        resp = self.client.patch(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 405)  # not allowed

    def test_anon_patch(self):
        resp = self.client.patch(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_forbidden_patch(self):
        self.client.login(username=self.forbidden_user.username, password=self.password)

        resp = self.client.patch(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_delete(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        resp = self.client.delete(self.endpoint, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_anon_delete(self):
        resp = self.client.delete(self.endpoint, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_forbidden_delete(self):
        self.client.login(username=self.forbidden_user.username, password=self.password)

        resp = self.client.delete(self.endpoint, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden


class MatterDiscussionCommentDetailTest(BaseMatterDiscussionEndpointTest):
    @property
    def endpoint(self):
        return reverse('matter_discussion_comment-detail', kwargs={
            'matter_slug': self.matter.slug,
            'slug': self.comment.slug,
            'thread_slug': self.thread.slug
        })

    def test_endpoint_name(self):
        self.assertEqual(self.endpoint, '/api/v1/matters/%(matter_slug)s/discussions/%(thread_slug)s/comments/%(slug)s' % {
            'matter_slug': self.matter.slug,
            'slug': self.comment.slug,
            'thread_slug': self.thread.slug
        })

    def test_get(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        resp = self.client.get(self.endpoint, content_type='application/json')
        self.assertEqual(resp.status_code, 200)

        json_data = json.loads(resp.content)
        self.assertEqual(json_data['slug'], str(self.comment.slug))
        self.assertEqual(json_data['content'], self.comment.comment)

    def test_anon_get(self):
        resp = self.client.get(self.endpoint, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_forbidden_get(self):
        """ Non matter-participants can't see the comment """
        self.client.login(username=self.forbidden_user.username, password=self.password)

        resp = self.client.get(self.endpoint, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_invalid_participant_get(self):
        """ Non thread-participants can't see the comment """
        self.client.login(username=self.invalid_user.username, password=self.password)

        resp = self.client.get(self.endpoint, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_non_author_get(self):
        self.client.login(username=self.user.username, password=self.password)

        resp = self.client.get(self.endpoint, content_type='application/json')
        self.assertEqual(resp.status_code, 200)

        json_data = json.loads(resp.content)
        self.assertEqual(json_data['slug'], str(self.comment.slug))
        self.assertEqual(json_data['content'], self.comment.comment)

    def test_post(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        resp = self.client.post(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 405)  # not allowed

    def test_anon_post(self):
        resp = self.client.post(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_forbidden_post(self):
        self.client.login(username=self.forbidden_user.username, password=self.password)

        resp = self.client.post(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_invalid_participant_post(self):
        self.client.login(username=self.invalid_user.username, password=self.password)

        resp = self.client.post(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_non_author_post(self):
        self.client.login(username=self.user.username, password=self.password)

        resp = self.client.post(self.endpoint, json.dumps({}), content_type='application/json')
        self.assertEqual(resp.status_code, 405)  # not allowed

    def test_put(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        resp = self.client.put(self.endpoint, json.dumps({
            'content': 'foobar',
        }), content_type='application/json')
        self.assertEqual(resp.status_code, 200)

        json_data = json.loads(resp.content)
        self.assertEqual(json_data['content'], 'foobar')

    def test_anon_put(self):
        resp = self.client.put(self.endpoint, json.dumps({
            'content': 'foobar',
        }), content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_forbidden_put(self):
        self.client.login(username=self.forbidden_user.username, password=self.password)

        resp = self.client.put(self.endpoint, json.dumps({
            'content': 'foobar',
        }), content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_invalid_participant_put(self):
        self.client.login(username=self.invalid_user.username, password=self.password)

        resp = self.client.put(self.endpoint, json.dumps({
            'content': 'foobar',
        }), content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_non_author_put(self):
        """ Can other users (apart from the author) edit the comment """
        self.client.login(username=self.user.username, password=self.password)

        resp = self.client.put(self.endpoint, json.dumps({
            'content': 'foobar',
        }), content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_delete(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        resp = self.client.delete(self.endpoint, content_type='application/json')
        # @TODO: self.assertEqual(resp.status_code, 204)  # deleted
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_anon_delete(self):
        resp = self.client.delete(self.endpoint, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_forbidden_delete(self):
        self.client.login(username=self.forbidden_user.username, password=self.password)

        resp = self.client.delete(self.endpoint, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_invalid_participant_delete(self):
        self.client.login(username=self.invalid_user.username, password=self.password)

        resp = self.client.delete(self.endpoint, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_non_author_delete(self):
        self.client.login(username=self.user.username, password=self.password)

        resp = self.client.delete(self.endpoint, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden


class MatterDiscussionParticipantsTest(BaseMatterDiscussionEndpointTest):
    @property
    def endpoint(self):
        return reverse('matter_discussion_participant-list', kwargs={
            'matter_slug': self.matter.slug,
            'thread_slug': self.thread.slug
        })

    def test_endpoint_name(self):
        self.assertEqual(self.endpoint, '/api/v1/matters/%(matter_slug)s/discussions/%(thread_slug)s/participants' % {
            'matter_slug': self.matter.slug,
            'thread_slug': self.thread.slug
        })

    def test_get(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        resp = self.client.get(self.endpoint, content_type='application/json')
        self.assertEqual(resp.status_code, 200)

        json_data = json.loads(resp.content)
        self.assertEqual(json_data['count'], 2)
        self.assertEqual(json_data['results'][0]['username'], self.user.username)
        self.assertEqual(json_data['results'][1]['username'], self.lawyer.username)

    def test_anon_get(self):
        resp = self.client.get(self.endpoint, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_forbidden_get(self):
        """ Non matter-participants can't see the participants """
        self.client.login(username=self.forbidden_user.username, password=self.password)

        resp = self.client.get(self.endpoint, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_invalid_participant_get(self):
        """ Non thread-participants can't see the participants """
        self.client.login(username=self.invalid_user.username, password=self.password)

        resp = self.client.get(self.endpoint, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_post(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        resp = self.client.post(self.endpoint, json.dumps({
            'username': self.forbidden_user.username,
        }), content_type='application/json')
        self.assertEqual(resp.status_code, 201)  # created

        json_data = json.loads(resp.content)
        self.assertEqual(json_data['username'], self.forbidden_user.username)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].from_email, 'support@lawpal.com')
        self.assertEqual(mail.outbox[0].to, [self.forbidden_user.email])
        self.assertEqual(mail.outbox[0].subject, u'{actor} added you to the thread {thread} in {matter}'.format(
            actor=self.lawyer,
            matter=self.workspace,
            thread=self.thread,
        ))

    def test_post_with_new_user(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        resp = self.client.post(self.endpoint, json.dumps({
            'email': 'new+user@lawpal.com',
            'first_name': 'New',
            'last_name': 'User',
        }), content_type='application/json')
        self.assertEqual(resp.status_code, 201)  # created

        new_user = User.objects.get(email='new+user@lawpal.com')

        json_data = json.loads(resp.content)
        self.assertEqual(json_data['username'], new_user.username)

    def test_anon_post(self):
        resp = self.client.post(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_forbidden_post(self):
        self.client.login(username=self.forbidden_user.username, password=self.password)

        resp = self.client.post(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_patch(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        resp = self.client.patch(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 405)  # not allowed

    def test_anon_patch(self):
        resp = self.client.patch(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_forbidden_patch(self):
        self.client.login(username=self.forbidden_user.username, password=self.password)

        resp = self.client.patch(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_delete(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        resp = self.client.delete(self.endpoint, content_type='application/json')
        self.assertEqual(resp.status_code, 405)  # not allowed

    def test_anon_delete(self):
        resp = self.client.delete(self.endpoint, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_forbidden_delete(self):
        self.client.login(username=self.forbidden_user.username, password=self.password)

        resp = self.client.delete(self.endpoint, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden


class MatterDiscussionParticipantDetailTest(BaseMatterDiscussionEndpointTest):
    @property
    def endpoint(self):
        return reverse('matter_discussion_participant-detail', kwargs={
            'matter_slug': self.matter.slug,
            'thread_slug': self.thread.slug,
            'username': self.lawyer.username
        })

    def test_endpoint_name(self):
        self.assertEqual(self.endpoint, '/api/v1/matters/%(matter_slug)s/discussions/%(thread_slug)s/participants/%(username)s' % {
            'matter_slug': self.matter.slug,
            'thread_slug': self.thread.slug,
            'username': self.lawyer.username
        })

    def test_get(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        resp = self.client.get(self.endpoint, content_type='application/json')
        self.assertEqual(resp.status_code, 200)

        json_data = json.loads(resp.content)
        self.assertEqual(json_data['username'], self.lawyer.username)

    def test_anon_get(self):
        resp = self.client.get(self.endpoint, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_forbidden_get(self):
        """ Non matter-participants can't see the participant """
        self.client.login(username=self.forbidden_user.username, password=self.password)

        resp = self.client.get(self.endpoint, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_invalid_participant_get(self):
        """ Non thread-participants can't see the participant """
        self.client.login(username=self.invalid_user.username, password=self.password)

        resp = self.client.get(self.endpoint, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_post(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        resp = self.client.post(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 405)  # not allowed

    def test_anon_post(self):
        resp = self.client.post(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_forbidden_post(self):
        self.client.login(username=self.forbidden_user.username, password=self.password)

        resp = self.client.post(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_invalid_participant_post(self):
        self.client.login(username=self.invalid_user.username, password=self.password)

        resp = self.client.post(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_non_author_post(self):
        self.client.login(username=self.user.username, password=self.password)

        resp = self.client.post(self.endpoint, json.dumps({}), content_type='application/json')
        self.assertEqual(resp.status_code, 405)  # not allowed

    def test_put(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        resp = self.client.put(self.endpoint, json.dumps({
            'username': self.forbidden_user.username,
        }), content_type='application/json')
        self.assertEqual(resp.status_code, 405)  # not allowed

    def test_anon_put(self):
        resp = self.client.put(self.endpoint, json.dumps({
            'username': self.forbidden_user.username,
        }), content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_forbidden_put(self):
        self.client.login(username=self.forbidden_user.username, password=self.password)

        resp = self.client.put(self.endpoint, json.dumps({
            'username': self.forbidden_user.username,
        }), content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_invalid_participant_put(self):
        self.client.login(username=self.invalid_user.username, password=self.password)

        resp = self.client.put(self.endpoint, json.dumps({
            'username': self.forbidden_user.username,
        }), content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_non_author_put(self):
        self.client.login(username=self.user.username, password=self.password)

        resp = self.client.put(self.endpoint, json.dumps({
            'username': self.forbidden_user.username,
        }), content_type='application/json')
        self.assertEqual(resp.status_code, 405)  # not allowed

    def test_delete(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        resp = self.client.delete(self.endpoint, content_type='application/json')
        self.assertEqual(resp.status_code, 204)  # deleted

    def test_anon_delete(self):
        resp = self.client.delete(self.endpoint, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_forbidden_delete(self):
        self.client.login(username=self.forbidden_user.username, password=self.password)

        resp = self.client.delete(self.endpoint, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_invalid_participant_delete(self):
        self.client.login(username=self.invalid_user.username, password=self.password)

        resp = self.client.delete(self.endpoint, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_other_participant_delete(self):
        self.client.login(username=self.user.username, password=self.password)

        resp = self.client.delete(self.endpoint, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden


"""
Item discussion tests
"""
class BaseItemDiscussionEndpointTest(BaseDiscussionEndpointTest):
    def setUp(self):
        super(BaseItemDiscussionEndpointTest, self).setUp()

        # Need to add another colleague
        self.colleague = self.create_user(username='colleague', email='colleague@lawpal.com')
        WorkspaceParticipants.objects.create(workspace=self.matter, user=self.colleague, role=ROLES.colleague)

        self.item = mommy.make(
            'item.Item',
            name='Test Item',
            matter=self.matter
        )

        self.private_comment = mommy.make(
            'discussion.DiscussionComment',
            item=self.item,
            comment='Hello world!',
            is_public=False,
            user=self.lawyer
        )

        self.public_comment = mommy.make(
            'discussion.DiscussionComment',
            item=self.item,
            comment='Hello world!',
            is_public=True,
            user=self.lawyer
        )


class ItemPrivateDiscussionCommentsTest(BaseItemDiscussionEndpointTest):
    @property
    def endpoint(self):
        return reverse('item_discussion_comment-list', kwargs={
            'item_slug': self.item.slug,
            'matter_slug': self.matter.slug,
            'thread_slug': 'private',
        })

    def test_endpoint_name(self):
        self.assertEqual(self.endpoint, '/api/v1/matters/%(matter_slug)s/items/%(item_slug)s/discussions/%(thread_slug)s/comments' % {
            'item_slug': self.item.slug,
            'matter_slug': self.matter.slug,
            'thread_slug': 'private',
        })

    def test_get(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        resp = self.client.get(self.endpoint, content_type='application/json')
        self.assertEqual(resp.status_code, 200)

        json_data = json.loads(resp.content)
        self.assertEqual(json_data['count'], 1)
        self.assertEqual(json_data['results'][0]['slug'], str(self.private_comment.slug))
        self.assertEqual(json_data['results'][0]['content'], self.private_comment.comment)

    def test_anon_get(self):
        resp = self.client.get(self.endpoint, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_forbidden_get(self):
        """ Non matter-participants can't see the comments """
        self.client.login(username=self.forbidden_user.username, password=self.password)

        resp = self.client.get(self.endpoint, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_invalid_get(self):
        """ Non-colleagues can't see private comments """
        self.client.login(username=self.invalid_user.username, password=self.password)

        resp = self.client.get(self.endpoint, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_post(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        resp = self.client.post(self.endpoint, json.dumps({
            'content': 'Goodbye world!',
        }), content_type='application/json')
        self.assertEqual(resp.status_code, 201)  # created

        json_data = json.loads(resp.content)
        self.assertEqual(json_data['content'], 'Goodbye world!')

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].from_email, 'support@lawpal.com')
        self.assertEqual(mail.outbox[0].to, [self.colleague.email])
        self.assertEqual(mail.outbox[0].subject, u'{actor} commented on the item {item} in {matter}'.format(
            actor=self.lawyer,
            item=self.item,
            matter=self.matter,
        ))

    def test_anon_post(self):
        resp = self.client.post(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_forbidden_post(self):
        self.client.login(username=self.forbidden_user.username, password=self.password)

        resp = self.client.post(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_invalid_post(self):
        self.client.login(username=self.invalid_user.username, password=self.password)

        resp = self.client.post(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_patch(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        resp = self.client.patch(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 405)  # not allowed

    def test_anon_patch(self):
        resp = self.client.patch(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_forbidden_patch(self):
        self.client.login(username=self.forbidden_user.username, password=self.password)

        resp = self.client.patch(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_invalid_patch(self):
        self.client.login(username=self.invalid_user.username, password=self.password)

        resp = self.client.patch(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_delete(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        resp = self.client.delete(self.endpoint, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_anon_delete(self):
        resp = self.client.delete(self.endpoint, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_forbidden_delete(self):
        self.client.login(username=self.forbidden_user.username, password=self.password)

        resp = self.client.delete(self.endpoint, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_invalid_delete(self):
        self.client.login(username=self.invalid_user.username, password=self.password)

        resp = self.client.delete(self.endpoint, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden


class ItemPublicDiscussionCommentsTest(BaseItemDiscussionEndpointTest):
    @property
    def endpoint(self):
        return reverse('item_discussion_comment-list', kwargs={
            'item_slug': self.item.slug,
            'matter_slug': self.matter.slug,
            'thread_slug': 'public',
        })

    def test_endpoint_name(self):
        self.assertEqual(self.endpoint, '/api/v1/matters/%(matter_slug)s/items/%(item_slug)s/discussions/%(thread_slug)s/comments' % {
            'item_slug': self.item.slug,
            'matter_slug': self.matter.slug,
            'thread_slug': 'public',
        })

    def test_get(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        resp = self.client.get(self.endpoint, content_type='application/json')
        self.assertEqual(resp.status_code, 200)

        json_data = json.loads(resp.content)
        self.assertEqual(json_data['count'], 1)
        self.assertEqual(json_data['results'][0]['slug'], str(self.public_comment.slug))
        self.assertEqual(json_data['results'][0]['content'], self.public_comment.comment)

    def test_anon_get(self):
        resp = self.client.get(self.endpoint, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_forbidden_get(self):
        """ Non matter-participants can't see the comments """
        self.client.login(username=self.forbidden_user.username, password=self.password)

        resp = self.client.get(self.endpoint, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_post(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        resp = self.client.post(self.endpoint, json.dumps({
            'content': 'Goodbye world!',
        }), content_type='application/json')
        self.assertEqual(resp.status_code, 201)  # created

        json_data = json.loads(resp.content)
        self.assertEqual(json_data['content'], 'Goodbye world!')

        args = {
            'actor': self.lawyer,
            'item': self.item,
            'matter': self.workspace,
        }

        self.assertEqual(len(mail.outbox), 3)
        self.assertEqual(mail.outbox[0].from_email, 'support@lawpal.com')
        self.assertEqual(mail.outbox[0].to, [self.user.email])
        self.assertEqual(mail.outbox[0].subject, u'{actor} commented on the item {item} in {matter}'.format(**args))
        self.assertEqual(mail.outbox[1].from_email, 'support@lawpal.com')
        self.assertEqual(mail.outbox[1].to, [self.invalid_user.email])
        self.assertEqual(mail.outbox[1].subject, u'{actor} commented on the item {item} in {matter}'.format(**args))
        self.assertEqual(mail.outbox[2].from_email, 'support@lawpal.com')
        self.assertEqual(mail.outbox[2].to, [self.colleague.email])
        self.assertEqual(mail.outbox[2].subject, u'{actor} commented on the item {item} in {matter}'.format(**args))

    def test_anon_post(self):
        resp = self.client.post(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_forbidden_post(self):
        self.client.login(username=self.forbidden_user.username, password=self.password)

        resp = self.client.post(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_patch(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        resp = self.client.patch(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 405)  # not allowed

    def test_anon_patch(self):
        resp = self.client.patch(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_forbidden_patch(self):
        self.client.login(username=self.forbidden_user.username, password=self.password)

        resp = self.client.patch(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_delete(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        resp = self.client.delete(self.endpoint, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_anon_delete(self):
        resp = self.client.delete(self.endpoint, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_forbidden_delete(self):
        self.client.login(username=self.forbidden_user.username, password=self.password)

        resp = self.client.delete(self.endpoint, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden
