# -*- coding: utf-8 -*-
from django.core.files import File
from django.core.urlresolvers import reverse
from django.core.files.storage import FileSystemStorage

from . import BaseEndpointTest
from .revision import TEST_IMAGE_PATH

from model_mommy import mommy

import mock
import json


class RevisionReviewsTest(BaseEndpointTest):
    """
    /matters/:matter_slug/items/:item_slug/revision/reviewers/ (GET,POST)
        [lawyer,customer] to list, create reviewers
    """
    @property
    def endpoint(self):
        return reverse('item_revision_reviewers', kwargs={'matter_slug': self.matter.slug, 'item_slug': self.item.slug})

    @mock.patch('storages.backends.s3boto.S3BotoStorage', FileSystemStorage)
    def setUp(self):
        super(RevisionReviewTest, self).setUp()

        # setup the items for testing
        self.item = mommy.make('item.Item', matter=self.matter, name='Test Item with Revision', category=None)
        self.revision = mommy.make('attachment.Revision', executed_file=None, slug=None, item=self.item, uploaded_by=self.lawyer)

    def test_endpoint_name(self):
        self.assertEqual(self.endpoint, '/api/v1/matters/%s/items/%s/revision/reviewers' % (self.matter.slug, self.item.slug))

    def test_lawyer_get_no_participants(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        resp = self.client.get(self.endpoint)
        self.assertEqual(resp.status_code, 200)

        json_data = json.loads(resp.content)
        self.assertEqual(json_data['count'], 0)

    def test_lawyer_post(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        participant = mommy.make('auth.User', first_name='Participant', last_name='Number 1', email='participant+1@lawpal.com')

        data = {
            "username": participant.username
        }
        resp = self.client.post(self.endpoint, json.dumps(data), content_type='application/json')

        self.assertEqual(resp.status_code, 201)  # created

        json_data = json.loads(resp.content)
        self.assertEqual(json_data['name'], participant.get_full_name())
        # test they are in the items reviewer set
        self.assertTrue(participant in self.item.latest_revision.reviewers.all())

        #
        # Test they show in the GET
        #
        resp = self.client.get(self.endpoint)

        self.assertEqual(resp.status_code, 200)

        json_data = json.loads(resp.content)
        self.assertEqual(json_data['count'], 1)
        self.assertEqual(json_data['results'][0]['name'], participant.get_full_name())


    def test_lawyer_patch(self):
        self.client.login(username=self.lawyer.username, password=self.password)
        resp = self.client.patch(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 405)  # not allowed

    def test_lawyer_delete(self):
        self.client.login(username=self.lawyer.username, password=self.password)
        resp = self.client.delete(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 405)  # not allowed


    def test_customer_get(self):
        self.client.login(username=self.user.username, password=self.password)
        resp = self.client.get(self.endpoint)
        self.assertEqual(resp.status_code, 200)  # customers can see

    def test_customer_post(self):
        self.client.login(username=self.user.username, password=self.password)
        resp = self.client.post(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_customer_patch(self):
        self.client.login(username=self.user.username, password=self.password)
        resp = self.client.patch(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_customer_delete(self):
        self.client.login(username=self.user.username, password=self.password)
        resp = self.client.delete(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_anon_get(self):
        resp = self.client.get(self.endpoint)
        self.assertEqual(resp.status_code, 401)  # unauthorized

    def test_anon_post(self):
        resp = self.client.post(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 401)  # unauthorized

    def test_anon_patch(self):
        resp = self.client.patch(self.endpoint, {})
        self.assertEqual(resp.status_code, 401)  # unauthorized

    def test_anon_delete(self):
        resp = self.client.delete(self.endpoint, {})
        self.assertEqual(resp.status_code, 401)  # unauthorized


class RevisionReviewerTest(BaseEndpointTest):
    """
    /matters/:matter_slug/items/:item_slug/revision/reviewer/:username (GET,DELETE)
        [lawyer,customer] to view, delete reviewers
    """
    @property
    def endpoint(self):
        return reverse('item_revision_reviewer', kwargs={'matter_slug': self.matter.slug, 'item_slug': self.item.slug, 'username': self.participant.username})

    @mock.patch('storages.backends.s3boto.S3BotoStorage', FileSystemStorage)
    def setUp(self):
        super(RevisionReviewerTest, self).setUp()

        # setup the items for testing
        self.item = mommy.make('item.Item', matter=self.matter, name='Test Item with Revision', category=None)
        self.revision = mommy.make('attachment.Revision', executed_file=None, slug=None, item=self.item, uploaded_by=self.lawyer)
        self.participant = mommy.make('auth.User', first_name='Participant', last_name='Number 1', email='participant+1@lawpal.com')

    def test_endpoint_name(self):
        self.assertEqual(self.endpoint, '/api/v1/matters/%s/items/%s/revision/reviewer/%s' % (self.matter.slug, self.item.slug, self.participant.username))


