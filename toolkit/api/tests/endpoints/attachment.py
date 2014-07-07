# -*- coding: utf-8 -*-
from django.conf import settings
from django.db.models import SET_NULL
from django.test import LiveServerTestCase
from rest_framework.reverse import reverse
from django.test.client import MULTIPART_CONTENT

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


class ItemAttachmentTest(BaseEndpointTest):
    """
    """
    # version_no = 1
    expected_num = 1

    @property
    def endpoint(self):
        return reverse('matter_item_attachment', kwargs={'matter_slug': self.matter.slug, 'item_slug': self.item.slug})

    def setUp(self):
        super(ItemAttachmentTest, self).setUp()

        # setup the items for testing
        self.item = mommy.make('item.Item', matter=self.matter, name='Test Item', category=None)

    def test_endpoint_name(self):
        self.assertEqual(self.endpoint, '/api/v1/matters/lawpal-test/items/%s/attachment' % self.item.slug)

    def test_no_attachment_get(self):
        """
        should return 404 if not present
        """
        self.item.attachments.all().delete()

        self.client.login(username=self.lawyer.username, password=self.password)
        resp = self.client.get(self.endpoint)

        self.assertEqual(resp.status_code, 404)  # not found

    def test_attachment_get(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        attachment = mommy.make('attachment.Attachment',
                                file=None,
                                name='filename.txt',
                                item=self.item,
                                uploaded_by=self.lawyer)

        resp = self.client.get(self.endpoint)
        resp_json = json.loads(resp.content)

        self.assertEqual(resp_json.get('name'), 'filename.txt')

        # test date is present
        self.assertTrue(resp_json.get('date_created') is not None)
        # test user is provided as a SimpleUserserializer
        # and has the correct keys
        provided_keys = resp_json.get('uploaded_by').keys()
        provided_keys.sort()
        expected_keys = SimpleUserSerializer(self.lawyer).data.keys()
        expected_keys.sort()
        self.assertEqual(provided_keys, expected_keys)

    def test_attachment_post_with_url(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        data = {
            'item': ItemSerializer(self.item).data.get('url'),
            'uploaded_by': UserSerializer(self.lawyer).data.get('url')
        }

        resp = self.client.post(self.endpoint, json.dumps(data), content_type='application/json')
        resp_json = json.loads(resp.content)
        self.assertEqual(resp_json.get('file'), None)

        self.assertEqual(resp.status_code, 201)  # created
        self.assertEqual(self.item.attachments.all().count(), self.expected_num)

    def test_attachment_delete(self):
        self.client.login(username=self.user.username, password=self.password)

        attachment = mommy.make('attachment.Attachment',
                                file=None,
                                name='filename.txt',
                                item=self.item,
                                uploaded_by=self.lawyer)

        self.assertEqual(self.item.attachments.count(), 1)

        user_perm = self.user.matter_permissions(self.matter)
        user_perm.update_permissions(manage_attachments=False)
        user_perm.save(update_fields=['data'])
        resp = self.client.delete(self.endpoint, {})
        self.assertEqual(resp.status_code, 403)  # forbidden if you do not own document or have required permission

        user_perm = self.user.matter_permissions(self.matter)
        user_perm.update_permissions(manage_attachments=True)
        user_perm.save(update_fields=['data'])
        resp = self.client.delete(self.endpoint, {})
        self.assertEqual(resp.status_code, 204)  # deleted

        self.assertEqual(self.item.attachments.count(), 0)

    def test_attachment_delete_own(self):
        self.client.login(username=self.user.username, password=self.password)

        attachment = mommy.make('attachment.Attachment',
                                file=None,
                                name='filename.txt',
                                item=self.item,
                                uploaded_by=self.user)

        self.assertEqual(self.item.attachments.count(), 1)

        user_perm = self.user.matter_permissions(self.matter)
        user_perm.update_permissions(manage_attachments=False)
        user_perm.save(update_fields=['data'])
        resp = self.client.delete(self.endpoint, {})
        self.assertEqual(resp.status_code, 204)  # deleted (because you own the document)

        self.assertEqual(self.item.attachments.count(), 0)


class AttachmentExecutedFileAsUrlOrMultipartDataTest(BaseEndpointTest,
                                                     LiveServerTestCase):
    FILE_TO_TEST_UPLOAD_WITH = TEST_PDF_PATH
    TEST_LONG_FILENAME_PATH = TEST_LONG_FILENAME_PATH

    @property
    def endpoint(self):
        return reverse('matter_item_attachment', kwargs={'matter_slug': self.matter.slug, 'item_slug': self.item.slug})

    def setUp(self):
        super(AttachmentExecutedFileAsUrlOrMultipartDataTest, self).setUp()

        # setup the items for testing
        self.item = mommy.make('item.Item', matter=self.matter, name='Test Item', category=None)

    def test_endpoint_name(self):
        self.assertEqual(self.endpoint, '/api/v1/matters/lawpal-test/items/%s/attachment' % self.item.slug)

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
            'file': expected_image_url,
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
        self.assertEqual(resp_json.get('file'),
                         u'/m/attachments/%s-%s-test-pirates-ahoy.pdf' % (self.item.pk, self.lawyer.username))
        self.assertEqual(self.item.attachments.count(), 1)

        # refresh
        self.item = self.item.__class__.objects.get(pk=self.item.pk)  # reset
        attachment = self.item.attachments.all().first()
        self.assertEqual(attachment.file.name,
                         u'attachments/%s-%s-test-pirates-ahoy.pdf' % (self.item.pk, self.lawyer.username))
        self.assertEqual(attachment.file.url,
                         u'/m/attachments/%s-%s-test-pirates-ahoy.pdf' % (self.item.pk, self.lawyer.username))

    def test_post_with_FILE_executed_file(self):
        """
        ensure we can upload an actual file to the endpoint
        """
        self.client.login(username=self.lawyer.username, password=self.password)

        with open(self.FILE_TO_TEST_UPLOAD_WITH) as file_being_posted:
            data = {
                'file': file_being_posted,
            }
            #
            # NB. uploading files must be a patch
            #
            self.assertEqual(self.item.attachments.all().count(), 0)
            #
            # @BUSINESSRULE if you are sending a binary file that needs to be download
            # ie. plain post then the CONTENT_TYPE must be MULTIPART_CONTENT and
            # the field "executed_file": a binary file object
            #
            resp = self.client.post(self.endpoint, data, content_type=MULTIPART_CONTENT)
        resp_json = json.loads(resp.content)

        self.assertEqual(resp.status_code, 201)  # created
        self.assertEqual(resp_json.get('name'), 'test.pdf')
        self.assertEqual(resp_json.get('file'), '/m/attachments/%s-%s-test.pdf' % (self.item.pk, self.lawyer.username))
        self.assertEqual(self.item.revision_set.all().count(), 1)

        revision = self.item.attachments.all().first()

        self.assertEqual(revision.file.name, 'attachments/%s-%s-test.pdf' % (self.item.pk, self.lawyer.username))
        self.assertEqual(revision.file.url, '/m/attachments/%s-%s-test.pdf' % (self.item.pk, self.lawyer.username))

#     def test_post_with_LONG_filename(self):
#         """
#         ensure we can upload an actual file to the endpoint
#         """
#         self.assertEqual(MAX_LENGTH_FILENAME, 50)  # should be as short as possible to allow for, upload_to path as well as extension and other attribs
#
#         self.client.login(username=self.lawyer.username, password=self.password)
#
#         with open(self.TEST_LONG_FILENAME_PATH) as file_being_posted:
#             data = {
#                 'executed_file': file_being_posted,
#             }
#             #
#             # NB. uploading files must be a patch
#             #
#             self.assertEqual(self.item.revision_set.all().count(), 0)
#             #
#             # @BUSINESSRULE if you are sending a binary file that needs to be download
#             # ie. plain post then the CONTENT_TYPE must be MULTIPART_CONTENT and
#             # the field "executed_file": a binary file object
#             #
#             resp = self.client.post(self.endpoint, data, content_type=MULTIPART_CONTENT)
#         resp_json = json.loads(resp.content)
#
#         self.assertEqual(resp.status_code, 201)  # created
#         self.assertEqual(resp_json.get('slug'), 'v1')
#         self.assertEqual(resp_json.get('name'), u'test-long-filename-@-(LawPal)-#1236202-v1-test-lon.doc')
#         # self.assertEqual(resp_json.get('executed_file'), u'https://dev-toolkit-lawpal-com.s3.amazonaws.com/executed_files/v1-%s-%s-test-long-filename-lawpal-1236202-v1-test-lon.doc' % (self.item.pk, self.lawyer.username))
#         self.assertEqual(resp_json.get('executed_file'), u'/m/executed_files/v1-%s-%s-test-long-filename-lawpal-1236202-v1-test-lon.doc' % (self.item.pk, self.lawyer.username))
#         self.assertEqual(self.item.revision_set.all().count(), 1)
#
#
# class InvalidFileTypeAsUrlOrMultipartDataTest(BaseEndpointTest, LiveServerTestCase):
#     """
#     Test invalid file uploads
#     """
#     FILE_TO_TEST_UPLOAD_WITH = TEST_INVALID_UPLOAD_IMAGE_PATH
#
#     @property
#     def endpoint(self):
#         return reverse('matter_item_revision', kwargs={'matter_slug': self.matter.slug, 'item_slug': self.item.slug})
#
#     def setUp(self):
#         super(InvalidFileTypeAsUrlOrMultipartDataTest, self).setUp()
#         # setup the items for testing
#         self.item = mommy.make('item.Item', matter=self.matter, name='Test Item with Revision', category=None)
#
#     def test_endpoint_name(self):
#         self.assertEqual(self.endpoint, '/api/v1/matters/lawpal-test/items/%s/revision' % self.item.slug)
#
#     def test_patch_with_URL_executed_file(self):
#         # normally there is no logo-white.png from filepicker io it sends name seperately
#         # but for our tests we need to fake this out
#         expected_image_url = 'http://localhost:8081/static/images/logo-white.png'
#         expected_file_name = 'logo-white.png'
#
#         self.client.login(username=self.lawyer.username, password=self.password)
#
#         #
#         # Filepicker IO sends us a url with no filename and or suffix that we use
#         # but they do send us the name of the file that was uploaded so lets use that
#         #
#         data = {
#             'executed_file': expected_image_url,
#             'name': expected_file_name
#         }
#         #
#         # @BUSINESSRULE if you are sending a url of a file that needs to be download
#         # ie. filepicker.io then the CONTENT_TYPE must be application/json and
#         # the field "executed_file": "http://example.com/myfile.pdf"
#         #
#         resp = self.client.patch(self.endpoint, json.dumps(data), content_type='application/json')
#         resp_json = json.loads(resp.content)
#
#         # self.lawyer.matter_permissions(matter=self.matter).permissions
#
#         self.assertEqual(resp.status_code, 400)  # error
#         self.assertEqual(resp_json.get('executed_file'), [u"Invalid filetype, is: .png should be in: ['.pdf', '.docx', '.doc', '.ppt', '.pptx', '.xls', '.xlsx']"])  # error
#
#     def test_post_with_URL_executed_file(self):
#         mommy.make('attachment.Revision', executed_file=None, slug=None, item=self.item, uploaded_by=self.lawyer)
#
#         expected_image_url = 'http://localhost:8081/static/images/logo-white.png'
#
#         self.client.login(username=self.lawyer.username, password=self.password)
#
#         data = {
#             'executed_file': expected_image_url,
#         }
#         resp = self.client.post(self.endpoint, json.dumps(data), content_type='application/json')
#         resp_json = json.loads(resp.content)
#
#         self.assertEqual(resp.status_code, 400)  # invalid
#
#     def test_post_with_FILE_executed_file(self):
#         self.client.login(username=self.lawyer.username, password=self.password)
#
#         with open(self.FILE_TO_TEST_UPLOAD_WITH) as file_being_posted:
#             data = {
#                 'executed_file': file_being_posted,
#             }
#             self.assertEqual(self.item.revision_set.all().count(), 0)
#             resp = self.client.post(self.endpoint, data, content_type=MULTIPART_CONTENT)
#
#         resp_json = json.loads(resp.content)
#
#         self.assertEqual(resp.status_code, 400)  # invalid