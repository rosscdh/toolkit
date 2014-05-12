# -*- coding: utf-8 -*-
from django.core import mail
from django.core import signing
from django.conf import settings
from django.test import TestCase
from django.core.files.base import ContentFile

from django.core.files.storage import default_storage
from storages.backends.s3boto import S3BotoStorage

from toolkit.casper.workflow_case import BaseScenarios
from ..services import MatterExportService

from model_mommy import mommy

import shutil
import datetime
import urllib
import os


def _ensure_file_exists_on_s3_for_testing():
    """
    Ensure that our test file exists on s3, which it must in order for this export
    service to function
    """
    s3_storage = S3BotoStorage()
    if not s3_storage.exists('testing/casper/test.pdf'):
        with open(os.path.join(settings.SITE_ROOT, 'toolkit', 'casper', 'test.pdf'), 'r') as filename:
            s3_storage.save('testing/casper/test.pdf', filename)
    return s3_storage.exists('testing/casper/test.pdf')


class MatterExportTest(BaseScenarios, TestCase):
    subject = MatterExportService

    def setUp(self):
        self.basic_workspace()

        self.item = mommy.make('item.Item', matter=self.workspace, name='Test Item #1')

        default_storage.save('testing/casper/test.pdf', ContentFile(os.path.join(settings.SITE_ROOT, 'toolkit', 'casper', 'test.pdf')))

        self.revision = mommy.make('attachment.Revision',
                                   item=self.item,
                                   executed_file='testing/casper/test.pdf',
                                   uploaded_by=self.lawyer)
        self.service = self.subject(matter=self.matter)

    def test_needed_revisions(self):
        self.service.ensure_needed_files_list()
        self.assertItemsEqual(self.service.needed_revisions, [self.revision])

    def test_token_data(self):
        self.assertEqual(self.service.token_data, {'matter_slug': u'lawpal-test', 'user_pk': 2, 'created_at': self.service.created_at})

    def test_token(self):
        encrypted_token = signing.dumps(self.service.token_data, salt=settings.SECRET_KEY)
        self.assertEqual(self.service.token, encrypted_token)
        decrypted_token = signing.loads(self.service.token, salt=settings.SECRET_KEY)
        self.assertEqual(self.service.token_data, decrypted_token)

    def test_token_unique(self):
        # compare against a new token from a new matterexport service
        self.assertTrue(self.service.token != self.subject(matter=self.matter).token)

    def test_ensure_files_exist_locally(self):
        """
        as this service runs async the files may not exist locally and must then be downloaded from s3
        """
        expected_test_s3_bucket_name = 'dev-toolkit-lawpal-com'
        self.assertEqual(settings.AWS_STORAGE_BUCKET_NAME, expected_test_s3_bucket_name)
        self.assertEqual(settings.AWS_FILESTORE_BUCKET, expected_test_s3_bucket_name)

        # delete the test file if it exists locally, as we want to download it from
        # s3 for this test
        if os.path.exists(os.path.join(settings.MEDIA_ROOT, 'testing', 'casper', 'test.pdf')):
            os.remove(os.path.join(settings.MEDIA_ROOT, 'testing', 'casper', 'test.pdf'))
        self.assertTrue(os.path.exists(os.path.join(settings.MEDIA_ROOT, 'testing', 'casper', 'test.pdf')) is False)

        # ensure our test file exists on s3 and not locally
        self.assertTrue(_ensure_file_exists_on_s3_for_testing())

        self.service.ensure_files_exist_locally()  # call the service
        # test that the service downloaded the file locally
        self.assertTrue(os.path.exists(os.path.join(settings.MEDIA_ROOT, 'testing', 'casper', 'test.pdf')) is True)
        # remove the test file and dir
        shutil.rmtree(os.path.join(settings.MEDIA_ROOT, 'testing', 'casper'))

    def test_get_zip_filename(self):
        self.assertEqual(self.service.get_zip_filename(token_data=self.service.token_data), u'exported_documents/lawpal-test_2_%s.zip' % self.service.created_at)

    def test_create_zip(self):
        zip_result = self.service.create_zip(filename=self.service.get_zip_filename(token_data=self.service.token_data))
        self.assertEqual(zip_result, u'%s/exported_documents/lawpal-test_2_%s.zip' % (settings.MEDIA_ROOT, self.service.created_at,))
        self.assertTrue(os.path.isfile(zip_result), True)

    def test_send_email(self):
        self.assertEqual(len(mail.outbox), 0)
        self.service.send_email(token=self.service.token)
        self.assertTrue(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.subject, u'Your Matter export has completed')
        self.assertEqual(email.recipients(), ['test+lawyer@lawpal.com'])
        # must url encode
        self.assertEqual(self.service.download_link, u'http://localhost:8000/matters/download/%s/' % urllib.quote_plus(self.service.token))
        self.assertTrue(self.service.download_link in email.body)

