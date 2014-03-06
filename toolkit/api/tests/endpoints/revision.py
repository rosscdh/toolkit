# -*- coding: utf-8 -*-
from django.test import LiveServerTestCase
from django.core.urlresolvers import reverse
from django.core.files.storage import FileSystemStorage
from django.test.client import MULTIPART_CONTENT

from toolkit.core.item.models import Item

from . import BaseEndpointTest
from ...serializers import ItemSerializer, UserSerializer

from model_mommy import mommy

import mock
import os
import json

TEST_IMAGE_PATH = os.path.join(os.path.dirname(__file__), 'data', 'test-image.png')


class ItemRevisionTest(BaseEndpointTest):
    """
    Test that the matter and its items can be updated with a sort order

    PATCH /matters/:matter_slug/sort
    {
        "categories": ["cat 1", "cat 2", "im not a cat, im a dog"],
        "items": [2,5,7,1,12,22,4]
    }
    """
    # fixtures = ['sites', 'tools', 'dev-fixtures']

    @property
    def endpoint(self):
        return reverse('matter_item_revision', kwargs={'matter_slug': self.matter.slug, 'item_slug': self.item.slug})

    def setUp(self):
        super(ItemRevisionTest, self).setUp()

        # setup the items for testing
        self.item = mommy.make('item.Item', matter=self.matter, name='Test Item with Revision', category=None)

    def test_endpoint_name(self):
        self.assertEqual(self.endpoint, '/api/v1/matters/lawpal-test/items/%s/revision' % self.item.slug)

    def test_no_revision_get(self):
        """
        should return 404 if not present
        """
        self.item.revision_set.all().delete()

        self.client.login(username=self.lawyer.username, password=self.password)
        resp = self.client.get(self.endpoint)

        self.assertEqual(resp.status_code, 404)  # not found

    def test_revision_get(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        revision = mommy.make('attachment.Revision', executed_file=None, slug=None, item=self.item, uploaded_by=self.lawyer)

        resp = self.client.get(self.endpoint)
        resp_json = json.loads(resp.content)

        document_review = revision.reviewdocument_set.all().first()
        # we have a user_review_url
        self.assertFalse(resp_json.get('user_review_url') == None)
        # it is the correct url for this specific user
        self.assertEqual(resp_json.get('user_review_url'), document_review.get_absolute_url(user=self.lawyer))

    def test_revision_post(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        data = {
            'item': ItemSerializer(self.item).data.get('url'),
            'uploaded_by': UserSerializer(self.lawyer).data.get('url')
        }

        resp = self.client.post(self.endpoint, json.dumps(data), content_type='application/json')
        resp_json = json.loads(resp.content)

        self.assertEqual(resp.status_code, 201)  # created
        self.assertEqual(resp_json.get('slug'), 'v1')
        self.assertEqual(self.item.revision_set.all().count(), 1)

    def test_revision_post_increment(self):
        self.client.login(username=self.lawyer.username, password=self.password)
        # set up a preexisting revision
        revision = mommy.make('attachment.Revision', executed_file=None, slug='v1', item=self.item, uploaded_by=self.lawyer)
        self.assertEqual(self.item.revision_set.all().count(), 1)

        data = {
            'item': ItemSerializer(self.item).data.get('url'),
            'uploaded_by': UserSerializer(self.lawyer).data.get('url')
        }

        resp = self.client.post(self.endpoint, json.dumps(data), content_type='application/json')
        resp_json = json.loads(resp.content)

        self.assertEqual(resp.status_code, 201)  # created
        self.assertEqual(resp_json.get('slug'), 'v2')
        self.assertEqual(self.item.revision_set.all().count(), 2)
        # @BUSINESSRULE order is preserved, oldest to newest
        self.assertTrue(all(i.pk == c+1 for c, i in enumerate(self.item.revision_set.all())))


class RevisionExecutedFileAsUrlOrMultipartDataTest(BaseEndpointTest, LiveServerTestCase):
    @property
    def endpoint(self):
        return reverse('matter_item_revision', kwargs={'matter_slug': self.matter.slug, 'item_slug': self.item.slug})

    def setUp(self):
        super(RevisionExecutedFileAsUrlOrMultipartDataTest, self).setUp()
        # setup the items for testing
        self.item = mommy.make('item.Item', matter=self.matter, name='Test Item with Revision', category=None)
        revision = mommy.make('attachment.Revision', executed_file=None, slug=None, item=self.item, uploaded_by=self.lawyer)

    def test_endpoint_name(self):
        self.assertEqual(self.endpoint, '/api/v1/matters/lawpal-test/items/%s/revision' % self.item.slug)

    @mock.patch('storages.backends.s3boto.S3BotoStorage', FileSystemStorage)
    def test_patch_with_URL_executed_file(self):
        """
        complicated: upload a file based on a filepicker.io url (or any url as below)
        which will then download that file in the bg and upload to s3 (async)
        this tests expects that the revision.HyperlinkedAutoDownloadFileField is working
        @NOTE: could NOT get httpretty working together with mock.patch for S3BotoStorage :(
        """
        expected_image_url = 'http://localhost:8081/static/images/logo-white.png'

        self.client.login(username=self.lawyer.username, password=self.password)

        data = {
            'executed_file': expected_image_url,
        }

        resp = self.client.patch(self.endpoint, json.dumps(data), content_type='application/json')
        resp_json = json.loads(resp.content)

        self.assertEqual(resp.status_code, 200)  # ok updated
        self.assertEqual(resp_json.get('slug'), 'v1')
        self.assertEqual(self.item.revision_set.all().count(), 1)

        # refresh
        self.item = Item.objects.get(pk=self.item.pk)
        revision = self.item.revision_set.all().first()
        self.assertEqual(revision.executed_file.name, 'executed_files/v1-1-%s-logo-white.png' % self.lawyer.username)
        self.assertEqual(revision.executed_file.url, 'https://dev-toolkit-lawpal-com.s3.amazonaws.com/executed_files/v1-1-%s-logo-white.png' % self.lawyer.username)

    @mock.patch('storages.backends.s3boto.S3BotoStorage', FileSystemStorage)
    def test_patch_with_FILE_executed_file(self):
        """
        ensure we can upload an actual file to the endpoint
        """
        self.client.login(username=self.lawyer.username, password=self.password)

        self.item.revision_set.all().delete()

        with open(TEST_IMAGE_PATH) as file_being_posted:
            data = {
                'executed_file': file_being_posted,
            }
            #
            # NB. uploading files must be a patch
            #
            self.assertEqual(self.item.revision_set.all().count(), 0)
            resp = self.client.post(self.endpoint, data, content_type=MULTIPART_CONTENT)
        resp_json = json.loads(resp.content)

        self.assertEqual(resp.status_code, 201)  # created
        self.assertEqual(resp_json.get('slug'), 'v1')
        self.assertEqual(self.item.revision_set.all().count(), 1)


