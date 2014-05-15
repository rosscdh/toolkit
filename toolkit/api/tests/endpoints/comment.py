# -*- coding: utf-8 -*-
import datetime
from django.conf import settings
from django.utils import timezone
from actstream.models import Action
from django.core.urlresolvers import reverse

from . import BaseEndpointTest

from model_mommy import mommy

import json


class CommentTest(BaseEndpointTest):
    """
    /comment/ (POST, DELETE)
        create comments

    (GET not needed, because comments are saved as actions)
    """
    def setUp(self):
        super(CommentTest, self).setUp()
        self.item = mommy.make('item.Item', matter=self.workspace, name='Comment Test Item #1')

    @property
    def endpoint(self):
        return reverse('item_comment', kwargs={'matter_slug': self.matter.slug, 'item_slug': self.item.slug})

    def test_endpoint_name(self):
        self.assertEqual(self.endpoint, '/api/v1/matters/%(matter_slug)s/items/%(item_slug)s/comment' % {
            'matter_slug': self.matter.slug,
            'item_slug': self.item.slug,
        })

    def test_empty_post(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        data = {
            "comment": ""
        }
        resp = self.client.post(self.endpoint, json.dumps(data), content_type='application/json')

        self.assertEqual(resp.status_code, 400)  # bad request

    def test_lawyer_post(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        data = {
            "comment": "The rain in spain, falls mainly on a monkey."
        }
        resp = self.client.post(self.endpoint, json.dumps(data), content_type='application/json')

        self.assertEqual(resp.status_code, 201)  # created

    def test_lawyer_patch(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        # post comment
        data = {
            "comment": "The rain in spain, falls mainly on a monkey."
        }
        resp = self.client.post(self.endpoint, json.dumps(data), content_type='application/json')

        # load the newly created comment and check if it was saved
        comment_object = Action.objects.first()
        self.assertEqual(comment_object.data.get('comment'), "The rain in spain, falls mainly on a monkey.")

        # patch the comment with its id
        data = {
            "comment": "The rain in france, falls mainly on a baguette."
        }
        patch_endpoint = reverse('item_comment', kwargs={'matter_slug': self.matter.slug,
                                                         'item_slug': self.item.slug,
                                                         'id': comment_object.id})
        resp = self.client.patch(patch_endpoint, json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 200)  # ok

        # reload object and check if change was saved
        comment_object = Action.objects.get(id=comment_object.id)
        self.assertEqual(comment_object.data.get('comment'), "The rain in france, falls mainly on a baguette.")

    def test_lawyer_patch_not_allowed(self):
        # create comment and patch as other user which should not be allowed
        self.client.login(username=self.user.username, password=self.password)

        comment1 = mommy.make('actstream.Action',
                              actor=self.lawyer,
                              verb=u'commented',
                              action_object=self.item,
                              target=self.matter,
                              data={'comment': u'I"m a test comment by lawyer'})

        # patch comment1 should not be allowed because it is not mine
        resp = self.client.patch(reverse('item_comment', kwargs={'matter_slug': self.matter.slug,
                                                                 'item_slug': self.item.slug,
                                                                 'id': comment1.id}),
                                 json.dumps({"comment": "The rain in france, falls mainly on a baguette."}),
                                 content_type='application/json')
        self.assertEqual(resp.status_code, 403)

        comment2 = mommy.make('actstream.Action',
                              actor=self.user,
                              verb=u'commented',
                              action_object=self.item,
                              target=self.matter,
                              timestamp=timezone.now() - datetime.timedelta(minutes=settings.EDIT_COMMENTS_DURATION + 10),
                              data={'comment': u'I"m a test comment #2 by user'})
        comment3 = mommy.make('actstream.Action',
                              actor=self.user,
                              verb=u'commented',
                              action_object=self.item,
                              target=self.matter,
                              data={'comment': u'I"m a test comment #3 by user'})

        # patch comment2 should not be allowed because it is too old
        resp = self.client.patch(reverse('item_comment', kwargs={'matter_slug': self.matter.slug,
                                                                 'item_slug': self.item.slug,
                                                                 'id': comment2.id}),
                                 json.dumps({"comment": "The rain in france, falls mainly on a baguette."}),
                                 content_type='application/json')
        self.assertEqual(resp.status_code, 403)
    # def test_lawyer_patch_not_allowed(self):
    #     # create comment and patch as other user which should not be allowed
    #     self.client.login(username=self.user.username, password=self.password)
    #
    #     comment1 = mommy.make('actstream.Action',
    #                           actor=self.lawyer,
    #                           verb=u'commented',
    #                           action_object=self.item,
    #                           target=self.matter,
    #                           data={'comment': u'I"m a test comment by lawyer'})
    #
    #     # patch comment1 should not be allowed because it is not mine
    #     resp = self.client.patch(reverse('item_comment', kwargs={'matter_slug': self.matter.slug,
    #                                                              'item_slug': self.item.slug,
    #                                                              'id': comment1.id}),
    #                              json.dumps({"comment": "The rain in france, falls mainly on a baguette."}),
    #                              content_type='application/json')
    #     self.assertEqual(resp.status_code, 403)
    #
    #     comment2 = mommy.make('actstream.Action',
    #                           actor=self.user,
    #                           verb=u'commented',
    #                           action_object=self.item,
    #                           target=self.matter,
    #                           data={'comment': u'I"m a test comment #2 by user'})
    #     comment3 = mommy.make('actstream.Action',
    #                           actor=self.user,
    #                           verb=u'commented',
    #                           action_object=self.item,
    #                           target=self.matter,
    #                           data={'comment': u'I"m a test comment #3 by user'})
    #
    #     # patch comment2 should not be allowed because it is not my newest
    #     resp = self.client.patch(reverse('item_comment', kwargs={'matter_slug': self.matter.slug,
    #                                                              'item_slug': self.item.slug,
    #                                                              'id': comment2.id}),
    #                              json.dumps({"comment": "The rain in france, falls mainly on a baguette."}),
    #                              content_type='application/json')
    #     self.assertEqual(resp.status_code, 403)

    def test_lawyer_delete(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        comment1 = mommy.make('actstream.Action',
                              actor=self.user,
                              verb=u'commented',
                              action_object=self.item,
                              target=self.matter,
                              data={'comment': u'I"m a test comment #1'})

        resp = self.client.delete(reverse('item_comment', kwargs={'matter_slug': self.matter.slug,
                                                                  'item_slug': self.item.slug,
                                                                  'id': comment1.id}),
                                  json.dumps({}),
                                  content_type='application/json')
        self.assertEqual(resp.status_code, 204)

    def test_customer_post(self):
        self.client.login(username=self.user.username, password=self.password)

        data = {
            "comment": "The rain in spain, falls mainly on a monkey."
        }
        resp = self.client.post(self.endpoint, json.dumps(data), content_type='application/json')

        self.assertEqual(resp.status_code, 201)  # created

    def test_customer_delete(self):
        self.client.login(username=self.user.username, password=self.password)

        comment1 = mommy.make('actstream.Action',
                              actor=self.user,
                              verb=u'commented',
                              action_object=self.item,
                              target=self.matter,
                              data={'comment': u'I"m a test comment #1'})
        comment2 = mommy.make('actstream.Action',
                              actor=self.user,
                              verb=u'commented',
                              action_object=self.item,
                              target=self.matter,
                              data={'comment': u'I"m a test comment #2'})

        # delete
        resp = self.client.delete(reverse('item_comment', kwargs={'matter_slug': self.matter.slug,
                                                                  'item_slug': self.item.slug,
                                                                  'id': comment2.id}),
                                  json.dumps({}),
                                  content_type='application/json')
        self.assertEqual(resp.status_code, 204)

        # delete
        resp = self.client.delete(reverse('item_comment', kwargs={'matter_slug': self.matter.slug,
                                                                  'item_slug': self.item.slug,
                                                                  'id': comment1.id}),
                                  json.dumps({}),
                                  content_type='application/json')
        self.assertEqual(resp.status_code, 204)

        result = Action.objects.deleted()
        self.assertEqual(len(result), 2)

    def test_customer_delete_forbidden(self):
        # create comment
        self.client.login(username=self.user.username, password=self.password)

        comment1 = mommy.make('actstream.Action',
                              actor=self.user,
                              verb=u'commented',
                              action_object=self.item,
                              target=self.matter,
                              timestamp=timezone.now() - datetime.timedelta(minutes=settings.DELETE_COMMENTS_DURATION + 10),
                              data={'comment': u'I"m a test comment #1'})
        comment2 = mommy.make('actstream.Action',
                              actor=self.user,
                              verb=u'commented',
                              action_object=self.item,
                              target=self.matter,
                              data={'comment': u'I"m a test comment #2'})

        # delete too old comment
        resp = self.client.delete(reverse('item_comment', kwargs={'matter_slug': self.matter.slug,
                                                                  'item_slug': self.item.slug,
                                                                  'id': comment1.id}),
                                  json.dumps({}),
                                  content_type='application/json')
        self.assertEqual(resp.status_code, 403)

        # delete
        resp = self.client.delete(reverse('item_comment', kwargs={'matter_slug': self.matter.slug,
                                                                  'item_slug': self.item.slug,
                                                                  'id': comment2.id}),
                                  json.dumps({}),
                                  content_type='application/json')
        self.assertEqual(resp.status_code, 204)

        result = Action.objects.deleted()
        self.assertEqual(len(result), 1)

    def test_anon_post(self):
        data = {
            "comment": "The rain in spain, falls mainly on a monkey."
        }
        resp = self.client.post(self.endpoint, json.dumps(data), content_type='application/json')

        self.assertEqual(resp.status_code, 403)  # forbidden