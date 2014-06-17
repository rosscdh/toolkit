# -*- coding: utf-8 -*-
from rest_framework.reverse import reverse
from toolkit.apps.workspace.models import ROLES

from .. import BaseEndpointTest

from model_mommy import mommy


class ItemDetailTest(BaseEndpointTest):
    """
    /matters/:matter_slug/items/:item_slug/ (GET,PATCH,DELETE)
        Allow the [lawyer,customer] user to list, and update an existing item
        objects; that belong to them
    """
    def setUp(self):
        super(ItemDetailTest, self).setUp()
        self.item = mommy.make('item.Item', matter=self.workspace, name='Test Item No. 1')

        self.revision = mommy.make('attachment.Revision',
                                   executed_file=None,
                                   slug=None,
                                   name='filename.txt',
                                   description='A test file',
                                   item=self.item,
                                   uploaded_by=self.lawyer)

    @property
    def endpoint(self):
        return reverse('matter_item_revision', kwargs={'matter_slug': self.matter.slug, 'item_slug': self.item.slug})

    def test_endpoint_name(self):
        self.assertEqual(self.endpoint, '/api/v1/matters/lawpal-test/items/%s/revision' % self.item.slug)

    def test_client_get(self):
        self.client.login(username=self.user.username, password=self.password)

        # colleague should get item-list and revisions
        user = self.matter.participants.get(username='test-customer')
        user_perms = user.matter_permissions(matter=self.matter)
        user_perms.role = ROLES.colleague
        user_perms.save(update_fields=['role'])

        resp = self.client.get(self.endpoint)
        self.assertEqual(resp.status_code, 200)

        # client should just get item-list, no revisions
        user = self.matter.participants.get(username='test-customer')
        user_perms = user.matter_permissions(matter=self.matter)
        user_perms.role = ROLES.client
        user_perms.save(update_fields=['role'])

        resp = self.client.get(self.endpoint)
        self.assertEqual(resp.status_code, 403)

        # share revision. client should get this one revision
        service = user.share_revision_service(revision=self.revision)
        self.assertFalse(service.is_shared)
        service.process()
        self.assertTrue(service.is_shared)

        resp = self.client.get(self.endpoint)

        self.assertEqual(resp.status_code, 200)