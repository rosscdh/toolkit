# -*- coding: utf-8 -*-
from django.core import mail
from django.conf import settings
from django.test import TestCase
# from django.utils import timezone

from toolkit.casper.prettify import mock_http_requests
from toolkit.casper.workflow_case import BaseScenarios

from .models import ReviewDocument

from model_mommy import mommy

import os
import urllib
import datetime


class BaseDataProvider(BaseScenarios):
    def setUp(self):
        super(BaseDataProvider, self).setUp()
        self.basic_workspace()

        self.invalid_reviewer = mommy.make('auth.User', username='invalid_reviewer', email='invalid_reviewer@lawpal.com')
        self.reviewer = mommy.make('auth.User', username='invited_reviewer', email='invited_reviewer@lawpal.com')

        self.item = mommy.make('item.Item', matter=self.matter, name='Test Item No. 1', category="A")

        self.revision = mommy.make('attachment.Revision',
                                   item=self.item,
                                   executed_file=os.path.join(settings.SITE_ROOT, 'toolkit', 'casper', 'test.pdf'),
                                   uploaded_by=self.lawyer)

        self.revision.reviewers.add(self.reviewer)

        #
        # Matter.participants automatically get an auth so that they can individual view the object
        # the 2 below are based on the matter.participants that are included as part of BaseScenarios
        #
        self.base_review_document = self.revision.reviewdocument_set.all().first()

        self.review_document = self.revision.reviewdocument_set.all().first()

        self.BASE_EXPECTED_AUTH_USERS = self.review_document.auth

        # this is the test subject
        self.exected_uuid = self.review_document.slug
        self.expected_auth_key = self.review_document.get_user_auth(user=self.reviewer)


"""
Model Tests
1. get_absolute_url
2. send_invite_emails
3. auth add
4. auth get
"""
class ReviewDocumentModelTest(BaseDataProvider, TestCase):
    def test_get_absolute_url(self):
        self.assertEqual(self.review_document.get_absolute_url(user=self.reviewer), '/review/{uuid}/{auth_key}/'.format(uuid=self.exected_uuid,
                                                                                                                        auth_key=urllib.quote(self.expected_auth_key)))

    def test_auth_get(self):
        self.assertEqual(self.review_document.auth, self.BASE_EXPECTED_AUTH_USERS)

    def test_auth_set(self):
        self.review_document.auth = {"monkey-key": 12345}
        self.assertEqual(self.review_document.auth, {"monkey-key": 12345})

    def test_get_auth(self):
        """
        test that the get_auth method returns the User.pk for authentication backend
        """
        self.review_document.reviewers.add(self.reviewer)  # add the user
        key = self.review_document.make_user_auth_key(user=self.reviewer)
        self.assertEqual(self.review_document.get_auth(auth_key=key), self.reviewer.pk)

    def test_get_auth_invalid(self):
        """
        test that the get_auth method returns None when the user is not a reviewer
        """
        non_authed_user = mommy.make('auth.User', username='Unauthorised Person', email='unauthorised@example.com')

        key = self.review_document.make_user_auth_key(user=non_authed_user)
        self.assertEqual(self.review_document.get_auth(auth_key=key), None)

class ReviewerAuthorisationTest(BaseDataProvider, TestCase):
    def test_authorise_user(self):
        EXPECTED_AUTH_USERS = self.BASE_EXPECTED_AUTH_USERS.copy()
        #
        # remove the current guy jsut for this test
        #
        self.review_document.reviewers.remove(self.reviewer)

        self.assertEqual(self.review_document.reviewers.all().count(), 0)
        self.assertEqual(self.review_document.auth, self.BASE_EXPECTED_AUTH_USERS)  # no auths

        # add the reviewer and we should then get an auth setup
        self.review_document.reviewers.add(self.reviewer)
        EXPECTED_AUTH_USERS.update({str(self.reviewer.pk): self.expected_auth_key})
        self.assertEqual(self.review_document.auth, EXPECTED_AUTH_USERS)  # has auth

    def test_deauthorise_user(self):
        # add the reviewer and we should then get an auth setup
        self.review_document.reviewers.add(self.reviewer)

        EXPECTED_AUTH_USERS = self.BASE_EXPECTED_AUTH_USERS.copy()
        EXPECTED_AUTH_USERS.update({str(self.reviewer.pk): self.expected_auth_key})
        self.assertEqual(self.review_document.auth, EXPECTED_AUTH_USERS)  # has auth

        # now we remove them
        self.review_document.reviewers.remove(self.reviewer)
        self.assertEqual(self.review_document.auth, self.BASE_EXPECTED_AUTH_USERS)  # no auths


class ReviewerSendEmailTest(BaseDataProvider, TestCase):
    def setUp(self):
        super(ReviewerSendEmailTest, self).setUp()
        # add the reviewer for this test
        self.review_document.reviewers.add(self.reviewer)

    def test_email_send_to_all_reviewers(self):
        self.review_document.send_invite_email(from_user=self.lawyer)

        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.subject, u'[ACTION REQUIRED] Invitation to review a document')
        self.assertEqual(email.to, [self.reviewer.email])
        #
        # Contains the invite url
        #
        self.assertTrue(self.review_document.get_absolute_url(user=self.reviewer) in email.body)

    def test_email_send_to_valid_reviewer(self):
        self.review_document.send_invite_email(from_user=self.lawyer, users=[self.reviewer])

        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]

        self.assertEqual(email.subject, u'[ACTION REQUIRED] Invitation to review a document')
        self.assertEqual(email.to, [self.reviewer.email])
        #
        # Contains the invite url
        #
        self.assertTrue(self.review_document.get_absolute_url(user=self.reviewer) in email.body)

    def test_email_send_to_invalid_reviewer(self):
        """
        in order to send a reminder email to a user they MUST be an authorised
        reviewer and cant be some random user from anywhere
        """
        self.review_document.send_invite_email(from_user=self.lawyer, users=[self.invalid_reviewer])

        self.assertEqual(len(mail.outbox), 0)  # no email was sent


"""
View tests
1. logs current user out (if session is present)
2. logs user in based on url :auth_slug matching with a currently authorized reviewer
3. if the user is not lawyer or a participant then they can only see their own commments annotation etc
3a. this is done using the crocodoc_service.view_url(filter=id,id,id)
"""
class ReviewRevisionViewTest(BaseDataProvider, TestCase):
    def setUp(self):
        super(ReviewRevisionViewTest, self).setUp()
        # add the reviewer for this test
        self.review_document.reviewers.add(self.reviewer)

    @mock_http_requests
    def test_reviewer_viewing_revision_updates_last_viewed(self):
        """
        Patched class for testing datetime
        """
        class patched_datetime(datetime.datetime):
            @classmethod
            def utcnow(cls):
                return datetime.datetime(1970, 1, 1, 0, 0, 0, 113903)
        datetime.datetime = patched_datetime

        self.client.login(username=self.reviewer.username, password=self.password)

        self.assertEqual(ReviewDocument.objects.get(pk=self.review_document.pk).date_last_viewed, None)

        resp = self.client.get(self.review_document.get_absolute_url(self.reviewer), follow=True)

        self.assertEqual(resp.status_code, 200)

        self.assertEqual(ReviewDocument.objects.get(pk=self.review_document.pk).date_last_viewed.year, 1970)
        self.assertEqual(ReviewDocument.objects.get(pk=self.review_document.pk).date_last_viewed.month, 1)
        self.assertEqual(ReviewDocument.objects.get(pk=self.review_document.pk).date_last_viewed.day, 1)
        self.assertEqual(ReviewDocument.objects.get(pk=self.review_document.pk).date_last_viewed.hour, 0)
        self.assertEqual(ReviewDocument.objects.get(pk=self.review_document.pk).date_last_viewed.minute, 0)
        self.assertEqual(ReviewDocument.objects.get(pk=self.review_document.pk).date_last_viewed.second, 0)

    @mock_http_requests
    def test_lawyer_viewing_revision_updates_nothing(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        self.assertEqual(ReviewDocument.objects.get(pk=self.review_document.pk).date_last_viewed, None)

        resp = self.client.get(self.review_document.get_absolute_url(self.lawyer), follow=True)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(ReviewDocument.objects.get(pk=self.review_document.pk).date_last_viewed, None)
