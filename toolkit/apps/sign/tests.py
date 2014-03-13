# -*- coding: utf-8 -*-
from django.core import mail
from django.conf import settings
from django.test import TestCase

from toolkit.casper.workflow_case import BaseScenarios

from .models import SignDocument

from uuidfield.fields import StringUUID
from model_mommy import mommy

import os
import urllib


class BaseDataProvider(BaseScenarios):
    def setUp(self):
        super(BaseDataProvider, self).setUp()
        self.basic_workspace()

        self.invalid_signer = mommy.make('auth.User', username='invalid_signer', email='invalid_signer@lawpal.com')
        self.signer = mommy.make('auth.User', username='invited_signer', email='invited_signer@lawpal.com')

        self.item = mommy.make('item.Item', matter=self.matter, name='Test Item No. 1', category="A")

        self.revision = mommy.make('attachment.Revision',
                                   item=self.item,
                                   executed_file=os.path.join(settings.SITE_ROOT, 'toolkit', 'casper', 'test.pdf'),
                                   uploaded_by=self.lawyer)

        self.revision.signers.add(self.signer)

        #
        # Matter.participants automatically get an auth so that they can individual view the object
        # the 2 below are based on the matter.participants that are included as part of BaseScenarios
        #
        self.base_sign_document = self.revision.signdocument_set.all().first()

        self.sign_document = self.revision.signdocument_set.all().last()

        self.BASE_EXPECTED_AUTH_USERS = self.sign_document.auth

        # this is the test subject
        self.exected_uuid = self.sign_document.slug
        self.expected_auth_key = self.sign_document.get_user_auth(user=self.signer)


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
        self.assertEqual(self.sign_document.get_auth(key=key), self.signer.pk)

    def test_get_auth_invalid(self):
        """
        test that the get_auth method returns None when the user is not a signer
        """
        non_authed_user = mommy.make('auth.User', username='Unauthorised Person', email='unauthorised@example.com')

        key = self.sign_document.make_user_auth_key(user=non_authed_user)
        self.assertEqual(self.sign_document.get_auth(key=key), None)

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
        EXPECTED_AUTH_USERS.update({self.expected_auth_key: self.signer.pk})
        self.assertEqual(self.sign_document.auth, EXPECTED_AUTH_USERS)  # has auth

    def test_deauthorise_user(self):
        # add the signer and we should then get an auth setup
        self.sign_document.signers.add(self.signer)

        EXPECTED_AUTH_USERS = self.BASE_EXPECTED_AUTH_USERS.copy()
        EXPECTED_AUTH_USERS.update({self.expected_auth_key: self.signer.pk})
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
1. logs current user out (if session is present)
2. logs user in based on url :auth_slug matching with a currently authorized signer
3. if the user is not lawyer or a participant then they can only see their own commments annotation etc
3a. this is done using the crocodoc_service.view_url(filter=id,id,id)
"""
