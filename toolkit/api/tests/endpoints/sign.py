# -*- coding: utf-8 -*-
from actstream.models import target_stream
from django.core import mail
from django.conf import settings
from django.core.files import File
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test.client import RequestFactory
from django.core.validators import URLValidator
from django.core.files.storage import FileSystemStorage

from toolkit.apps.workspace.models import InviteKey
from toolkit.casper.workflow_case import PyQueryMixin
from toolkit.casper.prettify import mock_http_requests
from toolkit.apps.default.templatetags.toolkit_tags import ABSOLUTE_BASE_URL

from . import BaseEndpointTest
from ...serializers import LiteUserSerializer

from model_mommy import mommy

import os
import mock
import json
import random
import urllib


class RevisionSignaturesTest(PyQueryMixin, BaseEndpointTest):
    """
    /matters/:matter_slug/items/:item_slug/revision/signers/ (GET,POST)
        [lawyer,customer] to list, create signers
    """
    EXPECTED_USER_SERIALIZER_FIELD_KEYS = [u'username', u'user_review_url', u'url', u'initials', u'user_class', u'name',]

    @property
    def endpoint(self):
        return reverse('item_revision_signers', kwargs={'matter_slug': self.matter.slug, 'item_slug': self.item.slug})

    @mock.patch('storages.backends.s3boto.S3BotoStorage', FileSystemStorage)
    def setUp(self):
        super(RevisionSignaturesTest, self).setUp()

        # setup the items for testing
        self.item = mommy.make('item.Item', matter=self.matter, name='Test Item with Revision', category=None)
        self.revision = mommy.make('attachment.Revision', executed_file=None, slug=None, item=self.item, uploaded_by=self.lawyer)

    def test_endpoint_name(self):
        self.assertEqual(self.endpoint, '/api/v1/matters/%s/items/%s/revision/signers' % (self.matter.slug, self.item.slug))

    def test_lawyer_get_no_participants(self):
        """
        We should get a signdocument but with None signers (only the participants, can view this signdocument object)
        """
        self.client.login(username=self.lawyer.username, password=self.password)

        resp = self.client.get(self.endpoint)
        self.assertEqual(resp.status_code, 200)

        json_data = json.loads(resp.content)

        self.assertEqual(json_data['count'], 1)

        self.assertEqual(json_data['results'][0]['signer'], None)
        self.assertEqual(json_data['results'][0]['is_complete'], False)

    def test_lawyer_post(self):
        """
        This is a bit of an anti pattern
        we POST a username into the endpoint
        and the system will create an account as well as assign them as a signer
        to the item revision
        """
        self.client.login(username=self.lawyer.username, password=self.password)

        # expect 1 review document at this point
        self.assertEqual(self.revision.signdocument_set.all().count(), 1)

        participant = mommy.make('auth.User', first_name='Participant', last_name='Number 1', email='participant+1@lawpal.com')

        data = {
            "username": participant.username
        }
        resp = self.client.post(self.endpoint, json.dumps(data), content_type='application/json')

        self.assertEqual(resp.status_code, 201)  # created

        json_data = json.loads(resp.content)

        # expect 2 review documents at this point
        self.assertEqual(self.revision.signdocument_set.all().count(), 1)
        # expect the newly created review doc to be available to the signer
        self.assertEqual(participant.signdocument_set.all().count(), 1)
        ## test the order by is workng order by newest first
        self.assertEqual(participant.signdocument_set.first(), self.revision.signdocument_set.first())

        self.assertEqual(json_data['signer']['name'], participant.get_full_name())
        # test they are in the items signer set
        self.assertTrue(participant in self.item.latest_revision.signers.all())

        #
        # Test they show in the GET
        #
        resp = self.client.get(self.endpoint)

        self.assertEqual(resp.status_code, 200)

        json_data = json.loads(resp.content)
        self.assertEqual(json_data['count'], 1)

        self.assertEqual(json_data['results'][0]['signer']['name'], participant.get_full_name())

        # user review url must be in it
        self.assertTrue('user_review_url' in json_data['results'][0]['signer'].keys())

        #
        # we expect the currently logged in users url to be returned;
        # as the view is relative to the user
        #
        expected_url = self.item.latest_revision.signdocument_set.all().first().get_absolute_url(user=self.lawyer)

        self.assertEqual(json_data['results'][0]['signer']['user_review_url'], expected_url)

        outbox = mail.outbox
        self.assertEqual(len(outbox), 1)

        email = outbox[0]
        self.assertEqual(email.subject, '[ACTION REQUIRED] Invitation to sign a document')

        pq = self.pq(email.body)

        review_document = self.item.latest_revision.signdocument_set.filter(signers__in=[participant]).first()

        invite_key = InviteKey.objects.get(matter=self.matter, invited_user=participant)

        expected_action_url = ABSOLUTE_BASE_URL(invite_key.get_absolute_url())

        self.assertEqual(pq('a')[0].attrib.get('href'), expected_action_url)
        self.assertEqual(invite_key.next, reverse('request:list'))

        # test if activity shows in stream
        stream = target_stream(self.matter)
        self.assertEqual(stream[0].data['message'], u'Lawyer Test invited Participant Number 1 as signer for Test Item with Revision')

    def test_second_lawyer_post(self):
        """
        This is the second post call to create a request to the signer.
        The system will return the already existing signer and send a new mail.
        NB. The email sent is slightly different note: subject
        """
        self.client.login(username=self.lawyer.username, password=self.password)

        participant = mommy.make('auth.User', first_name='Participant', last_name='Number 1', email='participant+1@lawpal.com')

        data = {
            "username": participant.username
        }
        resp = self.client.post(self.endpoint, json.dumps(data), content_type='application/json')

        self.assertEqual(resp.status_code, 201)  # created

        json_data = json.loads(resp.content)

        self.assertEqual(json_data['signer']['name'], participant.get_full_name())
        # test they are in the items signer set
        self.assertTrue(participant in self.item.latest_revision.signers.all())

        #
        # Test they show in the GET
        #
        resp = self.client.get(self.endpoint)

        self.assertEqual(resp.status_code, 200)

        json_data = json.loads(resp.content)
        self.assertEqual(json_data['count'], 1)

        self.assertEqual(json_data['results'][0]['signer']['name'], participant.get_full_name())

        # user review url must be in it
        self.assertTrue('user_review_url' in json_data['results'][0]['signer'].keys())

        #
        # we expect the currently logged in users url to be returned;
        # as the view is relative to the user
        #
        expected_url = self.item.latest_revision.signdocument_set.all().first().get_absolute_url(user=self.lawyer)

        self.assertEqual(json_data['results'][0]['signer']['user_review_url'], expected_url)

        outbox = mail.outbox
        self.assertEqual(len(outbox), 1)

        email = outbox[0]
        self.assertEqual(email.subject, '[ACTION REQUIRED] Invitation to sign a document')

        pq = self.pq(email.body)

        review_document = self.item.latest_revision.signdocument_set.filter(signers__in=[participant]).first()

        invite_key = InviteKey.objects.get(matter=self.matter, invited_user=participant)

        expected_action_url = ABSOLUTE_BASE_URL(invite_key.get_absolute_url())

        self.assertEqual(pq('a')[0].attrib.get('href'), expected_action_url)
        self.assertEqual(invite_key.next, reverse('request:list'))

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
        self.assertEqual(resp.status_code, 200)  # customers can see

    def test_customer_post(self):
        self.client.login(username=self.user.username, password=self.password)
        resp = self.client.post(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_customer_patch(self):
        self.client.login(username=self.user.username, password=self.password)
        resp = self.client.patch(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_customer_delete(self):
        self.client.login(username=self.user.username, password=self.password)
        resp = self.client.delete(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_anon_get(self):
        resp = self.client.get(self.endpoint)
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_anon_post(self):
        resp = self.client.post(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_anon_patch(self):
        resp = self.client.patch(self.endpoint, {})
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_anon_delete(self):
        resp = self.client.delete(self.endpoint, {})
        self.assertEqual(resp.status_code, 403)  # forbidden


class ReviewObjectIncrementWithNewSignerTest(BaseEndpointTest):
    """
    When we add a signer to a document(revision) then they should each get
    their own signdocument object so that they are sandboxed (see review app tests)
    """
    @property
    def endpoint(self):
        return reverse('item_revision_signers', kwargs={'matter_slug': self.matter.slug, 'item_slug': self.item.slug})

    @mock.patch('storages.backends.s3boto.S3BotoStorage', FileSystemStorage)
    def setUp(self):
        super(ReviewObjectIncrementWithNewSignerTest, self).setUp()

        # setup the items for testing
        self.item = mommy.make('item.Item', matter=self.matter, name='Test Revision signer signobject_set count', category=None)
        self.revision = mommy.make('attachment.Revision', executed_file=None, slug=None, item=self.item, uploaded_by=self.lawyer)

    def test_endpoint_name(self):
        self.assertEqual(self.endpoint, '/api/v1/matters/%s/items/%s/revision/signers' % (self.matter.slug, self.item.slug))

    def add_signer(self, data=None):
        if data is None:
            rand_num = random.random()
            data = {
                'email': 'invited-signer-%s@lawpal.com' % rand_num,
                'first_name': '%s' % rand_num,
                'last_name': 'Invited Signer',
                'message': 'Please sign this documnet',
            }
        # msut be logged in in order for this to work
        return self.client.post(self.endpoint, json.dumps(data), content_type='application/json')

    def test_new_signer_add_count_increment(self):
        """
        there should be 1 signdocument per signer
        """
        exected_num_signatures = 1
        expected_number_of_signdocuments = 5
        self.client.login(username=self.lawyer.username, password=self.password)

        self.assertEqual(self.revision.signdocument_set.all().count(), exected_num_signatures) # we should only have 1 at this point for the participants

        for i in range(1, expected_number_of_signdocuments):
            resp = self.add_signer()
            self.assertEqual(resp.status_code, 201)

            json_resp = json.loads(resp.content)

            username = json_resp.get('signer').get('username')
            signer = User.objects.get(username=username)

            # the revision has 2 signers now
            self.assertEqual(self.revision.signdocument_set.all().count(), exected_num_signatures)
            # but the signer only has 1
            self.assertEqual(signer.signdocument_set.all().count(), 1) # has only 1

    def test_signer_already_a_signer_add_count_no_increment(self):
        """
        a signer can have only 1 signdocument per document(revision)
        """
        exected_num_signatures = 1
        exected_total_num_signatures = 1
        number_of_add_attempts = 5
        self.client.login(username=self.lawyer.username, password=self.password)

        self.assertEqual(self.revision.signdocument_set.all().count(), exected_num_signatures) # we should only have 1 at this point for the participants

        for i in range(1, number_of_add_attempts):
            resp = self.add_signer(data={
                'email': 'single-invited-signer@lawpal.com',
                'first_name': 'Single',
                'last_name': 'Invited Signer',
                'message': 'There should only be 1 created in total for this person',
            })
            self.assertEqual(resp.status_code, 201)

            json_resp = json.loads(resp.content)

            username = json_resp.get('signer').get('username')
            signer = User.objects.get(username=username)

            # the revision has 2 signers now
            self.assertEqual(self.revision.signdocument_set.all().count(), exected_total_num_signatures)
            # but the signer only has 1
            self.assertEqual(signer.signdocument_set.all().count(), 1) # has only 1


class RevisionSignerTest(BaseEndpointTest):
    """
    /matters/:matter_slug/items/:item_slug/revision/signer/:username (GET,DELETE)
        [lawyer,customer] to view, delete signers
    """
    EXPECTED_USER_SERIALIZER_FIELD_KEYS = [u'username', u'user_review_url', u'url', u'initials', u'user_class', u'name',]

    @property
    def endpoint(self):
        return reverse('item_revision_signer', kwargs={'matter_slug': self.matter.slug, 'item_slug': self.item.slug, 'username': self.participant.username})

    @mock.patch('storages.backends.s3boto.S3BotoStorage', FileSystemStorage)
    def setUp(self):


        #
        # @NOTICE take note ye heathens; when we go live with signing this
        # gets removed
        #
        self.skipTest('Skiping Sign Tests until its ready')
        #
        #
        #
        #

        super(RevisionSignerTest, self).setUp()

        # setup the items for testing
        self.item = mommy.make('item.Item', matter=self.matter, name='Test Item with Revision', category=None)
        self.revision = mommy.make('attachment.Revision',
                                   executed_file=None,
                                   slug=None,
                                   item=self.item,
                                   uploaded_by=self.lawyer)

        with open(os.path.join(settings.SITE_ROOT, 'toolkit', 'casper', 'test.pdf'), 'r') as filename:
            self.revision.executed_file.save('test.pdf', File(filename))
            self.revision.save(update_fields=['executed_file'])

        self.participant = mommy.make('auth.User', username='authorised-signer', first_name='Participant', last_name='Number 1', email='participant+1@lawpal.com')
        self.participant.set_password(self.password)
        #
        # NB! by using the signdocument.signals and attachment.signals we are able to ensure that
        # all revision.signers are added to the appropriate signdocument objects
        # which means they can get an auth url to review the document
        #
        self.revision.signers.add(self.participant)

    def test_endpoint_name(self):
        self.assertEqual(self.endpoint, '/api/v1/matters/%s/items/%s/revision/signer/%s' % (self.matter.slug, self.item.slug, self.participant.username))

    @mock_http_requests
    def test_lawyer_get(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        resp = self.client.get(self.endpoint)

        self.assertEqual(resp.status_code, 200)
        json_data = json.loads(resp.content)

        self.assertItemsEqual(self.EXPECTED_USER_SERIALIZER_FIELD_KEYS, json_data.keys())

        self.assertEqual(len(self.revision.signers.all()), 1)
        self.assertEqual(len(self.revision.signdocument_set.all()), 1)

        signdocument = self.revision.signdocument_set.all().first()  # get the most recent
        #
        # People that are invited to review this document are in signers
        # only 1 per signdocument object
        #
        self.assertEqual(len(signdocument.signers.all()), 1)
        signer = signdocument.signers.all().first()
        self.assertEqual(signer, self.participant)

        #
        # Matter participants are always part of the signdocument auth users set
        #
        lawyer_auth = signdocument.get_user_auth(user=self.lawyer)
        user_auth = signdocument.get_user_auth(user=self.user)
        # now test them
        self.assertTrue(lawyer_auth is not None)
        self.assertTrue(user_auth is not None)
        self.assertEqual(len(signdocument.auth), 3)
        #
        # Test the auth for the new signer
        #
        url = urllib.unquote_plus(signdocument.get_absolute_url(user=self.participant))
        self.assertEqual(url, '/sign/%s/%s/' % (signdocument.slug, signdocument.make_user_auth_key(user=self.participant)))
        #
        # Test the auth urls for the matter.participants
        # test that they cant log in when logged in already (as the lawyer above)
        #
        for u in self.matter.participants.all():
            url = urllib.unquote_plus(signdocument.get_absolute_url(user=u))
            self.assertEqual(url, '/sign/%s/%s/' % (signdocument.slug, signdocument.get_user_auth(user=u)))
            # Test that permission is denied when logged in as a user that is not the auth_token user
            resp = self.client.get(url)
            self.assertTrue(resp.status_code, 403) # denied
        #
        # Now test the views not logged in
        #
        validate_url = URLValidator()

        for u in self.matter.participants.all():
            self.client.login(username=u.username, password=self.password)
            url = signdocument.get_absolute_url(user=u)
            resp = self.client.get(url)
            self.assertTrue(resp.status_code, 200) # ok logged in

            context_data = resp.context_data
            self.assertEqual(context_data.keys(), [u'object', 'signdocument', 'hellosign_view_url', u'view'])
            # is a valid url for crocodoc
            self.assertTrue(validate_url(context_data.get('hellosign_view_url')) is None)
            self.assertTrue('https://crocodoc.com/view/' in context_data.get('hellosign_view_url'))
            # expected_crocodoc_params = {'admin': False,
            #                             'demo': False,
            #                             'editable': True,
            #                             'downloadable': True,
            #                             'user': {'name': u.get_full_name(), 'id': u.pk},
            #                             'copyprotected': False,
            #                             'sidebar': 'auto'}

            # self.assertEqual(context_data.get('CROCDOC_PARAMS'), expected_crocodoc_params)

    def test_lawyer_post(self):
        self.client.login(username=self.lawyer.username, password=self.password)
        resp = self.client.post(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 405)  # method not allowed

    def test_lawyer_patch(self):
        self.client.login(username=self.lawyer.username, password=self.password)
        resp = self.client.patch(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 405)  # method not allowed

    def test_lawyer_delete(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        resp = self.client.delete(self.endpoint)
        self.assertEqual(resp.status_code, 200)  # ok

        json_data = json.loads(resp.content)
        keys = json_data.keys()
        self.assertItemsEqual(self.EXPECTED_USER_SERIALIZER_FIELD_KEYS, json_data.keys())

        self.assertEqual(len(self.revision.signers.all()), 0)
        self.assertEqual(len(self.revision.signdocument_set.all()), 1) # should be 1 because of the template one created for the participants
        self.assertEqual(len(self.revision.signdocument_set.all().first().signers.all()), 1)

    def test_customer_get(self):
        self.client.login(username=self.user.username, password=self.password)
        resp = self.client.get(self.endpoint)
        self.assertEqual(resp.status_code, 200)  # ok

        json_data = json.loads(resp.content)

        self.assertItemsEqual(self.EXPECTED_USER_SERIALIZER_FIELD_KEYS, json_data.keys())

    def test_customer_post(self):
        self.client.login(username=self.user.username, password=self.password)
        resp = self.client.post(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_customer_patch(self):
        self.client.login(username=self.user.username, password=self.password)
        resp = self.client.patch(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_customer_delete(self):
        self.client.login(username=self.user.username, password=self.password)
        resp = self.client.patch(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_anon_get(self):
        resp = self.client.get(self.endpoint)
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_anon_post(self):
        resp = self.client.post(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_anon_patch(self):
        resp = self.client.patch(self.endpoint, {})
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_anon_delete(self):
        resp = self.client.delete(self.endpoint, {})
        self.assertEqual(resp.status_code, 403)  # forbidden


