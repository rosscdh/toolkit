# -*- coding: utf-8 -*-
from django.core import mail
from django.core import signing
from django.conf import settings
from django.core.files import File
from django.core.urlresolvers import reverse
from django.contrib.auth.models import AnonymousUser
import mock

from toolkit.apps.matter.tasks import _export_matter

from toolkit.core.attachment.models import Revision
from toolkit.apps.workspace.models import Workspace
from toolkit.apps.default.templatetags.toolkit_tags import ABSOLUTE_BASE_URL

from . import BaseEndpointTest
from ...serializers import LiteClientSerializer

from model_mommy import mommy

import os
import json
import datetime


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
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_anon_post(self):
        resp = self.client.post(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_anon_patch(self):
        resp = self.client.patch(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_anon_delete(self):
        resp = self.client.delete(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden


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
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_anon_post(self):
        resp = self.client.post(self.endpoint, {})
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_anon_patch(self):
        resp = self.client.patch(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_anon_delete(self):
        resp = self.client.delete(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden


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

        self.assertEqual(_meta.keys(), ['templates', 'matter', 'item'])

        self.assertTrue('status' in _meta['matter'])
        self.assertTrue('custom_status' in _meta['item'])
        self.assertTrue('default_status' in _meta['item'])

        self.assertEqual(_meta['matter']['status'], None) # for the moment
        self.assertEqual(type(_meta['item']['custom_status']), dict)
        self.assertEqual(type(_meta['item']['default_status']), dict)

        # json changes int to string so we need to transform the result back:
        result = _meta['item'].get('default_status', {})
        result_int = {}
        for k in result.iterkeys():
            result_int[int(k)] = result[k]
        self.assertDictEqual(result_int, Revision.REVISION_STATUS.get_choices_dict())

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
        Test that the latest_revision is as it should be
        """
        self.assertEqual(type(items), list)

        latest_revision = items[0].get('latest_revision')
        self.assertEqual(type(latest_revision), dict)

        expected_url = ABSOLUTE_BASE_URL(reverse('matter_item_revision', kwargs={'matter_slug': self.revision.item.matter.slug, 'item_slug': self.revision.item.slug }))
        #self.assertEqual(latest_revision, expected_url)
        self.assertItemsEqual(latest_revision.keys(), ['url', 'regular_url', 'status', 'date_created', 'slug', 'name'])

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


class MatterRevisionLabelTest(BaseEndpointTest):
    default_status_dictionary = {'0': u'Draft',
                                 '1': u'For Discussion',
                                 '2': u'Final',
                                 '3': u'Executed',
                                 '4': u'Filed'}
    @property
    def endpoint(self):
        return reverse('matter_revision_label', kwargs={'matter_slug': self.matter.slug})

    @property
    def endpoint_for_get(self):
        return reverse('workspace-detail', kwargs={'slug': self.matter.slug})

    def test_endpoint_name(self):
        self.assertEqual(self.endpoint, '/api/v1/matters/lawpal-test/revision_label')

    def test_labels_get(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        resp = self.client.get(self.endpoint_for_get)
        resp_data = json.loads(resp.content)

        status_labels = resp_data['_meta']['item']['default_status']
        self.assertDictEqual(status_labels, self.default_status_dictionary)
        custom_labels = resp_data['_meta']['item']['custom_status']
        self.assertDictEqual(custom_labels, self.default_status_dictionary)

    def test_labels_post(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        data = {'status_labels': {'0': u'',
                                  '1': u'custom For Discussion',
                                  '2': u'custom Final',
                                  '3': u'custom Executed',
                                  '4': u'custom Filed',
                                  '5': u'custom New Name'}}

        resp = self.client.post(self.endpoint, data=json.dumps(data), content_type='application/json')
        self.assertEqual(201, resp.status_code)

        resp = self.client.get(self.endpoint_for_get)
        resp_data = json.loads(resp.content)

        status_labels = resp_data['_meta']['item']['custom_status']
        self.assertDictEqual(status_labels, {'0': u'',
                                             '1': u'custom For Discussion',
                                             '2': u'custom Final',
                                             '3': u'custom Executed',
                                             '4': u'custom Filed',
                                             '5': u'custom New Name'})

        # test patching a revision to the new label:
        item = mommy.make('item.Item', matter=self.matter, name='Test Item with Revision', category=None)
        data = {'status': '5'}
        resp = self.client.patch(reverse('matter_item_revision',
                                         kwargs={'matter_slug': self.matter.slug, 'item_slug': item.slug}),
                                 data=json.dumps(data), content_type='application/json')
        self.assertEqual(201, resp.status_code)
        resp_data = json.loads(resp.content)
        self.assertEqual(resp_data['status'], 5)


"""
Patched class for testing datetime
"""
class PatchedDateTime(datetime.datetime):
    @staticmethod
    def now():
        today = datetime.date.today()  # return today with the same time so the tests work even if other files are used which are NOT moke.
        return datetime.datetime(today.year, today.month, today.day, 0, 0, 0, 113903)


class MatterExportTest(BaseEndpointTest):
    """
    /matters/ (POST)
        Allow the [lawyer] user to start exporting a matter
    """
    @property
    def endpoint(self):
        return reverse('matter_export', kwargs={'matter_slug': self.matter.slug})

    def test_endpoint_name(self):
        self.assertEqual(self.endpoint, '/api/v1/matters/lawpal-test/export')

    def test_export_matter_post_not_allowed(self):
        self.client.login(username=self.user.username, password=self.password)

        # start the export
        resp = self.client.post(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def add_item_with_revision(self):
        # prepare item with revision and file
        self.item = mommy.make('item.Item', matter=self.matter, name='Test Item with Revision', category=None)
        self.revision = mommy.make('attachment.Revision', executed_file=None, slug=None, item=self.item,
                                  uploaded_by=self.lawyer, name='test file')
        with open(os.path.join(settings.SITE_ROOT, 'toolkit', 'casper', 'test.pdf'), 'r') as filename:
           self.revision.executed_file.save('test.pdf', File(filename))
           self.revision.save(update_fields=['executed_file'])

    def test_export_matter_post(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        self.add_item_with_revision()

        # start the export via post
        resp = self.client.post(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 200)  # ok
        # json_data = json.loads(resp.content)

        # check if mail is present
        outbox = mail.outbox
        self.assertEqual(len(outbox), 1)
        email = outbox[0]
        self.assertEqual(email.subject, u'Export has finished')
        self.assertEqual(email.recipients(), [u'test+lawyer@lawpal.com'])

    def test_exported_matter_download(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        self.add_item_with_revision()

        with mock.patch('datetime.datetime', PatchedDateTime):
            # start the export directly
            _export_matter(self.matter)

            # calculate download-link (which could also be taken from the email)
            created_at = datetime.datetime.now().isoformat()
            token_data = {'matter_slug': self.matter.slug,
                          'user_pk': self.lawyer.pk,
                          'created_at': created_at}
            token = signing.dumps(token_data, salt=settings.SECRET_KEY)

        # download the file and check its content
        download_link = ABSOLUTE_BASE_URL(reverse('matter:download-exported', kwargs={'token': token}))
        resp = self.client.get(download_link)
        self.assertEqual(resp.status_code, 200)
        self.assertGreater(len(resp.content), 3000)
        self.assertEqual(resp.get('Content-Type'), 'application/zip')


    def test_export_matter_post_with_download_customer(self):
        self.client.login(username=self.user.username, password=self.password)

        # start the export directly
        _export_matter(self.matter)

        # calculate download-link (which could also be taken from the email)
        created_at = datetime.date.today().isoformat()
        token_data = {'matter_slug': self.matter.slug,
                      'user_pk': self.user.pk,
                      'created_at': created_at}
        token = signing.dumps(token_data, salt=settings.SECRET_KEY)

        # download the file and check its content
        download_link = ABSOLUTE_BASE_URL(reverse('matter:download-exported', kwargs={'token': token}))
        resp = self.client.get(download_link)
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_export_matter_post_with_download_anon(self):
        # start the export directly
        _export_matter(self.matter)

        # calculate download-link (which could also be taken from the email)
        created_at = (datetime.date.today()).isoformat()
        token_data = {'matter_slug': self.matter.slug,
                      'user_pk': AnonymousUser.pk,
                      'created_at': created_at}
        token = signing.dumps(token_data, salt=settings.SECRET_KEY)

        # download the file and check its content
        download_link = ABSOLUTE_BASE_URL(reverse('matter:download-exported', kwargs={'token': token}))
        resp = self.client.get(download_link)
        self.assertEqual(resp.status_code, 302)  # redirect to login-page
