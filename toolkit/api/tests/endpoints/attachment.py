# -*- coding: utf-8 -*-
from django.conf import settings
from django.test import LiveServerTestCase
from rest_framework.reverse import reverse
from django.test.client import MULTIPART_CONTENT

from . import BaseEndpointTest
from ...serializers import ItemSerializer, UserSerializer, SimpleUserSerializer

from model_mommy import mommy

import os
import json

# Images are NOT valid filetypes to upload
TEST_INVALID_UPLOAD_IMAGE_PATH = os.path.join(os.path.dirname(__file__), 'data', 'test-image.png')
# Pdfs ARE valid filetypes
TEST_PDF_PATH = os.path.join(settings.SITE_ROOT, 'toolkit', 'casper', 'test.pdf')
TEST_LONG_FILENAME_PATH = os.path.join(settings.SITE_ROOT, 'toolkit', 'casper',
                                       'test-long-filename-@-(LawPal)-#1236202-v1-test-long-filename-@-(LawPal)-#1236202-v1-test-long-filename-@-(LawPal)-#1236202-v1-test-long-filename-@-(LawPal)-#1236202-v1-test-long-filename-@-(LawPal)-#1236202-v1-.doc')


class ItemAttachmentTest(BaseEndpointTest,
                         LiveServerTestCase):
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
        resp_json = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)  # empty list
        self.assertEqual(resp_json['count'], 0)

    def test_attachment_get(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        attachment = mommy.make('attachment.Attachment',
                                attachment=None,
                                name='filename.txt',
                                item=self.item,
                                uploaded_by=self.lawyer)

        resp = self.client.get(self.endpoint)
        resp_json = json.loads(resp.content)

        self.assertItemsEqual(resp_json.keys(), [u'count', u'previous', u'results', u'next'])
        
        self.assertEqual(resp_json['count'], 1)

        found_attachment = resp_json['results'][0]

        self.assertEqual(found_attachment.get('name'), 'filename.txt')

        # test date is present
        self.assertTrue(found_attachment.get('date_created') is not None)
        # test user is provided as a SimpleUserserializer
        # and has the correct keys
        provided_keys = found_attachment.get('uploaded_by').keys()

        provided_keys.sort()
        expected_keys = SimpleUserSerializer(self.lawyer).data.keys()

        expected_keys.sort()
        self.assertEqual(provided_keys, expected_keys)

    def test_attachment_post_with_url(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        data = {
            'item': ItemSerializer(self.item).data.get('url'),
            'uploaded_by': UserSerializer(self.lawyer).data.get('url'),
            'attachment': 'http://localhost:8081/static/test.pdf'
        }

        resp = self.client.post(self.endpoint, json.dumps(data), content_type='application/json')
        resp_json = json.loads(resp.content)
        self.assertEqual(resp_json.get('attachment'), u'/m/attachments/%s-test-lawyer-test-pirates-ahoy.pdf' % resp_json.get())

        self.assertEqual(resp.status_code, 201)  # created
        self.assertEqual(self.item.attachments.all().count(), self.expected_num)


class ItemAttachmentcRUDTest(BaseEndpointTest,
                             LiveServerTestCase):
    """
    """
    @property
    def endpoint(self):
        return reverse('attachment-detail', kwargs={'slug': self.attachment.slug})

    def setUp(self):
        super(ItemAttachmentcRUDTest, self).setUp()

        user_perm = self.lawyer.matter_permissions(self.matter)
        user_perm.update_permissions(manage_attachments=True)
        user_perm.save(update_fields=['data'])

        # setup the items for testing
        self.item = mommy.make('item.Item', matter=self.matter, name='Test Item', category=None)
        self.attachment = mommy.make('attachment.Attachment', item=self.item, uploaded_by=self.user, name='Test Item Attachment')

    def test_endpoint_name(self):
        self.assertEqual(self.endpoint, '/api/v1/attachments/%s' % self.attachment.slug)

    def test_attachment_delete_own(self):
        self.client.login(username=self.user.username, password=self.password)

        self.assertEqual(self.item.attachments.count(), 1)

        user_perm = self.user.matter_permissions(self.matter)
        user_perm.update_permissions(manage_attachments=False)
        user_perm.save(update_fields=['data'])
        resp = self.client.delete(self.endpoint, {})
        self.assertEqual(resp.status_code, 204)  # deleted (because you own the document)

        self.assertEqual(self.item.attachments.count(), 0)

    def test_attachment_delete(self):
        self.client.login(username=self.user.username, password=self.password)

        attachment = mommy.make('attachment.Attachment',
                                attachment=None,
                                name='filename.txt',
                                item=self.item,
                                uploaded_by=self.lawyer)

        endpoint = reverse('attachment-detail', kwargs={'slug': attachment.slug})

        self.assertEqual(self.item.attachments.count(), 2)  # own and by lawyer

        user_perm = self.user.matter_permissions(self.matter)
        user_perm.update_permissions(manage_attachments=False)
        user_perm.save(update_fields=['data'])
        resp = self.client.delete(endpoint, {})
        self.assertEqual(resp.status_code, 403)  # forbidden if you do not own document or have required permission

        user_perm = self.user.matter_permissions(self.matter)
        user_perm.update_permissions(manage_attachments=True)
        user_perm.save(update_fields=['data'])
        resp = self.client.delete(endpoint, {})
        self.assertEqual(resp.status_code, 204)  # deleted

        self.assertEqual(self.item.attachments.count(), 1)  # was 2 is now 1


class AttachmentExecutedFileAsUrlOrMultipartDataTest(BaseEndpointTest,
                                                     LiveServerTestCase):
    FILE_TO_TEST_UPLOAD_WITH = TEST_PDF_PATH
    TEST_LONG_FILENAME_PATH = TEST_LONG_FILENAME_PATH

    @property
    def endpoint(self):
        return reverse('attachment-detail', kwargs={'slug': self.attachment.slug})

    def setUp(self):
        super(AttachmentExecutedFileAsUrlOrMultipartDataTest, self).setUp()

        user_perm = self.lawyer.matter_permissions(self.matter)
        user_perm.update_permissions(manage_attachments=True)
        user_perm.save(update_fields=['data'])

        # setup the items for testing
        self.item = mommy.make('item.Item', matter=self.matter, name='Test Item', category=None)
        self.attachment = mommy.make('attachment.Attachment', item=self.item, uploaded_by=self.user, name='Test Item Attachment')

    def test_endpoint_name(self):
        self.assertEqual(self.endpoint, '/api/v1/attachments/%s' % self.attachment.slug)

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
            'executed_file': expected_image_url,  # NB posted as executed_file as thats what FilePicker sends
            'name': expected_file_name
        }
        #
        # @BUSINESSRULE if you are sending a url of a file that needs to be download
        # ie. filepicker.io then the CONTENT_TYPE must be application/json and
        # the field "executed_file": "http://example.com/myfile.pdf"
        #
        endpoint = reverse('matter_item_attachment', kwargs={'matter_slug': self.matter.slug, 'item_slug': self.item.slug})
        resp = self.client.post(endpoint, json.dumps(data), content_type='application/json')

        self.assertEqual(resp.status_code, 201)  # ok created

        resp_json = json.loads(resp.content)

        self.assertEqual(resp_json.get('attachment'), '/m/attachments/%s-test-lawyer-test-pirates-ahoy.pdf' % self.item.pk)
        self.assertEqual(resp_json.get('user_download_url'), reverse('download_attachment', kwargs={'slug': resp_json.get('slug')}))
        
        self.assertEqual(self.item.attachments.count(), 2)

        # refresh
        self.item = self.item.__class__.objects.get(pk=self.item.pk)  # reset
        attachment = self.item.attachments.get(slug=resp_json.get('slug'))

        self.assertEqual(attachment.attachment.name,
                         u'attachments/4-test-lawyer-test-pirates-ahoy.pdf')

    def test_post_with_FILE_executed_file(self):
        """
        ensure we can upload an actual file to the endpoint
        """
        self.client.login(username=self.lawyer.username, password=self.password)

        with open(self.FILE_TO_TEST_UPLOAD_WITH) as file_being_posted:
            data = {
                'attachment': file_being_posted,
            }
            #
            # NB. uploading files must be a patch
            #
            self.assertEqual(self.item.attachments.all().count(), 1)  # already has an attachment
            #
            # @BUSINESSRULE if you are sending a binary file that needs to be download
            # ie. plain post then the CONTENT_TYPE must be MULTIPART_CONTENT and
            # the field "executed_file": a binary file object
            #
            endpoint = reverse('matter_item_attachment', kwargs={'matter_slug': self.matter.slug, 'item_slug': self.item.slug})
            resp = self.client.post(endpoint, data, content_type=MULTIPART_CONTENT)

        resp_json = json.loads(resp.content)

        self.assertEqual(resp.status_code, 201)  # created

        self.assertEqual(resp_json.get('name'), 'test.pdf')
        self.assertEqual(resp_json.get('attachment'), '/m/attachments/%s-%s-test.pdf' % (self.item.pk, self.lawyer.username))
        self.assertEqual(self.item.attachments.count(), 2)

        attachment = self.item.attachments.get(slug=resp_json.get('slug'))

        self.assertEqual(attachment.attachment.name, 'attachments/%s-%s-test.pdf' % (self.item.pk, self.lawyer.username))
        self.assertEqual(attachment.attachment.url, '/m/attachments/%s-%s-test.pdf' % (self.item.pk, self.lawyer.username))

    def test_patch_permissions(self):
        self.client.login(username=self.user.username, password=self.password)

        user_perm = self.user.matter_permissions(self.matter)
        user_perm.update_permissions(manage_attachments=False)
        user_perm.role = user_perm.ROLES.client
        user_perm.save(update_fields=['data', 'role'])

        attachment = mommy.make('attachment.Attachment',
                                attachment=None,
                                name='filename.txt',
                                item=self.item,
                                uploaded_by=self.lawyer)
        
        endpoint = reverse('attachment-detail', kwargs={'slug': attachment.slug})

        resp = self.client.patch(endpoint, data=json.dumps({'name': 'tralala'}), content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

        user_perm = self.user.matter_permissions(self.matter)
        user_perm.update_permissions(manage_attachments=True)
        user_perm.save(update_fields=['data'])

        resp = self.client.patch(endpoint, data=json.dumps({'name': 'tralala'}), content_type='application/json')

        self.assertEqual(resp.status_code, 200)  # ok
        resp_json = json.loads(resp.content)
        self.assertEqual(resp_json.get('name'), 'tralala')

    def test_patch_own(self):
        self.client.login(username=self.user.username, password=self.password)

        user_perm = self.user.matter_permissions(self.matter)
        user_perm.update_permissions(manage_attachments=False)
        user_perm.save(update_fields=['data'])

        attachment = mommy.make('attachment.Attachment',
                                attachment=None,
                                name='filename.txt',
                                item=self.item,
                                uploaded_by=self.user)

        resp = self.client.patch(self.endpoint, data=json.dumps({'name': 'tralala'}), content_type='application/json')
        self.assertEqual(resp.status_code, 200)  # ok
        resp_json = json.loads(resp.content)
        self.assertEqual(resp_json.get('name'), 'tralala')