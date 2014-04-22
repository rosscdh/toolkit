# -*- coding: utf-8 -*-
from django.core import mail
from django.core.urlresolvers import reverse

from toolkit.apps.workspace.models import InviteKey
from toolkit.casper.workflow_case import PyQueryMixin
from toolkit.apps.default.templatetags.toolkit_tags import ABSOLUTE_BASE_URL

from . import BaseEndpointTest
from ...serializers import ClientSerializer

from model_mommy import mommy

import json

class BaseReviewEndpointTest(object):
    @property
    def endpoint(self):
        return reverse('item_revision_remind_reviewers', kwargs={'matter_slug': self.matter.slug, 'item_slug': self.item.slug})

    def test_endpoint_name(self):
        self.assertEqual(self.endpoint, '/api/v1/matters/%s/items/%s/revision/reviewers/remind' % (self.matter.slug, self.item.slug))


class RemindReviewersTest(PyQueryMixin, BaseReviewEndpointTest, BaseEndpointTest):
    """
    /matters/:matter_slug/items/:item_slug/revision/reviewers/remind (POST)
        Send reminder emails to any outstanding reviewers
    """
    def setUp(self):
        super(RemindReviewersTest, self).setUp()
        # setup the items for testing
        self.item = mommy.make('item.Item', matter=self.matter, name='Test Item for Review Reminder', category=None)
        self.revision = mommy.make('attachment.Revision', executed_file=None, slug=None, item=self.item, uploaded_by=self.lawyer)
        self.reviewer = mommy.make('auth.User', username='authorised-reviewer', first_name='Reviewer', last_name='Number 1', email='reviewer+1@lawpal.com')
        self.revision.reviewers.add(self.reviewer)

    def test_lawyer_get(self):
        self.client.login(username=self.lawyer.username, password=self.password)
        resp = self.client.get(self.endpoint)
        self.assertEqual(resp.status_code, 405) # forbidden

    def test_lawyer_post(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        resp = self.client.post(self.endpoint, {}, content_type='application/json')

        self.assertEqual(resp.status_code, 202)  # accepted
        json_data = json.loads(resp.content)

        self.assertEqual(json_data['detail'], 'Sent reminder email to the following users')
        self.assertEqual(type(json_data['results']), list)
        self.assertEqual(len(json_data['results']), 1)

        outbox = mail.outbox
        self.assertEqual(len(outbox), 1)

        email = outbox[0]
        self.assertEqual(email.subject, '[REMINDER] Please review this document')
        self.assertEqual(email.recipients(), [self.reviewer.email])

        pq = self.pq(email.body)

        invite_key = InviteKey.objects.get(matter=self.matter, invited_user=self.reviewer)
        review_document = self.item.latest_revision.reviewdocument_set.filter(reviewers__in=[self.reviewer]).first()

        expected_action_url = ABSOLUTE_BASE_URL(invite_key.get_absolute_url())

        self.assertEqual(pq('a')[0].attrib.get('href'), expected_action_url)
        self.assertEqual(invite_key.next, reverse('request:list'))


    def test_lawyer_patch(self):
        self.client.login(username=self.lawyer.username, password=self.password)
        resp = self.client.patch(self.endpoint, json.dumps({}), content_type='application/json')
        self.assertEqual(resp.status_code, 405)  # not allowed

    def test_lawyer_delete(self):
        self.client.login(username=self.lawyer.username, password=self.password)
        resp = self.client.delete(self.endpoint, json.dumps({}), content_type='application/json')
        self.assertEqual(resp.status_code, 405)  # not allowed

    def test_customer_get(self):
        self.client.login(username=self.user.username, password=self.password)
        resp = self.client.get(self.endpoint)
        self.assertEqual(resp.status_code, 403) # forbidden

    def test_customer_post(self):
        self.client.login(username=self.user.username, password=self.password)
        resp = self.client.post(self.endpoint, {}, content_type='application/json')
        self.assertEqual(resp.status_code, 403)  # forbidden

    def test_customer_patch(self):
        self.client.login(username=self.user.username, password=self.password)
        resp = self.client.patch(self.endpoint, json.dumps({}), content_type='application/json')
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


class RemindOnlyReviewersWhoHaveNotCompletedTheirReviewTest(BaseReviewEndpointTest, BaseEndpointTest):
    def setUp(self):
        super(RemindOnlyReviewersWhoHaveNotCompletedTheirReviewTest, self).setUp()
        # setup the items for testing
        self.item = mommy.make('item.Item', matter=self.matter, name='Test Item for Review Reminder', category=None)
        self.revision = mommy.make('attachment.Revision', executed_file=None, slug=None, item=self.item, uploaded_by=self.lawyer)

        self.reviewer = mommy.make('auth.User', username='authorised-reviewer', first_name='Reviewer', last_name='Number 1', email='reviewer+1@lawpal.com')
        self.revision.reviewers.add(self.reviewer)

        self.reviewer2 = mommy.make('auth.User', username='authorised-reviewer-2', first_name='Reviewer', last_name='Number 2', email='reviewer+1@lawpal.com')
        self.revision.reviewers.add(self.reviewer2)

        self.reviewer3 = mommy.make('auth.User', username='authorised-reviewer-3', first_name='Reviewer', last_name='Number 3', email='reviewer+3@lawpal.com')
        self.revision.reviewers.add(self.reviewer3)

        # mark one of them as complete
        review_document = self.item.invited_document_reviews().first()
        review_document.is_complete = True
        review_document.save(update_fields=['is_complete'])

    def test_only_un_reviewed_emails_are_sent(self):
        self.client.login(username=self.lawyer.username, password=self.password)

        resp = self.client.post(self.endpoint, {}, content_type='application/json')

        self.assertEqual(resp.status_code, 202)  # accepted
        json_data = json.loads(resp.content)

        outbox = mail.outbox
        self.assertEqual(len(outbox), 2)

        email = outbox[0]
        self.assertEqual(email.subject, '[REMINDER] Please review this document')
        self.assertEqual(email.recipients(), [self.reviewer.email])

        email = outbox[1]
        self.assertEqual(email.subject, '[REMINDER] Please review this document')
        self.assertEqual(email.recipients(), [self.reviewer2.email])