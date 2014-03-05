# -*- coding: utf-8 -*-
from django.core import mail
from django.conf import settings
from django.test import TestCase

from toolkit.casper.workflow_case import BaseScenarios

from .models import ReviewDocument

from uuidfield.fields import StringUUID
from model_mommy import mommy

import os


class BaseDataProvider(BaseScenarios):
    def setUp(self):
        super(BaseDataProvider, self).setUp()
        self.basic_workspace()

        self.reviewer = mommy.make('auth.User', username='invited_reviewer', email='invited_reviewer@lawpal.com')

        self.item = mommy.make('item.Item', matter=self.matter, name='Test Item No. 1', category="A")

        self.revision = mommy.make('attachment.Revision',
                                   item=self.item,
                                   executed_file=os.path.join(settings.SITE_ROOT, 'toolkit', 'casper', 'test.pdf'),
                                   uploaded_by=self.lawyer)

        # this is the test subject
        self.review_document = mommy.make('review.ReviewDocument', document=self.revision, slug=StringUUID('2c3981a04f2a46b7a18912b77c0abdd4'))
        self.expected_review_document_slug = '2RoAaR7gf9mh4Q=='


"""
Model Tests
1. get_absolute_url
2. send_invite_emails
3. auth add
4. auth get
"""
class ReviewDocumentModelTest(BaseDataProvider, TestCase):
    def test_get_absolute_url(self):
        self.assertEqual(self.review_document.get_absolute_url(user=self.reviewer), '/review/2c3981a04f2a46b7a18912b77c0abdd4/2RoAaR7gf9mh4Q%3D%3D/')

    def test_auth_get(self):
        self.assertEqual(self.review_document.auth, {})

    def test_auth_set(self):
        self.review_document.auth = {"monkey-key": 12345}
        self.assertEqual(self.review_document.auth, {"monkey-key": 12345})


class ReviewerAuthorisationTest(BaseDataProvider, TestCase):
    def test_authorise_user(self):
        self.assertEqual(self.review_document.reviewers.all().count(), 0)
        self.assertEqual(self.review_document.auth, {})  # no auths

        # add the reviewer and we should then get an auth setup
        self.review_document.reviewers.add(self.reviewer)
        self.assertEqual(self.review_document.auth, {self.expected_review_document_slug: self.reviewer.pk})  # has auth

    def test_deauthorise_user(self):
        # add the reviewer and we should then get an auth setup
        self.review_document.reviewers.add(self.reviewer)
        self.assertEqual(self.review_document.auth, {self.expected_review_document_slug: self.reviewer.pk})  # has auth

        # now we remove them
        self.review_document.reviewers.remove(self.reviewer)
        self.assertEqual(self.review_document.auth, {})  # no auths


class ReviewerSendEmailTest(BaseDataProvider, TestCase):
    def setUp(self):
        super(ReviewerSendEmailTest, self).setUp()
        # add the reviewer for this test
        self.review_document.reviewers.add(self.reviewer)

    def test_email_send_to_valid_reviewer(self):
        self.review_document.send_invite_email(users=[self.reviewer])
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]

    def test_email_send_to_invalid_reviewer(self): pass

"""
View tests

"""