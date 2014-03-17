# -*- coding: utf-8 -*-
from django.test import LiveServerTestCase
from django.core.urlresolvers import reverse
from django.core.files.storage import FileSystemStorage
from django.test.client import MULTIPART_CONTENT

from toolkit.core.item.models import Item

from . import BaseEndpointTest
from ...serializers import ItemSerializer, UserSerializer, SimpleUserSerializer

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
    version_no = 1
    expected_num = 1
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

        revision = mommy.make('attachment.Revision',
                              executed_file=None,
                              slug=None,
                              name='filename.txt',
                              description='A test file',
                              item=self.item,
                              uploaded_by=self.lawyer)

        resp = self.client.get(self.endpoint)
        resp_json = json.loads(resp.content)

        document_review = revision.reviewdocument_set.all().first()

        self.assertEqual(resp_json.get('name'), 'filename.txt')
        self.assertEqual(resp_json.get('description'), 'A test file')
        # we have a user_review_url
        self.assertTrue(resp_json.get('user_review_url') is not None)
        # it is the correct url for this specific user
        self.assertEqual(resp_json.get('user_review_url'), document_review.get_absolute_url(user=self.lawyer))
        # test date is present
        self.assertTrue(resp_json.get('date_created') is not None)
        # test user is provided as a SimpleUserserializer
        # and has the correct keys
        provided_keys = resp_json.get('uploaded_by').keys()
        provided_keys.sort()
        expected_keys = SimpleUserSerializer(self.lawyer).data.keys()
        expected_keys.sort()
        self.assertEqual(provided_keys, expected_keys)


    def test_revision_post_with_url(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        data = {
            'item': ItemSerializer(self.item).data.get('url'),
            'uploaded_by': UserSerializer(self.lawyer).data.get('url')
        }

        resp = self.client.post(self.endpoint, json.dumps(data), content_type='application/json')
        resp_json = json.loads(resp.content)

        self.assertEqual(resp.status_code, 201)  # created
        self.assertEqual(resp_json.get('slug'), 'v%d' % self.version_no)
        self.assertEqual(self.item.revision_set.all().count(), self.expected_num)

    def test_revision_post_increment_with_url(self):
        self.client.login(username=self.lawyer.username, password=self.password)
        # set up a preexisting revision
        mommy.make('attachment.Revision', executed_file=None, item=self.item, uploaded_by=self.lawyer)
        self.assertEqual(self.item.revision_set.all().count(), self.expected_num)

        data = {
            'item': ItemSerializer(self.item).data.get('url'),
            'uploaded_by': UserSerializer(self.lawyer).data.get('url')
        }

        resp = self.client.post(self.endpoint, json.dumps(data), content_type='application/json')
        resp_json = json.loads(resp.content)

        self.assertEqual(resp.status_code, 201)  # created

        self.assertEqual(resp_json.get('slug'), 'v%s' % str(self.version_no + 1))
        self.assertEqual(self.item.revision_set.all().count(), self.expected_num + 1)
        # @BUSINESSRULE order is preserved, oldest to newest
        self.assertTrue(all(i.slug == 'v%s' % str(c+1) for c, i in enumerate(self.item.revision_set.all())))


class ItemSubRevision2Test(ItemRevisionTest):
    version_no = 2
    expected_num = 2

    @property
    def endpoint(self):
        return reverse('matter_item_specific_revision', kwargs={'matter_slug': self.matter.slug, 'item_slug': self.item.slug, 'version': self.version_no})

    def setUp(self):
        super(ItemSubRevision2Test, self).setUp()
        # setup the items for testing
        self.item = mommy.make('item.Item', matter=self.matter, name='Test Item with Revision', category=None)
        mommy.make('attachment.Revision', executed_file=None, slug=None, item=self.item, uploaded_by=self.lawyer)

    def test_endpoint_name(self):
        self.assertEqual(self.endpoint, '/api/v1/matters/lawpal-test/items/%s/revision/v%d' % (self.item.slug, self.version_no))


class ItemSubRevision3Test(ItemSubRevision2Test):
    version_no = 3
    expected_num = 3

    def setUp(self):
        super(ItemSubRevision3Test, self).setUp()
        # setup the items for testing
        self.item = mommy.make('item.Item', matter=self.matter, name='Test Item with Revision', category=None)
        mommy.make('attachment.Revision', executed_file=None, slug=None, item=self.item, uploaded_by=self.lawyer)
        mommy.make('attachment.Revision', executed_file=None, slug=None, item=self.item, uploaded_by=self.lawyer)

    def test_endpoint_name(self):
        self.assertEqual(self.endpoint, '/api/v1/matters/lawpal-test/items/%s/revision/v%d' % (self.item.slug, self.version_no))


class RevisionExecutedFileAsUrlOrMultipartDataTest(BaseEndpointTest, LiveServerTestCase):
    @property
    def endpoint(self):
        return reverse('matter_item_revision', kwargs={'matter_slug': self.matter.slug, 'item_slug': self.item.slug})

    def setUp(self):
        super(RevisionExecutedFileAsUrlOrMultipartDataTest, self).setUp()
        # setup the items for testing
        self.item = mommy.make('item.Item', matter=self.matter, name='Test Item with Revision', category=None)

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
        # normally there is no logo-white.png from filepicker io it sends name seperately
        # but for our tests we need to fake this out
        expected_image_url = 'http://localhost:8081/static/images/logo-white.png'
        expected_file_name = 'logo-black.png'

        self.client.login(username=self.lawyer.username, password=self.password)

        #
        # Filepicker IO sends us a url with no filename and or suffix that we use
        # but they do send us the name of the file that was uploaded so lets use that
        #
        data = {
            'executed_file': expected_image_url,
            'name': expected_file_name
        }
        #
        # @BUSINESSRULE if you are sending a url of a file that needs to be download
        # ie. filepicker.io then the CONTENT_TYPE must be application/json and
        # the field "executed_file": "http://example.com/myfile.pdf"
        #
        resp = self.client.patch(self.endpoint, json.dumps(data), content_type='application/json')
        resp_json = json.loads(resp.content)
        
        self.assertEqual(resp.status_code, 201)  # ok created

        self.assertEqual(resp_json.get('slug'), 'v1')
        self.assertEqual(resp_json.get('executed_file'), 'https://dev-toolkit-lawpal-com.s3.amazonaws.com/executed_files/v1-1-%s-logo-black.png' % self.lawyer.username)
        self.assertEqual(self.item.revision_set.all().count(), 1)

        # refresh
        self.item = Item.objects.get(pk=self.item.pk)
        revision = self.item.revision_set.all().first()
        self.assertEqual(revision.executed_file.name, 'executed_files/v1-1-%s-logo-black.png' % self.lawyer.username)
        self.assertEqual(revision.executed_file.url, 'https://dev-toolkit-lawpal-com.s3.amazonaws.com/executed_files/v1-1-%s-logo-black.png' % self.lawyer.username)

    @mock.patch('storages.backends.s3boto.S3BotoStorage', FileSystemStorage)
    def test_post_with_URL_executed_file(self):
        """
        POSTING and PATCHING to the endpoint BOTH return a "new" revision with the slug
        changing to v2..v3..etc
        This is confusing but is important for history preservation
        """
        mommy.make('attachment.Revision', executed_file=None, slug=None, item=self.item, uploaded_by=self.lawyer)

        expected_image_url = 'http://localhost:8081/static/images/logo-white.png'

        self.client.login(username=self.lawyer.username, password=self.password)

        data = {
            'executed_file': expected_image_url,
        }
        resp = self.client.patch(self.endpoint, json.dumps(data), content_type='application/json')
        resp_json = json.loads(resp.content)

        self.assertEqual(resp.status_code, 200)  # updated but actually a new one was created
        self.assertEqual(resp_json.get('slug'), 'v2')

    @mock.patch('storages.backends.s3boto.S3BotoStorage', FileSystemStorage)
    def test_patch_with_FILE_executed_file(self):
        """
        ensure we can upload an actual file to the endpoint
        """
        self.client.login(username=self.lawyer.username, password=self.password)

        with open(TEST_IMAGE_PATH) as file_being_posted:
            data = {
                'executed_file': file_being_posted,
            }
            #
            # NB. uploading files must be a patch
            #
            self.assertEqual(self.item.revision_set.all().count(), 0)
            #
            # @BUSINESSRULE if you are sending a binary file that needs to be download
            # ie. plain post then the CONTENT_TYPE must be MULTIPART_CONTENT and
            # the field "executed_file": a binary file object
            #
            resp = self.client.post(self.endpoint, data, content_type=MULTIPART_CONTENT)
        resp_json = json.loads(resp.content)


        self.assertEqual(resp.status_code, 201)  # created
        self.assertEqual(resp_json.get('slug'), 'v1')
        self.assertEqual(resp_json.get('name'), 'test-image.png')
        self.assertEqual(resp_json.get('executed_file'), 'https://dev-toolkit-lawpal-com.s3.amazonaws.com/executed_files/v1-1-%s-test-image.png' % self.lawyer.username)
        self.assertEqual(self.item.revision_set.all().count(), 1)

        revision = self.item.revision_set.all().first()
        self.assertEqual(revision.executed_file.name, 'executed_files/v1-1-%s-test-image.png' % self.lawyer.username)
        self.assertEqual(revision.executed_file.url, 'https://dev-toolkit-lawpal-com.s3.amazonaws.com/executed_files/v1-1-%s-test-image.png' % self.lawyer.username)
