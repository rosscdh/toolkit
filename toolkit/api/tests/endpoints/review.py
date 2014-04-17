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


class RevisionReviewsTest(PyQueryMixin, BaseEndpointTest):
    """
    /matters/:matter_slug/items/:item_slug/revision/reviewers/ (GET,POST)
        [lawyer,customer] to list, create reviewers
    """
    EXPECTED_USER_SERIALIZER_FIELD_KEYS = [u'username', u'user_review_url', u'url', u'initials', u'user_class', u'name',]

    @property
    def endpoint(self):
        return reverse('item_revision_reviewers', kwargs={'matter_slug': self.matter.slug, 'item_slug': self.item.slug})

    @mock.patch('storages.backends.s3boto.S3BotoStorage', FileSystemStorage)
    def setUp(self):
        super(RevisionReviewsTest, self).setUp()

        # setup the items for testing
        self.item = mommy.make('item.Item', matter=self.matter, name='Test Item with Revision', category=None)
        self.revision = mommy.make('attachment.Revision', executed_file=None, slug=None, item=self.item, uploaded_by=self.lawyer)

    def test_endpoint_name(self):
        self.assertEqual(self.endpoint, '/api/v1/matters/%s/items/%s/revision/reviewers' % (self.matter.slug, self.item.slug))

    def test_lawyer_get_no_participants(self):
        """
        We should get a reviewdocument but with None reviewers (only the participants, can view this reviewdocument object)
        """
        self.client.login(username=self.lawyer.username, password=self.password)

        resp = self.client.get(self.endpoint)
        self.assertEqual(resp.status_code, 200)

        json_data = json.loads(resp.content)

        self.assertEqual(json_data['count'], 1)

        self.assertEqual(json_data['results'][0]['reviewer'], None)
        self.assertEqual(json_data['results'][0]['is_complete'], False)

    def test_lawyer_post(self):
        """
        This is a bit of an anti pattern
        we POST a username into the endpoint
        and the system will create an account as well as assign them as a reviewer
        to the item revision
        """
        self.client.login(username=self.lawyer.username, password=self.password)

        # expect 1 review document at this point
        self.assertEqual(self.revision.reviewdocument_set.all().count(), 1)

        participant = mommy.make('auth.User', first_name='Participant', last_name='Number 1', email='participant+1@lawpal.com')

        data = {
            "username": participant.username
        }
        resp = self.client.post(self.endpoint, json.dumps(data), content_type='application/json')

        self.assertEqual(resp.status_code, 201)  # created

        json_data = json.loads(resp.content)

        # expect 2 review documents at this point
        self.assertEqual(self.revision.reviewdocument_set.all().count(), 2)
        # expect the newly created review doc to be available to the reviewer
        self.assertEqual(participant.reviewdocument_set.all().count(), 1)
        ## test the order by is workng order by newest first
        self.assertEqual(participant.reviewdocument_set.first(), self.revision.reviewdocument_set.first())

        self.assertEqual(json_data['reviewer']['name'], participant.get_full_name())
        # test they are in the items reviewer set
        self.assertTrue(participant in self.item.latest_revision.reviewers.all())

        #
        # Test they show in the GET
        #
        resp = self.client.get(self.endpoint)

        self.assertEqual(resp.status_code, 200)

        json_data = json.loads(resp.content)
        self.assertEqual(json_data['count'], 2)

        self.assertEqual(json_data['results'][0]['reviewer']['name'], participant.get_full_name())
        # we have no reviewers and the last object in the set should be the oldest
        self.assertEqual(json_data['results'][1]['reviewer'], None)

        # user review url must be in it
        self.assertTrue('user_review_url' in json_data['results'][0]['reviewer'].keys())

        #
        # we expect the currently logged in users url to be returned;
        # as the view is relative to the user
        #
        expected_url = self.item.latest_revision.reviewdocument_set.all().first().get_absolute_url(user=self.lawyer)

        self.assertEqual(json_data['results'][0]['reviewer']['user_review_url'], expected_url)

        outbox = mail.outbox
        self.assertEqual(len(outbox), 1)

        email = outbox[0]
        self.assertEqual(email.subject, '[ACTION REQUIRED] Invitation to review a document')

        pq = self.pq(email.body)

        review_document = self.item.latest_revision.reviewdocument_set.filter(reviewers__in=[participant]).first()

        invite_key = InviteKey.objects.get(matter=self.matter, invited_user=participant)

        expected_action_url = ABSOLUTE_BASE_URL(invite_key.get_absolute_url())

        self.assertEqual(pq('a')[0].attrib.get('href'), expected_action_url)
        self.assertEqual(invite_key.next, reverse('request:list'))

        # test if activity shows in stream
        stream = target_stream(self.matter)
        self.assertEqual(stream[0].data['override_message'],
                         u'Lawyer Test invited a reviewer to Test Item with Revision')

    def test_second_lawyer_post(self):
        """
        This is the second post call to create a request to the reviewer.
        The system will return the already existing reviewer and send a new mail.
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

        self.assertEqual(json_data['reviewer']['name'], participant.get_full_name())
        # test they are in the items reviewer set
        self.assertTrue(participant in self.item.latest_revision.reviewers.all())

        #
        # Test they show in the GET
        #
        resp = self.client.get(self.endpoint)

        self.assertEqual(resp.status_code, 200)

        json_data = json.loads(resp.content)
        self.assertEqual(json_data['count'], 2)

        self.assertEqual(json_data['results'][0]['reviewer']['name'], participant.get_full_name())
        # we have no reviewers and the last object in the set should be the oldest
        self.assertEqual(json_data['results'][1]['reviewer'], None)

        # user review url must be in it
        self.assertTrue('user_review_url' in json_data['results'][0]['reviewer'].keys())

        #
        # we expect the currently logged in users url to be returned;
        # as the view is relative to the user
        #
        expected_url = self.item.latest_revision.reviewdocument_set.all().first().get_absolute_url(user=self.lawyer)

        self.assertEqual(json_data['results'][0]['reviewer']['user_review_url'], expected_url)

        outbox = mail.outbox
        self.assertEqual(len(outbox), 1)

        email = outbox[0]
        self.assertEqual(email.subject, '[ACTION REQUIRED] Invitation to review a document')

        pq = self.pq(email.body)

        review_document = self.item.latest_revision.reviewdocument_set.filter(reviewers__in=[participant]).first()

        invite_key = InviteKey.objects.get(matter=self.matter, invited_user=participant)

        expected_action_url = ABSOLUTE_BASE_URL(invite_key.get_absolute_url())

        self.assertEqual(pq('a')[0].attrib.get('href'), expected_action_url)
        self.assertEqual(invite_key.next, reverse('request:list'))

        # user review url must be in it
        self.assertTrue('user_review_url' in json_data['results'][0]['reviewer'].keys())

        #
        # we expect the currently logged in users url to be returned;
        # as the view is relative to the user
        #
        expected_url = self.item.latest_revision.reviewdocument_set.all().first().get_absolute_url(user=self.lawyer)

        self.assertEqual(json_data['results'][0]['reviewer']['user_review_url'], expected_url)

        outbox = mail.outbox
        self.assertEqual(len(outbox), 1)

        email = outbox[0]
        self.assertEqual(email.subject, '[ACTION REQUIRED] Invitation to review a document')

        pq = self.pq(email.body)

        review_document = self.item.latest_revision.reviewdocument_set.filter(reviewers__in=[participant]).first()

        invite_key = InviteKey.objects.get(matter=self.matter, invited_user=participant)

        expected_action_url = ABSOLUTE_BASE_URL(invite_key.get_absolute_url())

        self.assertEqual(pq('a')[0].attrib.get('href'), expected_action_url)
        self.assertEqual(invite_key.next, reverse('request:list'))

        # test if activity shows in stream
        stream = target_stream(self.matter)
        self.assertEqual(stream[0].data['override_message'],
                         u'Lawyer Test invited a reviewer to Test Item with Revision')


class ReviewObjectIncrementWithNewReviewerTest(BaseEndpointTest):
    """
    When we add a reviewer to a document(revision) then they should each get
    their own reviewdocument object so that they are sandboxed (see review app tests)
    """
    @property
    def endpoint(self):
        return reverse('item_revision_reviewers', kwargs={'matter_slug': self.matter.slug, 'item_slug': self.item.slug})

    @mock.patch('storages.backends.s3boto.S3BotoStorage', FileSystemStorage)
    def setUp(self):
        super(ReviewObjectIncrementWithNewReviewerTest, self).setUp()

        # setup the items for testing
        self.item = mommy.make('item.Item', matter=self.matter, name='Test Revision reviewer reviewobject_set count', category=None)
        self.revision = mommy.make('attachment.Revision', executed_file=None, slug=None, item=self.item, uploaded_by=self.lawyer)

    def test_endpoint_name(self):
        self.assertEqual(self.endpoint, '/api/v1/matters/%s/items/%s/revision/reviewers' % (self.matter.slug, self.item.slug))

    def add_reviewer(self, data=None):
        if data is None:
            rand_num = random.random()
            data = {
                'email': 'invited-reviewer-%s@lawpal.com' % rand_num,
                'first_name': '%s' % rand_num,
                'last_name': 'Invited Reviewer',
                'message': 'Please provide me with a document monkeyboy!',
            }
        # msut be logged in in order for this to work
        return self.client.post(self.endpoint, json.dumps(data), content_type='application/json')

    def test_new_reviewer_add_count_increment(self):
        """
        there should be 1 reviewdocument per reviewer
        """
        initial_exected_num_reviews = 1
        expected_number_of_reviewdocuments = 5
        self.client.login(username=self.lawyer.username, password=self.password)

        self.assertEqual(self.revision.reviewdocument_set.all().count(), initial_exected_num_reviews) # we should only have 1 at this point for the participants

        for i in range(1, expected_number_of_reviewdocuments):
            resp = self.add_reviewer()
            self.assertEqual(resp.status_code, 201)

            json_resp = json.loads(resp.content)

            username = json_resp.get('reviewer').get('username')
            reviewer = User.objects.get(username=username)

            # the revision has 2 reviewers now
            self.assertEqual(self.revision.reviewdocument_set.all().count(), initial_exected_num_reviews + i)
            # but the reviewer only has 1
            self.assertEqual(reviewer.reviewdocument_set.all().count(), 1) # has only 1

    def test_reviewer_already_a_reviewer_add_count_no_increment(self):
        """
        a reviewer can have only 1 reviewdocument per document(revision)
        """
        initial_exected_num_reviews = 1
        exected_total_num_reviews = 2
        number_of_add_attempts = 5
        self.client.login(username=self.lawyer.username, password=self.password)

        self.assertEqual(self.revision.reviewdocument_set.all().count(), initial_exected_num_reviews) # we should only have 1 at this point for the participants

        for i in range(1, number_of_add_attempts):
            resp = self.add_reviewer(data={
                'email': 'single-invited-reviewer@lawpal.com',
                'first_name': 'Single',
                'last_name': 'Invited Reviewer',
                'message': 'There should only be 1 created in total for this person',
            })
            self.assertEqual(resp.status_code, 201)

            json_resp = json.loads(resp.content)

            username = json_resp.get('reviewer').get('username')
            reviewer = User.objects.get(username=username)

            # the revision has 2 reviewers now
            self.assertEqual(self.revision.reviewdocument_set.all().count(), exected_total_num_reviews)
            # but the reviewer only has 1
            self.assertEqual(reviewer.reviewdocument_set.all().count(), 1) # has only 1
            # make sure when we copy the reviewdocument for the new invitee that it does not inherit the
            # previous review_documents is_complete status
            self.assertEqual(reviewer.reviewdocument_set.all().first().is_complete, False)


class RevisionReviewerTest(BaseEndpointTest):
    """
    /matters/:matter_slug/items/:item_slug/revision/reviewer/:username (GET,DELETE)
        [lawyer,customer] to view, delete reviewers
    """
    EXPECTED_USER_SERIALIZER_FIELD_KEYS = [u'username', u'user_review_url', u'url', u'initials', u'user_class', u'name',]

    @property
    def endpoint(self):
        return reverse('item_revision_reviewer', kwargs={'matter_slug': self.matter.slug, 'item_slug': self.item.slug, 'username': self.participant.username})

    @mock.patch('storages.backends.s3boto.S3BotoStorage', FileSystemStorage)
    def setUp(self):
        super(RevisionReviewerTest, self).setUp()

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

        self.participant = mommy.make('auth.User', username='authorised-reviewer', first_name='Participant', last_name='Number 1', email='participant+1@lawpal.com')
        self.participant.set_password(self.password)
        #
        # NB! by using the reviewdocument.signals and attachment.signals we are able to ensure that
        # all revision.reviewers are added to the appropriate reviewdocument objects
        # which means they can get an auth url to review the document
        #
        self.revision.reviewers.add(self.participant)

    def test_endpoint_name(self):
        self.assertEqual(self.endpoint, '/api/v1/matters/%s/items/%s/revision/reviewer/%s' % (self.matter.slug, self.item.slug, self.participant.username))

    @mock_http_requests
    def test_lawyer_get(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        resp = self.client.get(self.endpoint)

        self.assertEqual(resp.status_code, 200)
        json_data = json.loads(resp.content)

        self.assertItemsEqual(self.EXPECTED_USER_SERIALIZER_FIELD_KEYS, json_data.keys())

        self.assertEqual(len(self.revision.reviewers.all()), 1)
        self.assertEqual(len(self.revision.reviewdocument_set.all()), 2)

        reviewdocument = self.revision.reviewdocument_set.all().first()  # get the most recent
        #
        # People that are invited to review this document are in reviewers
        # only 1 per reviewdocument object
        #
        self.assertEqual(len(reviewdocument.reviewers.all()), 1)
        reviewer = reviewdocument.reviewers.all().first()
        self.assertEqual(reviewer, self.participant)

        #
        # Matter participants are always part of the reviewdocument auth users set
        #
        lawyer_auth = reviewdocument.get_user_auth(user=self.lawyer)
        user_auth = reviewdocument.get_user_auth(user=self.user)
        # now test them
        self.assertTrue(lawyer_auth is not None)
        self.assertTrue(user_auth is not None)
        self.assertEqual(len(reviewdocument.auth), 3)
        #
        # Test the auth for the new reviewer
        #
        url = urllib.unquote_plus(reviewdocument.get_absolute_url(user=self.participant))
        self.assertEqual(url, ABSOLUTE_BASE_URL('/review/%s/%s/' % (reviewdocument.slug, reviewdocument.make_user_auth_key(user=self.participant))))
        #
        # Test the auth urls for the matter.participants
        # test that they cant log in when logged in already (as the lawyer above)
        #
        for u in self.matter.participants.all():
            url = urllib.unquote_plus(reviewdocument.get_absolute_url(user=u))
            self.assertEqual(url, ABSOLUTE_BASE_URL('/review/%s/%s/' % (reviewdocument.slug, reviewdocument.get_user_auth(user=u))))
            # Test that permission is denied when logged in as a user that is not the auth_token user
            resp = self.client.get(url)
            self.assertTrue(resp.status_code, 403) # denied
        #
        # Now test the views not logged in
        #
        validate_url = URLValidator()

        for u in self.matter.participants.all():
            self.client.login(username=u.username, password=self.password)
            url = reviewdocument.get_absolute_url(user=u)
            resp = self.client.get(url)
            self.assertTrue(resp.status_code, 200) # ok logged in

            context_data = resp.context_data
            self.assertEqual(context_data.keys(), ['crocodoc_view_url', 'reviewdocument', u'object', 'CROCDOC_PARAMS', 'crocodoc', u'view'])
            # is a valid url for crocodoc
            self.assertTrue(validate_url(context_data.get('crocodoc_view_url')) is None)
            self.assertTrue('https://crocodoc.com/view/' in context_data.get('crocodoc_view_url'))
            expected_crocodoc_params = {'admin': False,
                                        'demo': False,
                                        'editable': True,
                                        'downloadable': True,
                                        'user': {'name': u.get_full_name(), 'id': u.pk},
                                        'copyprotected': False,
                                        'sidebar': 'auto'}

            self.assertEqual(context_data.get('CROCDOC_PARAMS'), expected_crocodoc_params)

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

        self.assertEqual(len(self.revision.reviewers.all()), 0)
        self.assertEqual(len(self.revision.reviewdocument_set.all()), 1) # should be 1 because of the template one created for the participants
        #self.assertEqual(len(self.revision.reviewdocument_set.all().first().participants.all()), 2)
        self.assertEqual(len(self.revision.reviewdocument_set.all().first().reviewers.all()), 0)

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


class RevisionRequestedDocumentTest(BaseEndpointTest):
    """
    When you request a document from someone
    item.is_requested = True
    and
    item.responsible_party must be a User
    """
    EXPECTED_USER_SERIALIZER_FIELD_KEYS = [u'status', u'category', u'is_complete', u'closing_group', u'description', u'parent', u'date_modified', u'url', u'is_requested', u'children', u'matter', u'date_due', u'responsible_party', u'is_final', u'date_created', u'latest_revision', u'request_document_meta', u'slug', u'name', u'review_percentage_complete']

    @property
    def endpoint(self):
        return reverse('matter_item_request_doc', kwargs={'matter_slug': self.matter.slug, 'item_slug': self.item.slug})

    def setUp(self):
        super(RevisionRequestedDocumentTest, self).setUp()

        self.request_factory = RequestFactory()

        #self.invited_uploader = mommy.make('auth.User', username='Invited Uploader', first_name='Invited', last_name='Uploader', email='inviteduploader@lawpal.com')
        # setup the items for testing
        self.item = mommy.make('item.Item',
                               matter=self.matter,
                               name='Test Item with Revision',
                               category=None)

    def test_endpoint_name(self):
        self.assertEqual(self.endpoint, '/api/v1/matters/%s/items/%s/request_document' % (self.matter.slug, self.item.slug))

    def test_lawyer_get(self):
        self.client.login(username=self.lawyer.username, password=self.password)
        resp = self.client.get(self.endpoint)

        self.assertEqual(resp.status_code, 200)
        json_data = json.loads(resp.content)

        self.assertItemsEqual(self.EXPECTED_USER_SERIALIZER_FIELD_KEYS, json_data.keys())

    def test_lawyer_post(self):
        self.client.login(username=self.lawyer.username, password=self.password)
        resp = self.client.post(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 405)  # not allowed

    def test_lawyer_patch(self):
        self.client.login(username=self.lawyer.username, password=self.password)
        data = {
            'email': 'inviteduploader@lawpal.com',
            'first_name': 'Invited',
            'last_name': 'Uploader User',
            'note': 'Please provide me with a document monkeyboy!',
        }
        resp = self.client.patch(self.endpoint, json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 200)  # method not allowed

        json_data = json.loads(resp.content)

        inviteduploader_user = User.objects.get(username='inviteduploader')
        invited_uploader = LiteUserSerializer(inviteduploader_user,
                                              context={'request': self.request_factory.get(self.endpoint)}).data  ## should exist as we jsut created him in the patch

        self.assertTrue(json_data.get('is_requested') is True)
        self.assertItemsEqual(json_data.get('responsible_party').keys(), invited_uploader.keys())


        #
        # now upload a document and ensure
        # from the responsible_party above and ensure that is_requested is False
        #
        new_revision = mommy.make('attachment.Revision', executed_file=None, slug=None, item=self.item,
                                  uploaded_by=inviteduploader_user)

        # refresh
        self.item = self.item.__class__.objects.get(pk=self.item.pk)

        # now the item should be is_requested = False
        self.assertEqual(self.item.is_requested, False)

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
