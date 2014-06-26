# -*- coding: utf-8 -*-
from django.conf import settings
from rest_framework.reverse import reverse

from .. import BaseEndpointTest

from model_mommy import mommy

import os
import json

from toolkit.apps.workspace.models import ROLES

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


class LatestRevisionTest(BaseEndpointTest):
    version_no = 1
    expected_num = 1

    @property
    def endpoint(self):
        return reverse('matter_item_revision', kwargs={'matter_slug': self.matter.slug, 'item_slug': self.item.slug})

    def setUp(self):
        super(LatestRevisionTest, self).setUp()

        # setup the items for testing
        self.item = mommy.make('item.Item', matter=self.matter, name='Test Item with Revision', category=None)

        self.revision = mommy.make('attachment.Revision',
                                   executed_file=None,
                                   slug=None,
                                   name='filename.txt',
                                   description='A test file',
                                   item=self.item,
                                   uploaded_by=self.lawyer)

        self.username_to_work_with = 'test-customer'

    def test_endpoint_name(self):
        self.assertEqual(self.endpoint, '/api/v1/matters/lawpal-test/items/%s/revision' % self.item.slug)

    # check if lawyer gets correct revisions
    def test_revision_get_lawyer(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        resp = self.client.get(self.endpoint)
        self.assertEqual(resp.status_code, 200)
        resp_content = json.loads(resp.content)
        self.assertEqual(resp_content.get('description'), 'A test file')
        self.assertTrue(resp_content.get('is_current'))

    # check if client gets no revisions
    def test_revision_get_client(self):
        self.client.login(username=self.user.username, password=self.password)

        user_perms = self.user.matter_permissions(self.matter)
        user_perms.role = ROLES.client
        user_perms.save(update_fields=['data'])

        resp = self.client.get(self.endpoint)
        self.assertEqual(resp.status_code, 403)

    # check if client gets revision if he is reviewer
    def test_revision_get_client_reviewer(self):
        self.client.login(username=self.user.username, password=self.password)

        user_perms = self.user.matter_permissions(self.matter)
        user_perms.role = ROLES.client
        user_perms.save(update_fields=['data'])

        self.revision.reviewers.add(self.user)

        resp = self.client.get(self.endpoint)
        self.assertEqual(resp.status_code, 200)
        resp_content = json.loads(resp.content)
        self.assertEqual(resp_content.get('description'), 'A test file')
        self.assertTrue(resp_content.get('is_current'))

    # check if client gets revision if he is reviewer and a new revision has been uploaded
    def test_revision_get_client_reviewer(self):
        self.client.login(username=self.user.username, password=self.password)

        user_perms = self.user.matter_permissions(self.matter)
        user_perms.role = ROLES.client
        user_perms.save(update_fields=['data'])

        self.revision.reviewers.add(self.user)

        self.revision = mommy.make('attachment.Revision',
                                   executed_file=None,
                                   slug=None,
                                   name='filename.txt',
                                   description='A test file',
                                   item=self.item,
                                   uploaded_by=self.lawyer)

        # query endpoint for current revision should return 403 because I am reviewing v1
        resp = self.client.get(self.endpoint)
        self.assertEqual(resp.status_code, 403)

        # query endpoint for v1 should return the revision, which is NOT current any more
        resp = self.client.get(self.endpoint + "/v1/")
        self.assertEqual(resp.status_code, 200)
        resp_content = json.loads(resp.content)
        self.assertEqual(resp_content.get('description'), 'A test file')
        self.assertFalse(resp_content.get('is_current'))