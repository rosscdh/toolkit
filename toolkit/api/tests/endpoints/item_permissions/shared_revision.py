# -*- coding: utf-8 -*-
import json
from types import NoneType

from rest_framework.reverse import reverse
from toolkit.api.serializers import SimpleUserSerializer
from toolkit.apps.workspace.models import ROLES

from .. import BaseEndpointTest

from model_mommy import mommy


# class ItemDetailPermissionTest(BaseEndpointTest):
#     """
#     /matters/:matter_slug/items/:item_slug/ (GET,PATCH,DELETE)
#         Allow the [lawyer,customer] user to list, and update an existing item
#         objects; that belong to them
#     """
#     def setUp(self):
#         super(ItemDetailPermissionTest, self).setUp()
#         self.item = mommy.make('item.Item', matter=self.workspace, name='Test Item No. 1')
#
#         self.revision = mommy.make('attachment.Revision',
#                                    executed_file=None,
#                                    slug=None,
#                                    name='filename.txt',
#                                    description='A test file',
#                                    item=self.item,
#                                    uploaded_by=self.lawyer)
#
#     @property
#     def endpoint(self):
#         return reverse('matter_item_revision', kwargs={'matter_slug': self.matter.slug, 'item_slug': self.item.slug})
#
#     def test_endpoint_name(self):
#         self.assertEqual(self.endpoint, '/api/v1/matters/lawpal-test/items/%s/revision' % self.item.slug)
#
#     def test_client_get(self):
#         self.client.login(username=self.user.username, password=self.password)
#         user = self.matter.participants.get(username='test-customer')
#
#         # colleague should get item-list and revisions
#         self.set_user_matter_role(user, ROLES.colleague, self.matter)
#
#         resp = self.client.get(self.endpoint)
#         self.assertEqual(resp.status_code, 200)
#
#         # client should just get item-list, no revisions
#         self.set_user_matter_role(user, ROLES.client, self.matter)
#
#         resp = self.client.get(self.endpoint)
#         resp_cont = json.loads(resp.content)
#
#         self.assertEqual(resp.status_code, 200)
#         self.assertEqual(resp_cont['revisions'], [])
#
#         # share revision.
#         self.revision.shared_with.add(user)
#
#         # client should now get this one revision
#         resp = self.client.get(self.endpoint)
#         resp_cont = json.loads(resp.content)
#         self.assertEqual(resp.status_code, 200)
#         self.assertEqual(resp_cont['revisions'], [])


class ShareRevisionPermissionTest(BaseEndpointTest):
    """
    """
    version_no = 1
    expected_num = 1

    @property
    def endpoint(self):
        return reverse('matter_item_revision', kwargs={'matter_slug': self.matter.slug, 'item_slug': self.item.slug})

    @property
    def share_endpoint(self):
        return reverse('matter_share_revision', kwargs={'matter_slug': self.matter.slug, 'item_slug': self.item.slug})

    @property
    def delete_endpoint(self):
        return '%s/%s' % (self.share_endpoint, self.username_to_work_with)

    def setUp(self):
        super(ShareRevisionPermissionTest, self).setUp()

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
        self.assertEqual(self.share_endpoint, '/api/v1/matters/lawpal-test/items/%s/revision/share' % self.item.slug)
        self.assertEqual(self.delete_endpoint, '/api/v1/matters/lawpal-test/items/%s/revision/share/%s' %
                         (self.item.slug, self.username_to_work_with))

    #
    # RevisionEndpoint
    #
    # check if shared_with is correctly set on the revision-endpoint
    def test_revision_get(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        # check that shared_with is empty
        resp = self.client.get(self.endpoint)
        self.assertEqual(resp.status_code, 200)
        resp_content = json.loads(resp.content)
        self.assertEqual(resp_content.get('shared_with'), [])

        # add user to shared_with
        user = self.matter.participants.get(username='test-customer')
        self.revision.shared_with.add(user)

        # check user is in shared_with
        resp = self.client.get(self.endpoint)
        self.assertEqual(resp.status_code, 200)
        resp_content = json.loads(resp.content)
        self.assertEqual(resp_content.get('shared_with')[0]['username'], SimpleUserSerializer(user).data['username'])

    #
    # ShareCurrentRevisionView
    #
    # helper-function to share with user
    def _share_with_user(self):
        return self.client.post(self.share_endpoint, json.dumps({'username': self.username_to_work_with}),
                                content_type='application/json')

    # helper-function to unshare with user
    def _delete_user_from_shared(self):
        return self.client.delete(self.delete_endpoint)

    # test sharing with sharing endpoint to check manage_items-permissions
    def test_post_permissions(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        # test if lawyer needs permissions to add someone
        self.set_user_matter_perms(self.lawyer, manage_items=False)
        resp_post = self._share_with_user()
        self.assertEqual(resp_post.status_code, 403)

        # set required permissions to test the rest
        self.set_user_matter_perms(self.lawyer, manage_items=True)

        # POST again to see if new permissions work
        resp_post = self._share_with_user()
        self.assertEqual(resp_post.status_code, 200)

    # test unsharing with sharing endpoint to check manage_items-permissions
    def test_delete_permissions(self):
        self.client.login(username=self.lawyer.username, password=self.password)
        self._share_with_user()

        # test if lawyer needs permissions to delete someone
        self.set_user_matter_perms(self.lawyer, manage_items=False)
        resp_post = self._delete_user_from_shared()
        self.assertEqual(resp_post.status_code, 403)

        # set required permissions to test the rest
        self.set_user_matter_perms(self.lawyer, manage_items=True)

        # DELETE again to see if new permissions work
        resp_post = self._delete_user_from_shared()
        self.assertEqual(resp_post.status_code, 200)

    # test that you only can share with clients, not with colleagues which see the revision anyway
    def test_post_only_client(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        # check endpoint does NOT accept non-client-user
        self.set_user_matter_role(self.user, ROLES.colleague)
        resp_post = self._share_with_user()
        self.assertEqual(resp_post.status_code, 400)

        # check endpoint accepts new client
        self.set_user_matter_role(self.user, ROLES.client)
        resp_post = self._share_with_user()
        self.assertEqual(resp_post.status_code, 200)

        # check endpoint accepts new user - ONE TIME
        resp_post = self._share_with_user()
        self.assertEqual(resp_post.status_code, 304)

    # test not to share with user that does not exist
    def test_post_only_existing_user(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        # check endpoint does NOT accept non-existing client
        resp_post = self.client.post(self.share_endpoint, json.dumps({'username': 'fake_username'}),
                                     content_type='application/json')
        self.assertEqual(resp_post.status_code, 400)

    # test the get-endpoint for shared_with-users
    def test_shared_with_in_item(self):
        self.client.login(username=self.lawyer.username, password=self.password)
        self._share_with_user()

        # check user is in shared_with
        resp = self.client.get(self.endpoint)
        self.assertEqual(resp.status_code, 200)
        resp_content = json.loads(resp.content)
        self.assertEqual(resp_content.get('shared_with')[0]['username'], self.username_to_work_with)

    # test deleting via endpoint
    def test_delete_client(self):
        self.client.login(username=self.lawyer.username, password=self.password)
        self._share_with_user()

        # check endpoint accepts client to delete
        self.set_user_matter_role(self.user, ROLES.client)
        resp_post = self._delete_user_from_shared()
        self.assertEqual(resp_post.status_code, 200)

        # check endpoint accepts client to delete - ONE TIME
        resp_post = self._delete_user_from_shared()
        self.assertEqual(resp_post.status_code, 304)

    #
    # MatterEndpoint with ItemSerializer
    #
    # test the matter-endpoint
    def test_matter_endpoint(self):
        self.client.login(username=self.user.username, password=self.password)

        # if customer is CLIENT and the revision is not shared with him, its latest_revision must be empty
        resp = self.client.get('/api/v1/matters/lawpal-test')
        resp_data = json.loads(resp.content)
        items = resp_data.get('items')
        self.assertEqual(type(items), list)

        latest_revision = items[0].get('latest_revision')
        self.assertEqual(type(latest_revision), NoneType)

        # add user to shared_with and check again
        self.revision.shared_with.add(self.user)
        resp = self.client.get('/api/v1/matters/lawpal-test')
        resp_data = json.loads(resp.content)
        items = resp_data.get('items')
        self.assertEqual(type(items), list)

        latest_revision = items[0].get('latest_revision')
        self.assertEqual(type(latest_revision), dict)
