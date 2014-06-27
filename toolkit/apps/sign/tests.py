# -*- coding: utf-8 -*-
"""
Signers
Unlike reviewdocuments, signdocuments have only 1 object per set of signature invitees
this object is created in the signal above "ensure_revision_signdocument_object" and they are
authorized to view the object via the toolkit.apps.sign.signals
"""
from django.core import mail
from django.test import TestCase
from django.core.urlresolvers import reverse

from toolkit.test_runner import DEMO_DOC

from toolkit.casper.prettify import mock_http_requests
from toolkit.casper.workflow_case import BaseScenarios

from model_mommy import mommy

import mock
import json
import urllib
import datetime


"""
Patched class for testing datetime
"""


class PatchedDateTime(datetime.datetime):
    @staticmethod
    def utcnow():
        return datetime.datetime(1970, 1, 1, 0, 0, 0, 113903)


class BaseDataProvider(BaseScenarios):
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

        super(BaseDataProvider, self).setUp()
        self.basic_workspace()

        self.invalid_signer = mommy.make('auth.User', username='invalid_signer', email='invalid_signer@lawpal.com')
        self.invalid_signer.set_password(self.password)
        self.invalid_signer.save()

        self.signer = mommy.make('auth.User', username='invited_signer', email='invited_signer@lawpal.com')

        self.item = mommy.make('item.Item', matter=self.matter, name='Test Item No. 1', category="A")

        self.revision = mommy.make('attachment.Revision',
                                   item=self.item,
                                   executed_file=DEMO_DOC,
                                   uploaded_by=self.lawyer)

        self.revision.signers.add(self.signer)
        #
        # Matter.participants automatically get an auth so that they can individual view the object
        # the 2 below are based on the matter.participants that are included as part of BaseScenarios
        #
        self.sign_document = self.revision.signdocument_set.all().first()

        self.BASE_EXPECTED_AUTH_USERS = self.sign_document.auth

        # this is the test subject
        self.exected_uuid = self.sign_document.slug
        self.expected_auth_key = self.sign_document.get_user_auth(user=self.signer)

        self.assertTrue(self.sign_document.get_absolute_url(user=self.signer) is not None)


"""
Model Tests
1. get_absolute_url
2. send_invite_emails
3. auth add
4. auth get
"""


class SignDocumentModelTest(BaseDataProvider, TestCase):
    def test_get_absolute_url(self):
        self.assertEqual(self.sign_document.get_absolute_url(user=self.signer), '/sign/{uuid}/{auth_key}/'.format(uuid=self.exected_uuid,
                                                                                                                  auth_key=urllib.quote(self.expected_auth_key)))

    def test_auth_get(self):
        self.assertEqual(self.sign_document.auth, self.BASE_EXPECTED_AUTH_USERS)

    def test_auth_set(self):
        self.sign_document.auth = {"monkey-key": 12345}
        self.assertEqual(self.sign_document.auth, {"monkey-key": 12345})

    def test_get_auth(self):
        """
        test that the get_auth method returns the User.pk for authentication backend
        """
        self.sign_document.signers.add(self.signer)  # add the user
        key = self.sign_document.make_user_auth_key(user=self.signer)
        self.assertEqual(self.sign_document.get_auth(auth_key=key), self.signer.pk)

    def test_get_auth_invalid(self):
        """
        test that the get_auth method returns None when the user is not a signer
        """
        non_authed_user = mommy.make('auth.User', username='Unauthorised Person', email='unauthorised@example.com')

        key = self.sign_document.make_user_auth_key(user=non_authed_user)
        self.assertEqual(self.sign_document.get_auth(auth_key=key), None)

    def test_get_hs_service(self):
        """
        Test we are using the right hellosign endpoint
        """
        self.assertEqual(self.sign_document.get_hs_service().HelloSignSignatureClass.__class__.__name__, 'HelloSignUnclaimedDraftDocumentSignature')


class SignerAuthorisationTest(BaseDataProvider, TestCase):
    def test_authorise_user(self):
        EXPECTED_AUTH_USERS = self.BASE_EXPECTED_AUTH_USERS.copy()
        #
        # remove the current guy jsut for this test
        #
        self.sign_document.signers.remove(self.signer)

        self.assertEqual(self.sign_document.signers.all().count(), 0)
        self.assertEqual(self.sign_document.auth, self.BASE_EXPECTED_AUTH_USERS)  # no auths

        # add the signer and we should then get an auth setup
        self.sign_document.signers.add(self.signer)
        EXPECTED_AUTH_USERS.update({str(self.signer.pk): self.expected_auth_key})
        self.assertEqual(self.sign_document.auth, EXPECTED_AUTH_USERS)  # has auth

    def test_deauthorise_user(self):
        # add the signer and we should then get an auth setup
        self.sign_document.signers.add(self.signer)

        EXPECTED_AUTH_USERS = self.BASE_EXPECTED_AUTH_USERS.copy()
        EXPECTED_AUTH_USERS.update({str(self.signer.pk): self.expected_auth_key})
        self.assertEqual(self.sign_document.auth, EXPECTED_AUTH_USERS)  # has auth

        # now we remove them
        self.sign_document.signers.remove(self.signer)
        self.assertEqual(self.sign_document.auth, self.BASE_EXPECTED_AUTH_USERS)  # no auths


class SignerSendEmailTest(BaseDataProvider, TestCase):
    def setUp(self):
        super(SignerSendEmailTest, self).setUp()
        # add the signer for this test
        self.sign_document.signers.add(self.signer)

    def test_email_send_to_all_signers(self):
        self.sign_document.send_invite_email(from_user=self.lawyer)

        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.subject, u'[ACTION REQUIRED] Invitation to sign a document')
        self.assertEqual(email.to, [self.signer.email])
        #
        # Contains the invite url
        #
        self.assertTrue(self.sign_document.get_absolute_url(user=self.signer) in email.body)

    def test_email_send_to_valid_signer(self):
        self.sign_document.send_invite_email(from_user=self.lawyer, users=[self.signer])

        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]

        self.assertEqual(email.subject, u'[ACTION REQUIRED] Invitation to sign a document')
        self.assertEqual(email.to, [self.signer.email])
        #
        # Contains the invite url
        #
        self.assertTrue(self.sign_document.get_absolute_url(user=self.signer) in email.body)

    def test_email_send_to_invalid_signer(self):
        """
        in order to send a reminder email to a user they MUST be an authorised
        signer and cant be some random user from anywhere
        """
        self.sign_document.send_invite_email(from_user=self.lawyer, users=[self.invalid_signer])

        self.assertEqual(len(mail.outbox), 0)  # no email was sent


"""
View tests
1. if user is logged in, check they are a participant or the expected user according to the auth_key
2. logs user in based on url :auth_slug matching with a currently authorized signer
3. if the user is not lawyer or a participant then they can only see their own commments annotation etc
3a. this is done using the crocodoc_service.view_url(filter=id,id,id)
"""
class ReviewHellosignViewTest(BaseDataProvider, TestCase):
    def setUp(self):
        super(ReviewHellosignViewTest, self).setUp()
        # add the signer for this test
        self.sign_document.signers.add(self.signer)

    @mock_http_requests
    def test_anonymous_is_logged_in_as_expected_signer(self):
        self.assertEqual(self.sign_document.date_last_viewed, None)

        with mock.patch('datetime.datetime', PatchedDateTime):
            resp = self.client.get(self.sign_document.get_absolute_url(user=self.signer), follow=True)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['user'], self.signer)

        self.sign_document = self.sign_document.__class__.objects.get(pk=self.sign_document.pk) ## refresh
        #
        # And date updated
        #
        self.assertEqual(self.sign_document.date_last_viewed.year, 1970)
        self.assertEqual(self.sign_document.date_last_viewed.month, 1)
        self.assertEqual(self.sign_document.date_last_viewed.day, 1)
        self.assertEqual(self.sign_document.date_last_viewed.hour, 0)
        self.assertEqual(self.sign_document.date_last_viewed.minute, 0)
        self.assertEqual(self.sign_document.date_last_viewed.second, 0)

    @mock_http_requests
    def test_logged_in_invalid_user(self):
        """
        if we are logged in as someone with no connection to the sign or matter then it should
        throw a 403 foridden
        """
        self.client.login(username=self.invalid_signer.username, password=self.password)

        resp = self.client.get(self.sign_document.get_absolute_url(self.signer), follow=True)

        self.assertEqual(resp.status_code, 403)  # forbidden

    @mock_http_requests
    def test_signer_viewing_revision_updates_last_viewed(self):
        self.assertEqual(self.sign_document.date_last_viewed, None)

        with mock.patch('datetime.datetime', PatchedDateTime):
            resp = self.client.get(self.sign_document.get_absolute_url(self.signer), follow=True)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['user'], self.signer)

        self.sign_document = self.sign_document.__class__.objects.get(pk=self.sign_document.pk) ## refresh

        self.assertEqual(self.sign_document.date_last_viewed.year, 1970)
        self.assertEqual(self.sign_document.date_last_viewed.month, 1)
        self.assertEqual(self.sign_document.date_last_viewed.day, 1)
        self.assertEqual(self.sign_document.date_last_viewed.hour, 0)
        self.assertEqual(self.sign_document.date_last_viewed.minute, 0)
        self.assertEqual(self.sign_document.date_last_viewed.second, 0)

        #
        # Test the api endpoint returns the expected date_last_viewed
        #
        self.client.login(username=self.lawyer.username, password=self.password)
        resp = self.client.get(reverse('signdocument-detail', kwargs={'pk': self.sign_document.pk}))

        self.assertEqual(resp.status_code, 200)

        json_resp = json.loads(resp.content)
        self.assertEqual(json_resp.get('date_last_viewed'), u'1970-01-01T00:00:00.113Z')

    @mock_http_requests
    def test_lawyer_viewing_revision_updates_nothing(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        self.assertEqual(self.sign_document.date_last_viewed, None)

        resp = self.client.get(self.sign_document.get_absolute_url(self.lawyer), follow=True)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['user'], self.lawyer)

        self.sign_document = self.sign_document.__class__.objects.get(pk=self.sign_document.pk) ## refresh

        self.assertEqual(self.sign_document.date_last_viewed, None)
