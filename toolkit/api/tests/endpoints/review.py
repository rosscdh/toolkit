# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.files import File
from django.test import LiveServerTestCase
from django.core.urlresolvers import reverse
from django.core.validators import URLValidator
from django.core.files.storage import FileSystemStorage

from toolkit.casper.prettify import mock_http_requests

from . import BaseEndpointTest


from model_mommy import mommy

import os
import mock
import json
import urllib

class RevisionReviewsTest(BaseEndpointTest):
    """
    /matters/:matter_slug/items/:item_slug/revision/reviewers/ (GET,POST)
        [lawyer,customer] to list, create reviewers
    """
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
        self.client.login(username=self.lawyer.username, password=self.password)

        resp = self.client.get(self.endpoint)
        self.assertEqual(resp.status_code, 200)

        json_data = json.loads(resp.content)
        self.assertEqual(json_data['count'], 0)

    def test_lawyer_post(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        participant = mommy.make('auth.User', first_name='Participant', last_name='Number 1', email='participant+1@lawpal.com')

        data = {
            "username": participant.username
        }
        resp = self.client.post(self.endpoint, json.dumps(data), content_type='application/json')

        self.assertEqual(resp.status_code, 201)  # created

        json_data = json.loads(resp.content)
        self.assertEqual(json_data['name'], participant.get_full_name())
        # test they are in the items reviewer set
        self.assertTrue(participant in self.item.latest_revision.reviewers.all())

        #
        # Test they show in the GET
        #
        resp = self.client.get(self.endpoint)

        self.assertEqual(resp.status_code, 200)

        json_data = json.loads(resp.content)
        self.assertEqual(json_data['count'], 1)
        self.assertEqual(json_data['results'][0]['name'], participant.get_full_name())


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
        self.assertEqual(resp.status_code, 401)  # unauthorized

    def test_anon_post(self):
        resp = self.client.post(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 401)  # unauthorized

    def test_anon_patch(self):
        resp = self.client.patch(self.endpoint, {})
        self.assertEqual(resp.status_code, 401)  # unauthorized

    def test_anon_delete(self):
        resp = self.client.delete(self.endpoint, {})
        self.assertEqual(resp.status_code, 401)  # unauthorized


class RevisionReviewerTest(BaseEndpointTest, LiveServerTestCase):
    """
    /matters/:matter_slug/items/:item_slug/revision/reviewer/:username (GET,DELETE)
        [lawyer,customer] to view, delete reviewers
    """
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

        self.assertEqual(json_data.keys(), [u'url', u'auth_url', u'name', u'user_class', u'initials'])

        self.assertEqual(len(self.revision.reviewers.all()), 1)
        self.assertEqual(len(self.revision.reviewdocument_set.all()), 2)

        reviewdocument = self.revision.reviewdocument_set.all().last()  # get the most recent
        #
        # People that are invited to review this document are in reviewers
        # only 1 per reviewdocument object
        #
        self.assertEqual(len(reviewdocument.reviewers.all()), 1)
        reviewer = reviewdocument.reviewers.all().first()
        self.assertEqual(reviewer, self.participant)

        #
        # Matter participants are always part of the participants set
        #
        participants = reviewdocument.participants.all()
        self.assertEqual(len(participants), 2)
        self.assertTrue(self.lawyer in participants)
        self.assertTrue(self.user in participants)
        # our new participant is not part of the participants on a review
        self.assertTrue(self.participant not in participants)
        #
        # Test the auth for the new reviewer
        #
        url = urllib.unquote_plus(reviewdocument.get_absolute_url(user=self.participant))
        self.assertEqual(url, '/review/%s/%s/' % (reviewdocument.slug, reviewdocument.make_user_auth_key(user=self.participant)))
        #
        # Test the auth urls for the matter.participants
        # test that they cant log in when logged in already (as the lawyer above)
        #
        for u in self.matter.participants.all():
            url = urllib.unquote_plus(reviewdocument.get_absolute_url(user=u))
            self.assertEqual(url, '/review/%s/%s/' % (reviewdocument.slug, reviewdocument.get_user_auth(user=u)))
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

        self.assertEqual(json_data.keys(), [u'url', u'name', u'user_class', u'initials'])

        self.assertEqual(len(self.revision.reviewers.all()), 0)
        self.assertEqual(len(self.revision.reviewdocument_set.all()), 1) # should be 1 because of the template one created for the participants
        self.assertEqual(len(self.revision.reviewdocument_set.all().first().participants.all()), 2)
        self.assertEqual(len(self.revision.reviewdocument_set.all().first().reviewers.all()), 0)

    def test_customer_get(self):
        self.client.login(username=self.user.username, password=self.password)
        resp = self.client.get(self.endpoint)
        self.assertEqual(resp.status_code, 200)  # ok

        json_data = json.loads(resp.content)

        self.assertEqual(json_data.keys(), [u'url', u'auth_url', u'name', u'user_class', u'initials'])

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
        self.assertEqual(resp.status_code, 401)  # unauthorized

    def test_anon_post(self):
        resp = self.client.post(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 401)  # unauthorized

    def test_anon_patch(self):
        resp = self.client.patch(self.endpoint, {})
        self.assertEqual(resp.status_code, 401)  # unauthorized

    def test_anon_delete(self):
        resp = self.client.delete(self.endpoint, {})
        self.assertEqual(resp.status_code, 401)  # unauthorized
