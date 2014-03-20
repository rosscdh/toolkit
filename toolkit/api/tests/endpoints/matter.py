# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse

from toolkit.core.item.models import Item
from toolkit.core.attachment.models import Revision
from toolkit.apps.workspace.models import Workspace

from . import BaseEndpointTest
from ...serializers import LiteClientSerializer

from model_mommy import mommy

import json


class MattersTest(BaseEndpointTest):
    """
    /matters/ (GET,POST)
        Allow the [lawyer] user to list, and create new matter ("workspace") objects
    """
    endpoint = reverse('workspace-list')

    def test_endpoint_name(self):
        self.assertEqual(self.endpoint, '/api/v1/matters')

    def test_lawyer_get(self):
        self.client.login(username=self.lawyer.username, password=self.password)
        resp = self.client.get(self.endpoint)

        self.assertEqual(resp.status_code, 200)

        json_data = json.loads(resp.content)
        self.assertEqual(json_data['count'], 1)
        self.assertEqual(json_data['results'][0]['name'], self.workspace.name)

    def test_lawyer_post(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        new_client = mommy.prepare('client.Client', lawyer=self.lawyer, name='A new Client for Test Lawyer')

        resp = self.client.post(self.endpoint, json.dumps(LiteClientSerializer(new_client).data), content_type='application/json')

        self.assertEqual(resp.status_code, 201)  # created

        json_data = json.loads(resp.content)
        self.assertEqual(json_data['name'], new_client.name)

    def test_lawyer_patch(self):
        self.client.login(username=self.lawyer.username, password=self.password)
        resp = self.client.patch(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 405)  # not allowed

    def test_lawyer_delete(self):
        self.client.login(username=self.lawyer.username, password=self.password)
        resp = self.client.delete(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 405)  # not allowed

    def test_customer_get(self):
        self.client.login(username=self.user.username, password=self.password)
        resp = self.client.get(self.endpoint)

        self.assertEqual(resp.status_code, 200)

        json_data = json.loads(resp.content)
        self.assertEqual(json_data['count'], 1)
        self.assertEqual(json_data['results'][0]['name'], self.workspace.name)

    def test_customer_post(self):
        self.client.login(username=self.user.username, password=self.password)
        resp = self.client.post(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)

    def test_customer_patch(self):
        self.client.login(username=self.user.username, password=self.password)
        resp = self.client.patch(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # method forbidden

    def test_customer_delete(self):
        self.client.login(username=self.user.username, password=self.password)
        resp = self.client.delete(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # method forbidden

    def test_anon_get(self):
        resp = self.client.get(self.endpoint)
        self.assertEqual(resp.status_code, 401)  # denied

    def test_anon_post(self):
        resp = self.client.post(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 401)  # denied

    def test_anon_patch(self):
        resp = self.client.patch(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 401)  # denied

    def test_anon_delete(self):
        resp = self.client.delete(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 401)  # denied


class MatterPercentageTest(BaseEndpointTest):
    """
        belongs to MattersTest and just tests if progress is calculated correctly
    """
    endpoint = reverse('workspace-list')

    def test_endpoint_name(self):
        self.assertEqual(self.endpoint, '/api/v1/matters')

    def test_percent_complete_zero(self):
        # create unfinished item:
        mommy.make('item.Item', name='Test Item #1', matter=self.workspace)
        self.client.login(username=self.lawyer.username, password=self.password)
        resp = self.client.get(self.endpoint)

        self.assertEqual(resp.status_code, 200)
        json_data = json.loads(resp.content)
        self.assertEqual(json_data['results'][0]['percent_complete'], u'0%')

    def test_percent_complete_one(self):
        # build 100 % case
        mommy.make('item.Item', name='Test Item #1', matter=self.workspace, is_complete=True)
        mommy.make('item.Item', name='Test Item #2', matter=self.workspace, is_complete=True)
        self.client.login(username=self.lawyer.username, password=self.password)
        resp = self.client.get(self.endpoint)

        self.assertEqual(resp.status_code, 200)

        json_data = json.loads(resp.content)
        self.assertEqual(json_data['results'][0]['percent_complete'], u'100%')

    def test_percent_complete_two_thirds(self):
        # build a 2/3 setup with a deleted object
        mommy.make('item.Item', name='Test Item #1', matter=self.workspace, is_complete=True)
        mommy.make('item.Item', name='Test Item #2', matter=self.workspace, is_complete=True)
        mommy.make('item.Item', name='Test Item #3', matter=self.workspace)
        mommy.make('item.Item', name='Test Item #4', matter=self.workspace, is_deleted=True)
        self.client.login(username=self.lawyer.username, password=self.password)
        resp = self.client.get(self.endpoint)

        self.assertEqual(resp.status_code, 200)

        json_data = json.loads(resp.content)
        self.assertEqual(json_data['results'][0]['percent_complete'], u'67%')

    def test_percent_complete_deleted(self):
        # check if newly deleted item gets calculated correctly
        mommy.make('item.Item', name='Test Item #1', matter=self.workspace, is_complete=True)
        item = mommy.make('item.Item', name='Test Item #1', matter=self.workspace)
        self.client.login(username=self.lawyer.username, password=self.password)

        resp = self.client.get(self.endpoint)
        self.assertEqual(resp.status_code, 200)
        json_data = json.loads(resp.content)
        self.assertEqual(json_data['results'][0]['percent_complete'], u'50%')

        item.delete()

        resp = self.client.get(self.endpoint)
        self.assertEqual(resp.status_code, 200)
        json_data = json.loads(resp.content)
        self.assertEqual(json_data['results'][0]['percent_complete'], u'100%')

    def test_percent_complete_no_items(self):
        # test what happens when matter has no items
        self.client.login(username=self.lawyer.username, password=self.password)
        resp = self.client.get(self.endpoint)
        self.assertEqual(resp.status_code, 200)
        json_data = json.loads(resp.content)

        self.assertEqual(json_data['results'][0]['percent_complete'], u'0%')


class MatterDetailTest(BaseEndpointTest):
    """
    /matters/:matter_slug/ (GET,PATCH,DELETE)
        Allow the [lawyer] user to list, and update an existing matter ("workspace") object
    """
    @property
    def endpoint(self):
        return reverse('workspace-detail', kwargs={'slug': self.workspace.slug})

    def test_endpoint_name(self):
        self.assertEqual(self.endpoint, '/api/v1/matters/lawpal-test')

    def test_lawyer_get(self):
        self.client.login(username=self.lawyer.username, password=self.password)
        resp = self.client.get(self.endpoint)

        self.assertEqual(resp.status_code, 200)

        json_data = json.loads(resp.content)
        self.assertEqual(json_data['name'], self.workspace.name)

    def test_lawyer_post(self):
        self.client.login(username=self.lawyer.username, password=self.password)
        resp = self.client.post(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 405)  # not implemented

    def test_lawyer_patch(self):
        expected_name = 'Changed Name test'

        self.client.login(username=self.lawyer.username, password=self.password)

        resp = self.client.patch(self.endpoint, json.dumps({'name': expected_name}), content_type='application/json')
        self.assertEqual(resp.status_code, 200)  # patched

        json_data = json.loads(resp.content)
        self.assertEqual(json_data['name'], expected_name)

    def test_lawyer_delete(self):
        """
        Lawyer can Soft delete workspaces
        """
        self.client.login(username=self.lawyer.username, password=self.password)
        resp = self.client.delete(self.endpoint, {}, content_type='application/json')

        self.assertEqual(resp.status_code, 204)  # no content but 2** success

        deleted_workspaces = Workspace.objects.deleted()
        self.assertEqual(len(deleted_workspaces), 1)

        deleted_workspace = deleted_workspaces[0]
        self.assertEqual(deleted_workspace.name, self.workspace.name)

    def test_customer_get(self):
        self.client.login(username=self.user.username, password=self.password)
        resp = self.client.get(self.endpoint)

        self.assertEqual(resp.status_code, 200)

        json_data = json.loads(resp.content)
        self.assertEqual(json_data['name'], self.workspace.name)

    def test_customer_post(self):
        self.client.login(username=self.user.username, password=self.password)
        resp = self.client.post(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)

    def test_customer_patch(self):
        self.client.login(username=self.user.username, password=self.password)

        resp = self.client.patch(self.endpoint, json.dumps({}), content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_customer_delete(self):
        """
        customers may not delete
        """
        self.client.login(username=self.user.username, password=self.password)
        resp = self.client.delete(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # method forbidden

    def test_anon_get(self):
        resp = self.client.get(self.endpoint)
        self.assertEqual(resp.status_code, 401)  # denied

    def test_anon_post(self):
        resp = self.client.post(self.endpoint, {})
        self.assertEqual(resp.status_code, 401)  # denied

    def test_anon_patch(self):
        resp = self.client.patch(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 401)  # denied

    def test_anon_delete(self):
        resp = self.client.delete(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 401)  # denied


class MatterDetailProvidedDataTest(BaseEndpointTest):
    """
    Test the provided data as expected by the gui app
    """
    @property
    def endpoint(self):
        return reverse('workspace-detail', kwargs={'slug': self.matter.slug})

    def setUp(self):
        super(MatterDetailProvidedDataTest, self).setUp()
        self.item = mommy.make('item.Item', matter=self.matter, name='Test Item No. 1', category="A")
        self.revision = mommy.make('attachment.Revision', executed_file=None, slug=None, item=self.item, uploaded_by=self.lawyer)

    def test_endpoint_name(self):
        self.assertEqual(self.endpoint, '/api/v1/matters/%s' % self.matter.slug)

    def confirm_meta(self, data):
        self.assertTrue('_meta' in data)

        _meta = data['_meta']
        self.assertEqual(type(_meta), dict)

        self.assertEqual(_meta.keys(), ['matter', 'item', 'revision'])

        self.assertTrue('status' in _meta['matter'])
        self.assertTrue('status' in _meta['item'])
        self.assertTrue('status' in _meta['revision'])

        self.assertEqual(_meta['matter']['status'], None) # for the moment
        self.assertEqual(type(_meta['item']['status']), dict)
        self.assertEqual(type(_meta['revision']['status']), dict)

        self.assertEqual(_meta['item'].get('status'), Item.ITEM_STATUS.get_choices_dict())
        self.assertEqual(_meta['revision'].get('status'), Revision.REVISION_STATUS.get_choices_dict())

    def confirm_participants(self, participants):
        """
        Test the participants construct
        """
        self.assertEqual(type(participants), list)
        # must have full url
        self.assertTrue(all(u.get('url') == 'http://testserver/api/v1/users/%s' % u.get('username') for u in participants))

        participant_urls = [u.get('url') for u in participants]
        self.assertTrue('http://testserver/api/v1/users/%s' % self.user.username in participant_urls)
        self.assertTrue('http://testserver/api/v1/users/%s' % self.lawyer.username in participant_urls)


    def confirm_item_latest_revision(self, items):
        """
        Test that the latest_revision is as it shoudl be
        """
        self.assertEqual(type(items), list)

        latest_revision = items[0].get('latest_revision')
        self.assertEqual(type(latest_revision), dict)
        self.assertEqual(latest_revision.get('url'), 'http://testserver/api/v1/revisions/%d' % self.revision.pk)

    def test_endpoint_data_lawyer(self):
        self.client.login(username=self.lawyer.username, password=self.password)
        resp = self.client.get(self.endpoint)
        resp_data = json.loads(resp.content)
        self.assertTrue(resp_data.get('url') is not None)

        # _meta
        self.confirm_meta(data=resp_data)
        # participants
        self.confirm_participants(participants=resp_data.get('participants'))
        # revisions
        self.confirm_item_latest_revision(items=resp_data.get('items'))

    def test_endpoint_data_customer(self):
        self.client.login(username=self.user.username, password=self.password)
        resp = self.client.get(self.endpoint)
        resp_data = json.loads(resp.content)
        self.assertTrue(resp_data.get('url') is not None)

        # participants
        self.confirm_participants(participants=resp_data.get('participants'))
        # revisions
        self.confirm_item_latest_revision(items=resp_data.get('items'))
