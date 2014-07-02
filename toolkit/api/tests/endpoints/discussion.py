# -*- coding: utf-8 -*-
import json

from django.contrib.auth.models import User

from model_mommy import mommy
from rest_framework.reverse import reverse

from toolkit.api.serializers import DiscussionSerializer
from toolkit.apps.workspace.models import ROLES, WorkspaceParticipants

from . import BaseEndpointTest


class DiscussionsTest(BaseEndpointTest):
    def setUp(self):
        super(DiscussionsTest, self).setUp()
        self.thread = mommy.make(
            'discussion.DiscussionComment',
            matter=self.workspace,
            title='Thread',
            comment='Hello world!',
            participants=(self.lawyer,),
            user=self.lawyer
        )

        self.comment = mommy.make(
            'discussion.DiscussionComment',
            matter=self.workspace,
            parent=self.thread,
            comment='Hello world!',
            user=self.lawyer
        )

        self.forbidden_user = mommy.make('auth.User', username='forbidden-user', email='forbidden+user@lawpal.com')
        self.forbidden_user.set_password(self.password)
        self.forbidden_user.save()

    @property
    def endpoint(self):
        return reverse('discussion-list', kwargs={ 'matter_slug': self.matter.slug })

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
        self.client.login(username=self.user.username, password=self.password)

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


class DiscussionDetailTest(BaseEndpointTest):
    def setUp(self):
        super(DiscussionDetailTest, self).setUp()
        self.thread = mommy.make(
            'discussion.DiscussionComment',
            matter=self.workspace,
            title='Thread',
            comment='Hello world!',
            participants=(self.lawyer,),
            user=self.lawyer
        )

        self.comment = mommy.make(
            'discussion.DiscussionComment',
            matter=self.workspace,
            parent=self.thread,
            comment='Hello world!',
            user=self.lawyer
        )

        self.forbidden_user = mommy.make('auth.User', username='forbidden-user', email='forbidden+user@lawpal.com')
        self.forbidden_user.set_password(self.password)
        self.forbidden_user.save()

    @property
    def endpoint(self):
        return reverse('discussion-detail', kwargs={ 'matter_slug': self.matter.slug, 'slug': self.thread.slug })

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
        self.client.login(username=self.user.username, password=self.password)

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
        self.client.login(username=self.user.username, password=self.password)

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
        self.client.login(username=self.user.username, password=self.password)

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
        self.client.login(username=self.user.username, password=self.password)

        resp = self.client.delete(self.endpoint, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden


class DiscussionCommentsTest(BaseEndpointTest):
    def setUp(self):
        super(DiscussionCommentsTest, self).setUp()
        self.thread = mommy.make(
            'discussion.DiscussionComment',
            matter=self.workspace,
            title='Thread',
            comment='Hello world!',
            participants=(self.lawyer,),
            user=self.lawyer
        )

        self.comment = mommy.make(
            'discussion.DiscussionComment',
            matter=self.workspace,
            parent=self.thread,
            comment='Hello world!',
            user=self.lawyer
        )

        self.forbidden_user = mommy.make('auth.User', username='forbidden-user', email='forbidden+user@lawpal.com')
        self.forbidden_user.set_password(self.password)
        self.forbidden_user.save()

    @property
    def endpoint(self):
        return reverse('discussion_comment-list', kwargs={ 'matter_slug': self.matter.slug, 'thread_slug': self.thread.slug })

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
        self.client.login(username=self.user.username, password=self.password)

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


class DiscussionCommentDetailTest(BaseEndpointTest):
    def setUp(self):
        super(DiscussionCommentDetailTest, self).setUp()
        self.thread = mommy.make(
            'discussion.DiscussionComment',
            matter=self.workspace,
            title='Thread',
            comment='Hello world!',
            participants=(self.lawyer, self.user),
            user=self.lawyer
        )

        self.comment = mommy.make(
            'discussion.DiscussionComment',
            matter=self.workspace,
            parent=self.thread,
            comment='Hello world!',
            user=self.lawyer
        )

        # Not a matter participant
        self.forbidden_user = mommy.make('auth.User', username='forbidden-user', email='forbidden+user@lawpal.com')
        self.forbidden_user.set_password(self.password)
        self.forbidden_user.save()

        # Not a thread participant
        self.invalid_user = mommy.make('auth.User', username='invalid-user', email='invalid+user@lawpal.com')
        self.invalid_user.set_password(self.password)
        WorkspaceParticipants.objects.create(workspace=self.workspace, user=self.invalid_user, role=ROLES.client)

    @property
    def endpoint(self):
        return reverse('discussion_comment-detail', kwargs={
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


class DiscussionParticipantsTest(BaseEndpointTest):
    def setUp(self):
        super(DiscussionParticipantsTest, self).setUp()
        self.thread = mommy.make(
            'discussion.DiscussionComment',
            matter=self.workspace,
            title='Thread',
            comment='Hello world!',
            participants=(self.lawyer, self.user),
            user=self.lawyer
        )

        self.comment = mommy.make(
            'discussion.DiscussionComment',
            matter=self.workspace,
            parent=self.thread,
            comment='Hello world!',
            user=self.lawyer
        )

        # Not a matter participant
        self.forbidden_user = mommy.make('auth.User', username='forbidden-user', email='forbidden+user@lawpal.com')
        self.forbidden_user.set_password(self.password)
        self.forbidden_user.save()

        # Not a thread participant
        self.invalid_user = mommy.make('auth.User', username='invalid-user', email='invalid+user@lawpal.com')
        self.invalid_user.set_password(self.password)
        WorkspaceParticipants.objects.create(workspace=self.workspace, user=self.invalid_user, role=ROLES.client)

    @property
    def endpoint(self):
        return reverse('discussion_participant-list', kwargs={ 'matter_slug': self.matter.slug, 'thread_slug': self.thread.slug })

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


class DiscussionParticipantDetailTest(BaseEndpointTest):
    def setUp(self):
        super(DiscussionParticipantDetailTest, self).setUp()
        self.thread = mommy.make(
            'discussion.DiscussionComment',
            matter=self.workspace,
            title='Thread',
            comment='Hello world!',
            participants=(self.lawyer,self.user),
            user=self.lawyer
        )

        self.comment = mommy.make(
            'discussion.DiscussionComment',
            matter=self.workspace,
            parent=self.thread,
            comment='Hello world!',
            user=self.lawyer
        )

        # Not a matter participant
        self.forbidden_user = mommy.make('auth.User', username='forbidden-user', email='forbidden+user@lawpal.com')
        self.forbidden_user.set_password(self.password)
        self.forbidden_user.save()

        # Not a thread participant
        self.invalid_user = mommy.make('auth.User', username='invalid-user', email='invalid+user@lawpal.com')
        self.invalid_user.set_password(self.password)
        WorkspaceParticipants.objects.create(workspace=self.workspace, user=self.invalid_user, role=ROLES.client)

    @property
    def endpoint(self):
        return reverse('discussion_participant-detail', kwargs={
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