# -*- coding: utf-8 -*-
from django.conf import settings
from rest_framework.reverse import reverse

from .. import BaseEndpointTest

from model_mommy import mommy

import os
import json
import urllib

from toolkit.api.serializers import SimpleUserSerializer

TEST_INVALID_UPLOAD_IMAGE_PATH = os.path.join(os.path.dirname(__file__), 'data', 'test-image.png')
# Pdfs ARE valid filetypes
TEST_PDF_PATH = os.path.join(settings.SITE_ROOT, 'toolkit', 'casper', 'test.pdf')
TEST_LONG_FILENAME_PATH = os.path.join(settings.SITE_ROOT, 'toolkit', 'casper', 'test-long-filename-@-(LawPal)-#1236202-v1-test-long-filename-@-(LawPal)-#1236202-v1-test-long-filename-@-(LawPal)-#1236202-v1-test-long-filename-@-(LawPal)-#1236202-v1-test-long-filename-@-(LawPal)-#1236202-v1-.doc')


class ItemRevisionPermissionTest(BaseEndpointTest):
    """
    Looks like manage_items has influence on revision-get.

    This test is NOT to test any permission related to Revision since there is none.
    """
    version_no = 1
    expected_num = 1
    # fixtures = ['sites', 'tools', 'dev-fixtures']

    @property
    def endpoint(self):
        return reverse('matter_item_revision', kwargs={'matter_slug': self.matter.slug, 'item_slug': self.item.slug})

    def setUp(self):
        super(ItemRevisionPermissionTest, self).setUp()

        # setup the items for testing
        self.item = mommy.make('item.Item', matter=self.matter, name='Test Item with Revision', category=None)

    def test_endpoint_name(self):
        self.assertEqual(self.endpoint, '/api/v1/matters/lawpal-test/items/%s/revision' % self.item.slug)

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

        self.set_user_matter_perms(user=self.lawyer, manage_items=False)
        resp = self.client.get(self.endpoint)
        self.assertEqual(resp.status_code, 200)