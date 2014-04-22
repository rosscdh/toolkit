# -*- coding: utf-8 -*-
from django.core import mail
from django.conf import settings
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from actstream.models import Action

from toolkit.casper.prettify import mock_http_requests
from toolkit.casper.workflow_case import BaseScenarios
from toolkit.apps.default.templatetags.toolkit_tags import ABSOLUTE_BASE_URL

from .models import ReviewDocument

from model_mommy import mommy

import os
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
        super(BaseDataProvider, self).setUp()
        self.basic_workspace()

        self.invalid_reviewer = mommy.make('auth.User', username='invalid_reviewer', email='invalid_reviewer@lawpal.com')
        self.invalid_reviewer.set_password(self.password)
        self.invalid_reviewer.save()

        self.reviewer = mommy.make('auth.User', username='invited_reviewer', email='invited_reviewer@lawpal.com')

        self.item = mommy.make('item.Item', matter=self.matter, name='Test Item No. 1', category="A")
        self.assertEqual(self.item.review_percentage_complete, None)  # ensure we have None when there are no review requests
        # this wil change to a percentage when the request goes in

        default_storage.save('executed_files/test.pdf', ContentFile(os.path.join(settings.SITE_ROOT, 'toolkit', 'casper', 'test.pdf')))

        self.revision = mommy.make('attachment.Revision',
                                   item=self.item,
                                   executed_file='executed_files/test.pdf',
                                   uploaded_by=self.lawyer)

        # there should always be 1 reviewdocument that the matter.participants can review together alone
        self.assertEqual(self.revision.reviewdocument_set.all().count(), 1)
        self.assertEqual(self.item.review_percentage_complete, None)

        # when I add another reviewer they should get their own reviewdocument to talk about with the matter.participants
        self.revision.reviewers.add(self.reviewer)
        self.assertEqual(self.revision.reviewdocument_set.all().count(), 2)
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
        self.assertEqual(self.review_document.get_absolute_url(user=self.reviewer), ABSOLUTE_BASE_URL('/review/{uuid}/{auth_key}/'.format(uuid=self.exected_uuid,
                                                                                                                        auth_key=urllib.quote(self.expected_auth_key))))

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


class ReviewerAddToMatterRevisionTest(BaseDataProvider, TestCase):
    """
    When adding a new reviewer to a matter.revision; there should be a ReviewDocument
    per reviewer; this ensures a sandboxed view of the document where the reviewer
    and only the matter.participants can interact with each other
    """
    def test_reviewer_already_a_reviewer_add_count_no_increment(self):
        self.assertEqual(self.revision.reviewdocument_set.all().count(), 2)
        self.revision.reviewers.add(self.reviewer)
        # the revision has 2 reviewers now
        self.assertEqual(self.revision.reviewdocument_set.all().count(), 2)
        # but the reviewer only has 1
        self.assertEqual(self.reviewer.reviewdocument_set.all().count(), 1) # has only 1

    def test_new_reviewer_add_count_increment(self):
        self.assertEqual(self.revision.reviewdocument_set.all().count(), 2)

        new_reviewer_monkey = mommy.make('auth.User', username='new_reviewer_monkey', email='new_reviewer_monkey@lawpal.com')
        self.revision.reviewers.add(new_reviewer_monkey)
        self.assertEqual(self.revision.reviewdocument_set.all().count(), 3)
        self.assertEqual(new_reviewer_monkey.reviewdocument_set.all().count(), 1)

        reviewdocument = new_reviewer_monkey.reviewdocument_set.all().first()

        auth_key = reviewdocument.get_user_auth(user=new_reviewer_monkey)
        self.assertTrue(auth_key is not None)

        auth_url = reviewdocument.get_absolute_url(user=new_reviewer_monkey)
        self.assertEqual(auth_url, ABSOLUTE_BASE_URL('/review/%s/%s/' % (reviewdocument.slug, urllib.quote(auth_key))))



class ReviewerAuthorisationTest(BaseDataProvider, TestCase):
    def test_authorise_user(self):
        EXPECTED_AUTH_USERS = self.BASE_EXPECTED_AUTH_USERS.copy()
        #
        # remove the current reviewer just for this test
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


class ReviewerPercentageCompleteTest(BaseDataProvider, TestCase):
    num_reviewers = 5
    test_reviewers = []

    def setUp(self):
        super(ReviewerPercentageCompleteTest, self).setUp()

        base_num_reviewdocuments = self.review_document.document.reviewdocument_set.all().count() - 1

        self.test_reviewers.append(self.reviewer)  # append the main reviewer added in SetUp

        for u_num in range(1, self.num_reviewers + 1):
            reviewer = mommy.make('auth.User', username='invited_reviewer_%d' % u_num, email='invited_reviewer_%d@lawpal.com' % u_num)
            self.review_document.document.reviewers.add(reviewer)
            self.test_reviewers.append(reviewer)

            # test that we increment the reviewdocument_set of the base document
            self.assertEqual(self.item.invited_document_reviews().count(), base_num_reviewdocuments + u_num)

    def test_percentage_complete_increments(self):
        num_complete = 0
        total_num_reviews = self.item.invited_document_reviews().count()

        self.assertEqual(total_num_reviews, 6) # 6 not 5 because of the primary documentreview which is ignored
        self.assertEqual(self.item.review_percentage_complete, 0)
        self.assertEqual(self.item.percent_formatted(self.item.review_percentage_complete), '0%')

        for c, user in enumerate(self.test_reviewers):
            reviewdocument = self.item.invited_document_reviews().get(reviewers__in=[user])
            reviewdocument.is_complete = True
            reviewdocument.save(update_fields=['is_complete'])

            # test that we are incrementing the number of reviewdocuments for each user
            # test the built in api method
            self.assertEqual(self.item.invited_document_reviews().filter(is_complete=True).count(), num_complete + (c+1))
            # affirm that the built in matches the manual calc below
            self.assertEqual(self.review_document.document.reviewdocument_set.filter(is_complete=True).count(), num_complete + (c+1))

            # test % increment
            num_reviewdocuments_complete = self.item.invited_document_reviews().filter(is_complete=True).count()
            review_percentage_complete = float(num_reviewdocuments_complete) / float(total_num_reviews)
            review_percentage_complete = round(review_percentage_complete * 100, 0)

            self.assertEqual(self.item.review_percentage_complete, review_percentage_complete)

        self.assertEqual(self.item.review_percentage_complete, 100.0)
        self.assertEqual(self.item.percent_formatted(self.item.review_percentage_complete), '100%')
        # we have recorded the action
        self.assertEqual(Action.objects.all().first().__unicode__(), u'Lawyër Tëst completed all reviews Test Item No. 1 on Lawpal (test) 0 minutes ago')
        Action.objects.all().delete()

        # Test Decrement
        for c, user in enumerate(self.test_reviewers):
            reviewdocument = self.item.invited_document_reviews().get(reviewers__in=[user])
            reviewdocument.is_complete = False
            reviewdocument.save(update_fields=['is_complete'])

            # test that we are incrementing the number of reviewdocuments for each user
            # test the built in api method
            self.assertEqual(self.item.invited_document_reviews().filter(is_complete=True).count(), total_num_reviews - (c+1))
            # affirm that the built in matches the manual calc below
            self.assertEqual(self.review_document.document.reviewdocument_set.filter(is_complete=True).count(), total_num_reviews - (c+1))

            # test % increment
            num_reviewdocuments_complete = self.item.invited_document_reviews().filter(is_complete=True).count()
            review_percentage_complete = float(num_reviewdocuments_complete) / float(total_num_reviews)
            review_percentage_complete = round(review_percentage_complete * 100, 0)

            self.assertEqual(self.item.review_percentage_complete, review_percentage_complete)

        self.assertEqual(self.item.review_percentage_complete, 0.0)
        self.assertEqual(self.item.percent_formatted(self.item.review_percentage_complete), '0%')
        self.assertEqual(Action.objects.all().count(), 0)

        # Test new Revision added should set count to null
        previous_revision = self.item.latest_revision
        # create a new one
        new_revision = mommy.make('attachment.Revision', item=self.item)
        self.assertTrue(self.item.latest_revision is new_revision)
        self.assertTrue(new_revision.is_current)
        self.assertEqual(self.item.review_percentage_complete, None)
        self.assertEqual(self.item.percent_formatted(self.item.review_percentage_complete), None)



"""
View tests
1. if user is logged in, check they are a participant or the expected user according to the auth_key
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
    def test_anonymous_is_logged_in_as_expected_reviewer(self):
        self.assertEqual(self.review_document.date_last_viewed, None)

        with mock.patch('datetime.datetime', PatchedDateTime):
            resp = self.client.get(self.review_document.get_absolute_url(self.reviewer), follow=True)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['user'], self.reviewer)
        #
        # And date updated
        #
        self.review_document = self.review_document.__class__.objects.get(pk=self.review_document.pk)  # refresh
        self.assertEqual(self.review_document.date_last_viewed.year, 1970)
        self.assertEqual(self.review_document.date_last_viewed.month, 1)
        self.assertEqual(self.review_document.date_last_viewed.day, 1)
        self.assertEqual(self.review_document.date_last_viewed.hour, 0)
        self.assertEqual(self.review_document.date_last_viewed.minute, 0)
        self.assertEqual(self.review_document.date_last_viewed.second, 0)

    @mock_http_requests
    def test_logged_in_invalid_user(self):
        """
        if we are logged in as someone with no connection to the review or matter then it should
        throw a 403 foridden
        """
        self.client.login(username=self.invalid_reviewer.username, password=self.password)

        resp = self.client.get(self.review_document.get_absolute_url(self.reviewer), follow=True)

        self.assertEqual(resp.status_code, 403)  # forbidden

    @mock_http_requests
    def test_reviewer_viewing_revision_updates_last_viewed(self):
        self.assertEqual(self.review_document.date_last_viewed, None)

        with mock.patch('datetime.datetime', PatchedDateTime):
            resp = self.client.get(self.review_document.get_absolute_url(self.reviewer), follow=True)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['user'], self.reviewer)

        self.review_document = self.review_document.__class__.objects.get(pk=self.review_document.pk)  # refresh
        self.assertEqual(self.review_document.date_last_viewed.year, 1970)
        self.assertEqual(self.review_document.date_last_viewed.month, 1)
        self.assertEqual(self.review_document.date_last_viewed.day, 1)
        self.assertEqual(self.review_document.date_last_viewed.hour, 0)
        self.assertEqual(self.review_document.date_last_viewed.minute, 0)
        self.assertEqual(self.review_document.date_last_viewed.second, 0)

        #
        # Test the api endpoint returns the expected date_last_viewed
        #
        self.client.login(username=self.lawyer.username, password=self.password)
        resp = self.client.get(reverse('reviewdocument-detail', kwargs={'pk': self.review_document.pk}))
        self.assertEqual(resp.status_code, 200)

        json_resp = json.loads(resp.content)
        self.assertEqual(json_resp.get('date_last_viewed'), u'1970-01-01T00:00:00.113Z')

    @mock_http_requests
    def test_lawyer_viewing_revision_updates_nothing(self):
        self.assertEqual(self.review_document.date_last_viewed, None)

        self.client.login(username=self.lawyer.username, password=self.password)

        resp = self.client.get(self.review_document.get_absolute_url(self.lawyer), follow=True)
        self.assertEqual(resp.context['user'], self.lawyer)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(ReviewDocument.objects.get(pk=self.review_document.pk).date_last_viewed, None)


"""
test primary_reviewdocument()-function for Revision to get the revision that JUST belongs to the participants
"""
class PrimaryReviewDocumentTest(BaseDataProvider, TestCase):
    def test_primary_reviewdocument(self):
        reviewer_reviewdocument = self.revision.reviewdocument_set.get(reviewers=self.reviewer)
        self.assertNotEqual(reviewer_reviewdocument, self.revision.primary_reviewdocument)
