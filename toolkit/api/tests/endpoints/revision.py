# -*- coding: utf-8 -*-
from django.conf import settings
from django.db.models import SET_NULL
from django.test import LiveServerTestCase
from rest_framework.reverse import reverse
from django.test.client import MULTIPART_CONTENT
from actstream.models import target_stream

from . import BaseEndpointTest
from ...serializers import ItemSerializer, UserSerializer, SimpleUserSerializer
from ...serializers.revision import MAX_LENGTH_FILENAME

from model_mommy import mommy

import os
import json
import urllib

# Images are NOT valid filetypes to upload
TEST_INVALID_UPLOAD_IMAGE_PATH = os.path.join(os.path.dirname(__file__), 'data', 'test-image.png')
# Pdfs ARE valid filetypes
TEST_PDF_PATH = os.path.join(settings.SITE_ROOT, 'toolkit', 'casper', 'test.pdf')
TEST_LONG_FILENAME_PATH = os.path.join(settings.SITE_ROOT, 'toolkit', 'casper', 'test-long-filename-@-(LawPal)-#1236202-v1-test-long-filename-@-(LawPal)-#1236202-v1-test-long-filename-@-(LawPal)-#1236202-v1-test-long-filename-@-(LawPal)-#1236202-v1-test-long-filename-@-(LawPal)-#1236202-v1-.doc')


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
        #
        # Add a reviewer so we can test the specific user_review
        #
        reviewer = mommy.make('auth.User')
        revision.reviewers.add(reviewer)

        resp = self.client.get(self.endpoint)
        resp_json = json.loads(resp.content)

        # should be the last object in the set as the default one created for the reviewers
        document_review = revision.reviewdocument_set.all().last()
        # first in this case because there are only 2 in our tests case
        invited_reviewer_document_review = revision.reviewdocument_set.all().first()

        self.assertEqual(resp_json.get('name'), 'filename.txt')
        self.assertEqual(resp_json.get('description'), 'A test file')
        # we have a user_review
        self.assertTrue(resp_json.get('user_review') is not None)
        # it is the correct url for this specific user to view object
        self.assertEqual(resp_json.get('user_review'), {
            'url': document_review.get_absolute_url(user=self.lawyer),
            'slug': str(document_review.slug)
        })

        # test date is present
        self.assertTrue(resp_json.get('date_created') is not None)
        # test user is provided as a SimpleUserserializer
        # and has the correct keys
        provided_keys = resp_json.get('uploaded_by').keys()
        provided_keys.sort()
        expected_keys = SimpleUserSerializer(self.lawyer).data.keys()
        expected_keys.sort()
        self.assertEqual(provided_keys, expected_keys)

        # Test the reviewers and the relative user_reivew_url (should be the current logged in users)
        self.assertEqual(len(resp_json.get('reviewers')), 1)

        # Test the reviewers section
        reviewers = resp_json.get('reviewers')

        # should only have 1 reviewer, ever
        self.assertEqual(len(reviewers), 1)
        # get that person
        resp_reviewer = reviewers[0].get('reviewer')
        # test their url
        self.assertTrue(type(resp_reviewer.get('user_review')) is dict)
        # it is the correct url for this specific user to view object in this case the lawyer is looking at this review
        # not this is a head trip, but the viewing user should only EVER see THEIR url to that document
        self.assertEqual(resp_reviewer.get('user_review'), {
            'url': invited_reviewer_document_review.get_absolute_url(user=self.lawyer),
            'slug': str(invited_reviewer_document_review.slug)
        })

        # ensure that the user_review is never the actual reviewers url that gets sent out
        for rd in revision.reviewdocument_set.all():
            self.assertTrue(resp_reviewer.get('user_review') != rd.get_user_auth(user=reviewer))

        # ensure that the reviewer user does have a url in the appropriate object
        self.assertTrue(invited_reviewer_document_review.get_absolute_url(user=reviewer) is not None)
        # must be a string as we store the pk in as a string
        self.assertTrue(str(reviewer.pk) in invited_reviewer_document_review.auth.keys())
        # test that the url for the reviewer is correct
        self.assertEqual(invited_reviewer_document_review.get_absolute_url(user=reviewer),
                         'http://localhost:8000/review/%s/%s/' % (
                             invited_reviewer_document_review.slug,
                             urllib.quote(invited_reviewer_document_review.get_user_auth(user=reviewer))
                         ))

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

        self.item = self.item.__class__.objects.get(pk=self.item.pk)  # reset
        self.assertEqual(self.item.review_percentage_complete, None)  # test review_percentage_complete is reset

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

        self.item = self.item.__class__.objects.get(pk=self.item.pk)  # reset
        self.assertEqual(self.item.review_percentage_complete, None)  # test review_percentage_complete is reset


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


class RevisionExecutedFileAsUrlOrMultipartDataTest(BaseEndpointTest,
                                                   LiveServerTestCase):
    FILE_TO_TEST_UPLOAD_WITH = TEST_PDF_PATH
    TEST_LONG_FILENAME_PATH = TEST_LONG_FILENAME_PATH

    @property
    def endpoint(self):
        return reverse('matter_item_revision', kwargs={'matter_slug': self.matter.slug, 'item_slug': self.item.slug})

    def setUp(self):
        super(RevisionExecutedFileAsUrlOrMultipartDataTest, self).setUp()
        # setup the items for testing
        self.item = mommy.make('item.Item', matter=self.matter, name='Test Item with Revision', category=None)

    def test_endpoint_name(self):
        self.assertEqual(self.endpoint, '/api/v1/matters/lawpal-test/items/%s/revision' % self.item.slug)

    def test_patch_with_URL_executed_file(self):
        """
        complicated: upload a file based on a filepicker.io url (or any url as below)
        which will then download that file in the bg and upload to s3 (async)
        this tests expects that the revision.HyperlinkedAutoDownloadFileField is working
        @NOTE: could NOT get httpretty working together with mock.patch for S3BotoStorage :(
        """
        # normally there is no logo-white.png from filepicker io it sends name seperately
        # but for our tests we need to fake this out
        expected_image_url = 'http://localhost:8081/static/test.pdf'
        expected_file_name = 'test-pirates-ahoy.pdf'  # test renaming

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
        resp = self.client.post(self.endpoint, json.dumps(data), content_type='application/json')
        resp_json = json.loads(resp.content)

        self.assertEqual(resp.status_code, 201)  # ok created

        self.assertEqual(resp_json.get('slug'), 'v1')

        #self.assertEqual(resp_json.get('executed_file'), 'https://dev-toolkit-lawpal-com.s3.amazonaws.com/executed_files/v1-%s-%s-test-pirates-ahoy.pdf' % (self.item.pk, self.lawyer.username))
        # NB: the media path is local here as we use the localstorage for test environment so what were really testing is the upload_to path
        self.assertEqual(resp_json.get('executed_file'), u'/m/executed_files/v1-%s-%s-test-pirates-ahoy.pdf' % (self.item.pk, self.lawyer.username))
        self.assertEqual(self.item.revision_set.all().count(), 1)

        # refresh
        self.item = self.item.__class__.objects.get(pk=self.item.pk)  # reset
        revision = self.item.revision_set.all().first()
        self.assertEqual(revision.executed_file.name, 'executed_files/v1-%s-%s-test-pirates-ahoy.pdf' % (self.item.pk, self.lawyer.username))
        #self.assertEqual(revision.executed_file.url, 'https://dev-toolkit-lawpal-com.s3.amazonaws.com/executed_files/v1-%s-%s-test-pirates-ahoy.pdf' % (self.item.pk, self.lawyer.username))
        # NB: the media path is local here as we use the localstorage for test environment so what were really testing is the upload_to path
        self.assertEqual(revision.executed_file.url, u'/m/executed_files/v1-%s-%s-test-pirates-ahoy.pdf' % (self.item.pk, self.lawyer.username))

        self.assertEqual(self.item.review_percentage_complete, None)  # test review_percentage_complete is reset

    def test_post_with_URL_executed_file(self):
        """
        POSTING and PATCHING to the endpoint BOTH return a "new" revision with the slug
        changing to v2..v3..etc
        This is confusing but is important for history preservation
        """
        mommy.make('attachment.Revision', executed_file=None, slug=None, item=self.item, uploaded_by=self.lawyer)

        expected_image_url = 'http://localhost:8081/static/test.pdf'

        self.client.login(username=self.lawyer.username, password=self.password)

        data = {
            'executed_file': expected_image_url,
        }
        resp = self.client.post(self.endpoint, json.dumps(data), content_type='application/json')
        resp_json = json.loads(resp.content)

        self.assertEqual(resp.status_code, 201)  # 201 created
        self.assertEqual(resp_json.get('slug'), 'v2')

        self.item = self.item.__class__.objects.get(pk=self.item.pk)  # reset
        self.assertEqual(self.item.review_percentage_complete, None)  # test review_percentage_complete is reset

    def test_post_with_FILE_executed_file(self):
        """
        ensure we can upload an actual file to the endpoint
        """
        self.client.login(username=self.lawyer.username, password=self.password)

        with open(self.FILE_TO_TEST_UPLOAD_WITH) as file_being_posted:
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
        self.assertEqual(resp_json.get('name'), 'test.pdf')
        self.assertEqual(resp_json.get('executed_file'), '/m/executed_files/v1-%s-%s-test.pdf' % (self.item.pk, self.lawyer.username))
        self.assertEqual(self.item.revision_set.all().count(), 1)

        revision = self.item.revision_set.all().first()

        self.assertEqual(revision.executed_file.name, 'executed_files/v1-%s-%s-test.pdf' % (self.item.pk, self.lawyer.username))
        self.assertEqual(revision.executed_file.url, '/m/executed_files/v1-%s-%s-test.pdf' % (self.item.pk, self.lawyer.username))

        self.item = self.item.__class__.objects.get(pk=self.item.pk)  # reset
        self.assertEqual(self.item.review_percentage_complete, None)  # test review_percentage_complete is reset

    def test_post_with_LONG_filename(self):
        """
        ensure we can upload an actual file to the endpoint
        """
        self.assertEqual(MAX_LENGTH_FILENAME, 50)  # should be as short as possible to allow for, upload_to path as well as extension and other attribs

        self.client.login(username=self.lawyer.username, password=self.password)

        with open(self.TEST_LONG_FILENAME_PATH) as file_being_posted:
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
        self.assertEqual(resp_json.get('name'), u'test-long-filename-@-(LawPal)-#1236202-v1-test-lon.doc')
        # self.assertEqual(resp_json.get('executed_file'), u'https://dev-toolkit-lawpal-com.s3.amazonaws.com/executed_files/v1-%s-%s-test-long-filename-lawpal-1236202-v1-test-lon.doc' % (self.item.pk, self.lawyer.username))
        self.assertEqual(resp_json.get('executed_file'), u'/m/executed_files/v1-%s-%s-test-long-filename-lawpal-1236202-v1-test-lon.doc' % (self.item.pk, self.lawyer.username))
        self.assertEqual(self.item.revision_set.all().count(), 1)

    def test_post_with_URL_executed_file_and_stream(self):
        self.test_post_with_URL_executed_file()
        stream = target_stream(self.matter)
        self.assertEqual(stream[0].data['override_message'],
                         u'Lawyër Tëst added a file to Test Item with Revision')


    def test_post_with_FILE_executed_file_and_stream(self):
        self.test_post_with_FILE_executed_file()
        stream = target_stream(self.matter)
        self.assertEqual(stream[0].data['override_message'],
                         u'Lawyër Tëst added a file to Test Item with Revision')

        revision = self.item.revision_set.all().first()

        self.assertEqual(revision.executed_file.name, 'executed_files/v1-%s-%s-test.pdf' % (self.item.pk, self.lawyer.username))
        self.assertEqual(revision.executed_file.url, '/m/executed_files/v1-%s-%s-test.pdf' % (self.item.pk, self.lawyer.username))

    def test_requested_revision_upload(self):
        """
        what should happen here:
        - create an invitation
        - login as invited user
        - upload a file
        - check in stream if toolkit/api/views/revision.py line 130 worked
        """
        # @TODO ross
        self.skipTest('todo for ross')

        self.assertEqual(revision.executed_file.name, 'executed_files/v1-%s-%s-test.pdf' % (self.item.pk, self.lawyer.username))
        self.assertEqual(revision.executed_file.url, 'https://dev-toolkit-lawpal-com.s3.amazonaws.com/executed_files/v1-%s-%s-test.pdf' % (self.item.pk, self.lawyer.username))


class InvalidFileTypeAsUrlOrMultipartDataTest(BaseEndpointTest, LiveServerTestCase):
    """
    Test invalid file uploads
    """
    FILE_TO_TEST_UPLOAD_WITH = TEST_INVALID_UPLOAD_IMAGE_PATH

    @property
    def endpoint(self):
        return reverse('matter_item_revision', kwargs={'matter_slug': self.matter.slug, 'item_slug': self.item.slug})

    def setUp(self):
        super(InvalidFileTypeAsUrlOrMultipartDataTest, self).setUp()
        # setup the items for testing
        self.item = mommy.make('item.Item', matter=self.matter, name='Test Item with Revision', category=None)

    def test_endpoint_name(self):
        self.assertEqual(self.endpoint, '/api/v1/matters/lawpal-test/items/%s/revision' % self.item.slug)

    def test_patch_with_URL_executed_file(self):
        # normally there is no logo-white.png from filepicker io it sends name seperately
        # but for our tests we need to fake this out
        expected_image_url = 'http://localhost:8081/static/images/logo-white.png'
        expected_file_name = 'logo-white.png'

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

        # self.lawyer.matter_permissions(matter=self.matter).permissions

        self.assertEqual(resp.status_code, 400)  # error
        self.assertEqual(resp_json.get('executed_file'), [u"Invalid filetype, is: .png should be in: ['.pdf', '.docx', '.doc', '.ppt', '.pptx', '.xls', '.xlsx']"])  # error

    def test_post_with_URL_executed_file(self):
        mommy.make('attachment.Revision', executed_file=None, slug=None, item=self.item, uploaded_by=self.lawyer)

        expected_image_url = 'http://localhost:8081/static/images/logo-white.png'

        self.client.login(username=self.lawyer.username, password=self.password)

        data = {
            'executed_file': expected_image_url,
        }
        resp = self.client.post(self.endpoint, json.dumps(data), content_type='application/json')
        resp_json = json.loads(resp.content)

        self.assertEqual(resp.status_code, 400)  # invalid

    def test_post_with_FILE_executed_file(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        with open(self.FILE_TO_TEST_UPLOAD_WITH) as file_being_posted:
            data = {
                'executed_file': file_being_posted,
            }
            self.assertEqual(self.item.revision_set.all().count(), 0)
            resp = self.client.post(self.endpoint, data, content_type=MULTIPART_CONTENT)

        resp_json = json.loads(resp.content)

        self.assertEqual(resp.status_code, 400)  # invalid


class RevisionDeleteWithReviewersTest(BaseEndpointTest):
    """
    Bug in production 2014-04-07
    """
    def setUp(self):
        super(RevisionDeleteWithReviewersTest, self).setUp()
        self.item = mommy.make('item.Item', matter=self.matter, name='Test Item with Revision', category=None)
        self.revision = mommy.make('attachment.Revision', executed_file=None, slug=None, item=self.item, uploaded_by=self.lawyer)

        self.reviewer = mommy.make('auth.User', username='New Person', email='username@example.com')
        self.revision.reviewers.add(self.reviewer)

        self.item = self.item.__class__.objects.get(pk=self.item.pk)  # reset
        self.assertEqual(self.item.review_percentage_complete, 0.0)  # test review_percentage_complete is reset

    def test_delete_of_revision_not_blocked_by_reviwers(self):
        self.assertEqual(self.item.latest_revision, self.revision)
        # print self.item.latest_revision.pk
        self.assertEqual(self.item.revision_set.all().count(), 1)
        self.revision.delete()
        self.assertEqual(self.item.revision_set.all().count(), 0)

        self.item = self.item.__class__.objects.get(pk=self.item.pk)  # refresh

        self.assertEqual(self.item.review_percentage_complete, None)  # test review_percentage_complete is reset
        # print self.item.latest_revision.pk
        self.assertEqual(self.item.latest_revision, None)

        #
        # If it throws an Item.DoesNotExist exception here
        # then we have a problem becuause the field Item.latest_revision.on_delete should be on_delete=models.SET_NULL
        #
        self.item.__class__.objects.get(pk=self.item.pk)
        # test that the field has on_delete set to models.SET_NULL
        on_delete = getattr(self.item.__class__._meta.get_field_by_name('latest_revision')[0].rel, 'on_delete', None)
        self.assertTrue(on_delete == SET_NULL)

